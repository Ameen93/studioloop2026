"""Webhook management endpoints (Epic 11, Stories 11.9 & 11.10).

Implements:
- Story 11.9: Webhook Event System (delivery/retry)
- Story 11.10: Webhook Management (CRUD for gym webhook endpoints)

Webhook endpoints are gym-scoped and require owner role.
Events are signed with HMAC-SHA256 using the endpoint's secret key.
"""

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import SQLModel, col, select

from app.api.deps import RequireOwner, SessionDep, StaffGymDep
from app.models.admin import (
    WebhookDelivery,
    WebhookDeliveryPublic,
    WebhookDeliveryStatus,
    WebhookEndpoint,
    WebhookEndpointCreate,
    WebhookEndpointPublic,
    WebhookEndpointUpdate,
)

router = APIRouter(prefix="/gyms/{gym_id}/webhooks", tags=["webhooks"])


# =============================================================================
# Helpers
# =============================================================================


def _generate_webhook_secret() -> str:
    """Generate a random HMAC-SHA256 signing secret."""
    return f"whsec_{secrets.token_hex(32)}"


def _sign_payload(secret: str, payload: dict[str, Any]) -> str:
    """Sign a webhook payload with HMAC-SHA256."""
    payload_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def _mask_secret(secret: str) -> str:
    """Return last 4 characters of the secret for display."""
    if len(secret) <= 4:
        return secret
    return secret[-4:]


def _serialize_endpoint(endpoint: WebhookEndpoint) -> WebhookEndpointPublic:
    """Convert a WebhookEndpoint to its public schema."""
    return WebhookEndpointPublic(
        id=endpoint.id,
        gym_id=endpoint.gym_id,
        url=endpoint.url,
        events=endpoint.events,
        is_active=endpoint.is_active,
        secret_last4=_mask_secret(endpoint.secret),
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
    )


# =============================================================================
# Response schemas
# =============================================================================


class WebhookEndpointCreatedResponse(SQLModel):
    """Response after creating a webhook endpoint. Includes full secret (only time it's shown)."""

    endpoint: WebhookEndpointPublic
    secret: str


class WebhookEndpointListResponse(SQLModel):
    """Paginated webhook endpoint list."""

    items: list[WebhookEndpointPublic]
    total: int


class WebhookDeliveryListResponse(SQLModel):
    """Paginated webhook delivery list."""

    items: list[WebhookDeliveryPublic]
    total: int
    skip: int
    limit: int


class WebhookTestResponse(SQLModel):
    """Response after sending a test webhook event."""

    delivery_id: UUID
    status: str
    response_status_code: int | None = None
    message: str


# =============================================================================
# Story 11.10: Webhook Management CRUD
# =============================================================================


@router.post(
    "",
    response_model=WebhookEndpointCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireOwner],
)
def create_webhook_endpoint(
    session: SessionDep,
    current_staff: StaffGymDep,
    payload: WebhookEndpointCreate,
) -> WebhookEndpointCreatedResponse:
    """Create a new webhook endpoint for the gym.

    Returns the full signing secret - this is the only time
    the full secret is visible. Store it securely.
    """
    secret = _generate_webhook_secret()

    endpoint = WebhookEndpoint(
        gym_id=current_staff.gym_id,
        url=payload.url,
        events=payload.events,
        is_active=True,
        secret=secret,
    )
    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)

    return WebhookEndpointCreatedResponse(
        endpoint=_serialize_endpoint(endpoint),
        secret=secret,
    )


@router.get(
    "",
    response_model=WebhookEndpointListResponse,
    dependencies=[RequireOwner],
)
def list_webhook_endpoints(
    session: SessionDep,
    current_staff: StaffGymDep,
) -> WebhookEndpointListResponse:
    """List all webhook endpoints for the gym."""
    stmt = select(WebhookEndpoint).where(
        WebhookEndpoint.gym_id == current_staff.gym_id,
    )

    total = session.exec(select(func.count()).select_from(stmt.subquery())).one()

    endpoints = session.exec(stmt.order_by(col(WebhookEndpoint.created_at).desc())).all()

    return WebhookEndpointListResponse(
        items=[_serialize_endpoint(ep) for ep in endpoints],
        total=total,
    )


@router.get(
    "/{webhook_id}",
    response_model=WebhookEndpointPublic,
    dependencies=[RequireOwner],
)
def get_webhook_endpoint(
    session: SessionDep,
    current_staff: StaffGymDep,
    webhook_id: UUID,
) -> WebhookEndpointPublic:
    """Get a specific webhook endpoint."""
    endpoint = session.exec(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.gym_id == current_staff.gym_id,
        )
    ).first()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WEBHOOK_NOT_FOUND",
                "message": "Webhook endpoint not found",
                "details": {},
            },
        )

    return _serialize_endpoint(endpoint)


@router.patch(
    "/{webhook_id}",
    response_model=WebhookEndpointPublic,
    dependencies=[RequireOwner],
)
def update_webhook_endpoint(
    session: SessionDep,
    current_staff: StaffGymDep,
    webhook_id: UUID,
    payload: WebhookEndpointUpdate,
) -> WebhookEndpointPublic:
    """Update a webhook endpoint's URL, events, or active status."""
    endpoint = session.exec(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.gym_id == current_staff.gym_id,
        )
    ).first()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WEBHOOK_NOT_FOUND",
                "message": "Webhook endpoint not found",
                "details": {},
            },
        )

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(endpoint, key, value)

    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)

    return _serialize_endpoint(endpoint)


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireOwner],
)
def delete_webhook_endpoint(
    session: SessionDep,
    current_staff: StaffGymDep,
    webhook_id: UUID,
) -> None:
    """Delete a webhook endpoint and all its delivery records."""
    endpoint = session.exec(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.gym_id == current_staff.gym_id,
        )
    ).first()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WEBHOOK_NOT_FOUND",
                "message": "Webhook endpoint not found",
                "details": {},
            },
        )

    # Delete associated deliveries first
    deliveries = session.exec(
        select(WebhookDelivery).where(
            WebhookDelivery.webhook_endpoint_id == webhook_id,
        )
    ).all()
    for delivery in deliveries:
        session.delete(delivery)

    session.delete(endpoint)
    session.commit()


# =============================================================================
# Story 11.9: Webhook Event System
# =============================================================================


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResponse,
    dependencies=[RequireOwner],
)
def test_webhook(
    session: SessionDep,
    current_staff: StaffGymDep,
    webhook_id: UUID,
) -> WebhookTestResponse:
    """Send a test event to a webhook endpoint.

    Delivers a 'test.ping' event synchronously and returns
    the delivery result immediately.
    """
    endpoint = session.exec(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.gym_id == current_staff.gym_id,
        )
    ).first()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WEBHOOK_NOT_FOUND",
                "message": "Webhook endpoint not found",
                "details": {},
            },
        )

    # Build test payload
    test_payload: dict[str, Any] = {
        "event": "test.ping",
        "gym_id": str(current_staff.gym_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"message": "This is a test webhook event from StudioLoop"},
    }

    # Sign payload
    signature = _sign_payload(endpoint.secret, test_payload)

    # Create delivery record
    delivery = WebhookDelivery(
        webhook_endpoint_id=endpoint.id,
        event_type="test.ping",
        payload=test_payload,
        status=WebhookDeliveryStatus.PENDING,
        attempts=1,
        last_attempt_at=datetime.now(timezone.utc),
    )

    # Attempt delivery
    response_status_code: int | None = None
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                endpoint.url,
                json=test_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-StudioLoop-Signature": signature,
                    "X-StudioLoop-Event": "test.ping",
                },
            )
            response_status_code = response.status_code
            delivery.response_status_code = response_status_code
            delivery.response_body = response.text[:2000] if response.text else None

            if 200 <= response.status_code < 300:
                delivery.status = WebhookDeliveryStatus.DELIVERED
            else:
                delivery.status = WebhookDeliveryStatus.FAILED
    except Exception as exc:
        delivery.status = WebhookDeliveryStatus.FAILED
        delivery.response_body = str(exc)[:2000]

    session.add(delivery)
    session.commit()
    session.refresh(delivery)

    status_msg = (
        "Test event delivered successfully"
        if delivery.status == WebhookDeliveryStatus.DELIVERED
        else "Test event delivery failed"
    )

    return WebhookTestResponse(
        delivery_id=delivery.id,
        status=delivery.status.value,
        response_status_code=response_status_code,
        message=status_msg,
    )


@router.get(
    "/{webhook_id}/deliveries",
    response_model=WebhookDeliveryListResponse,
    dependencies=[RequireOwner],
)
def list_webhook_deliveries(
    session: SessionDep,
    current_staff: StaffGymDep,
    webhook_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status_filter: WebhookDeliveryStatus | None = Query(default=None, alias="status"),
) -> WebhookDeliveryListResponse:
    """List delivery logs for a webhook endpoint."""
    # Verify endpoint belongs to gym
    endpoint = session.exec(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.gym_id == current_staff.gym_id,
        )
    ).first()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WEBHOOK_NOT_FOUND",
                "message": "Webhook endpoint not found",
                "details": {},
            },
        )

    stmt = select(WebhookDelivery).where(
        WebhookDelivery.webhook_endpoint_id == webhook_id,
    )

    if status_filter is not None:
        stmt = stmt.where(WebhookDelivery.status == status_filter)

    total = session.exec(select(func.count()).select_from(stmt.subquery())).one()

    deliveries = session.exec(
        stmt.order_by(col(WebhookDelivery.created_at).desc()).offset(skip).limit(limit)
    ).all()

    items = [
        WebhookDeliveryPublic(
            id=d.id,
            webhook_endpoint_id=d.webhook_endpoint_id,
            event_type=d.event_type,
            status=d.status,
            attempts=d.attempts,
            last_attempt_at=d.last_attempt_at,
            response_status_code=d.response_status_code,
            next_retry_at=d.next_retry_at,
            created_at=d.created_at,
        )
        for d in deliveries
    ]

    return WebhookDeliveryListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
