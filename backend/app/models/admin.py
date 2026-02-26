"""Admin & platform administration models for Epic 11.

This module defines models for:
- Complaint: Consumer complaint handling (Story 11.3)
- CreditLog: Account credit issuance tracking (Story 11.4)
- AuditLog: Admin action audit trail (Story 11.6)
- WebhookEndpoint: Gym webhook endpoint registration (Story 11.10)
- WebhookDelivery: Webhook delivery tracking and retry (Story 11.9)
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.models.base import BaseModel, GymScopedModel

# =============================================================================
# Enums
# =============================================================================


class ComplaintStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    CLOSED = "closed"


class WebhookDeliveryStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"


# =============================================================================
# Complaint (Story 11.3)
# =============================================================================


class ComplaintBase(SQLModel):
    """Shared fields for Complaint schemas."""

    consumer_id: UUID = Field(
        foreign_key="consumers.id",
        nullable=False,
        index=True,
        description="Consumer who filed the complaint",
    )
    gym_id: UUID | None = Field(
        default=None,
        foreign_key="gyms.id",
        nullable=True,
        index=True,
        description="Gym the complaint relates to (optional)",
    )
    description: str = Field(
        min_length=1,
        max_length=5000,
        description="Complaint description text",
    )


class Complaint(BaseModel, ComplaintBase, table=True):
    """Consumer complaint record.

    Platform-scoped (not gym-scoped) since complaints can span
    multiple gyms or be platform-level issues.
    """

    __tablename__ = "complaints"

    status: ComplaintStatus = Field(
        default=ComplaintStatus.OPEN,
        max_length=20,
        index=True,
        description="Current complaint status",
    )
    assigned_to: UUID | None = Field(
        default=None,
        foreign_key="user.id",
        nullable=True,
        index=True,
        description="Admin user assigned to handle this complaint",
    )
    notes: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description="Chronological list of admin notes [{admin_id, text, timestamp}]",
    )
    resolution: str | None = Field(
        default=None,
        max_length=5000,
        description="Resolution description when complaint is closed",
    )


class ComplaintCreate(SQLModel):
    """Schema for creating a new complaint."""

    consumer_id: UUID
    gym_id: UUID | None = None
    description: str = Field(min_length=1, max_length=5000)


class ComplaintUpdate(SQLModel):
    """Schema for updating a complaint - all fields optional."""

    status: ComplaintStatus | None = None
    assigned_to: UUID | None = None
    resolution: str | None = Field(default=None, max_length=5000)
    note: str | None = Field(
        default=None,
        max_length=2000,
        description="New note to append to the notes list",
    )


class ComplaintPublic(SQLModel):
    """Schema for complaint in API responses."""

    id: UUID
    consumer_id: UUID
    gym_id: UUID | None = None
    description: str
    status: ComplaintStatus
    assigned_to: UUID | None = None
    notes: list[dict[str, Any]] = []
    resolution: str | None = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# CreditLog (Story 11.4)
# =============================================================================


class CreditLogBase(SQLModel):
    """Shared fields for CreditLog schemas."""

    consumer_id: UUID = Field(
        foreign_key="consumers.id",
        nullable=False,
        index=True,
        description="Consumer receiving the credit",
    )
    admin_user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Admin user who issued the credit",
    )
    amount: int = Field(
        ge=1,
        description="Number of class credits to issue",
    )
    reason: str = Field(
        min_length=1,
        max_length=1000,
        description="Reason for issuing credits",
    )
    marketplace_subscription_id: UUID | None = Field(
        default=None,
        foreign_key="marketplace_subscriptions.id",
        nullable=True,
        index=True,
        description="Marketplace subscription to credit (if applicable)",
    )


class CreditLog(BaseModel, CreditLogBase, table=True):
    """Record of admin-issued credits to a consumer's marketplace subscription."""

    __tablename__ = "credit_logs"


class CreditLogCreate(SQLModel):
    """Schema for creating a credit issuance."""

    amount: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=1000)
    marketplace_subscription_id: UUID | None = None


class CreditLogPublic(SQLModel):
    """Schema for credit log in API responses."""

    id: UUID
    consumer_id: UUID
    admin_user_id: UUID
    amount: int
    reason: str
    marketplace_subscription_id: UUID | None = None
    created_at: datetime


# =============================================================================
# AuditLog (Story 11.6)
# =============================================================================


class AuditLogBase(SQLModel):
    """Shared fields for AuditLog schemas."""

    admin_user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Admin user who performed the action",
    )
    action: str = Field(
        max_length=100,
        description="Action performed (e.g., 'approve_gym', 'issue_credit')",
    )
    resource_type: str = Field(
        max_length=100,
        description="Type of resource acted upon (e.g., 'gym', 'complaint')",
    )
    resource_id: UUID | None = Field(
        default=None,
        nullable=True,
        description="ID of the resource acted upon",
    )
    gym_id: UUID | None = Field(
        default=None,
        foreign_key="gyms.id",
        nullable=True,
        index=True,
        description="Gym context for the action (if applicable)",
    )


class AuditLog(BaseModel, AuditLogBase, table=True):
    """Audit trail for admin actions.

    Platform-scoped. Records every admin action for compliance
    and accountability purposes.
    """

    __tablename__ = "audit_logs"

    details: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Additional details about the action",
    )


class AuditLogCreate(SQLModel):
    """Internal schema for creating audit log entries."""

    admin_user_id: UUID
    action: str = Field(max_length=100)
    resource_type: str = Field(max_length=100)
    resource_id: UUID | None = None
    gym_id: UUID | None = None
    details: dict[str, Any] = {}


class AuditLogPublic(SQLModel):
    """Schema for audit log in API responses."""

    id: UUID
    admin_user_id: UUID
    action: str
    resource_type: str
    resource_id: UUID | None = None
    gym_id: UUID | None = None
    details: dict[str, Any] = {}
    created_at: datetime


# =============================================================================
# WebhookEndpoint (Story 11.10)
# =============================================================================


class WebhookEndpointBase(SQLModel):
    """Shared fields for WebhookEndpoint schemas."""

    url: str = Field(
        max_length=2048,
        description="URL to deliver webhook events to",
    )
    events: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description="List of event types to subscribe to (e.g., ['booking.created', 'booking.cancelled'])",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this webhook endpoint is active",
    )


class WebhookEndpoint(GymScopedModel, WebhookEndpointBase, table=True):
    """Gym-scoped webhook endpoint registration.

    Each gym can register multiple webhook endpoints to receive
    event notifications. Events are signed with HMAC-SHA256 using
    the endpoint's secret key.
    """

    __tablename__ = "webhook_endpoints"

    secret: str = Field(
        max_length=255,
        description="HMAC-SHA256 signing key for webhook payloads",
    )


class WebhookEndpointCreate(SQLModel):
    """Schema for creating a webhook endpoint."""

    url: str = Field(max_length=2048)
    events: list[str] = Field(default_factory=list)


class WebhookEndpointUpdate(SQLModel):
    """Schema for updating a webhook endpoint - all fields optional."""

    url: str | None = Field(default=None, max_length=2048)
    events: list[str] | None = None
    is_active: bool | None = None


class WebhookEndpointPublic(SQLModel):
    """Schema for webhook endpoint in API responses.

    Note: secret is intentionally excluded from public response.
    Only a masked version is returned.
    """

    id: UUID
    gym_id: UUID
    url: str
    events: list[str] = []
    is_active: bool
    secret_last4: str = Field(description="Last 4 characters of signing secret")
    created_at: datetime
    updated_at: datetime


# =============================================================================
# WebhookDelivery (Story 11.9)
# =============================================================================


class WebhookDeliveryBase(SQLModel):
    """Shared fields for WebhookDelivery schemas."""

    webhook_endpoint_id: UUID = Field(
        foreign_key="webhook_endpoints.id",
        nullable=False,
        index=True,
        description="Target webhook endpoint",
    )
    event_type: str = Field(
        max_length=100,
        description="Event type (e.g., 'booking.created')",
    )


class WebhookDelivery(BaseModel, WebhookDeliveryBase, table=True):
    """Webhook delivery attempt record.

    Platform-scoped. Tracks each webhook delivery attempt including
    retry logic with exponential backoff.
    """

    __tablename__ = "webhook_deliveries"

    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="JSON payload delivered to the webhook endpoint",
    )
    status: WebhookDeliveryStatus = Field(
        default=WebhookDeliveryStatus.PENDING,
        max_length=20,
        index=True,
        description="Delivery status",
    )
    attempts: int = Field(
        default=0,
        ge=0,
        description="Number of delivery attempts made",
    )
    last_attempt_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp of the last delivery attempt",
    )
    response_status_code: int | None = Field(
        default=None,
        nullable=True,
        description="HTTP status code from last delivery attempt",
    )
    response_body: str | None = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="Truncated response body from last delivery attempt",
    )
    next_retry_at: datetime | None = Field(
        default=None,
        nullable=True,
        index=True,
        description="Scheduled time for next retry attempt",
    )


class WebhookDeliveryCreate(SQLModel):
    """Internal schema for creating webhook delivery records."""

    webhook_endpoint_id: UUID
    event_type: str = Field(max_length=100)
    payload: dict[str, Any] = {}


class WebhookDeliveryPublic(SQLModel):
    """Schema for webhook delivery in API responses."""

    id: UUID
    webhook_endpoint_id: UUID
    event_type: str
    status: WebhookDeliveryStatus
    attempts: int
    last_attempt_at: datetime | None = None
    response_status_code: int | None = None
    next_retry_at: datetime | None = None
    created_at: datetime
