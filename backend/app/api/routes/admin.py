"""Platform administration endpoints (Epic 11).

Implements:
- Story 11.1: Gym Application Review (approve/reject)
- Story 11.2: Platform Gym Management (list, search, suspend, reactivate)
- Story 11.3: Consumer Complaint Handling (CRUD + status management)
- Story 11.4: Account Credit Issuance
- Story 11.5: Platform Health Monitoring
- Story 11.6: Gym-Level Data Access for Support (with audit logging)

All endpoints require superuser authentication via CurrentUser.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import SQLModel, col, select

from app.api.deps import CurrentUser, SessionDep
from app.models.admin import (
    AuditLog,
    AuditLogPublic,
    Complaint,
    ComplaintCreate,
    ComplaintPublic,
    ComplaintStatus,
    ComplaintUpdate,
    CreditLog,
    CreditLogCreate,
    CreditLogPublic,
)
from app.models.booking import Booking
from app.models.consumer import Consumer
from app.models.gym import Gym, GymSubscriptionTier
from app.models.gym_membership import GymMembership
from app.models.marketplace_subscription import MarketplaceSubscription
from app.models.payment import Payment, PaymentStatus
from app.models.staff import Staff

router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# Helpers
# =============================================================================


def _require_superuser(current_user: CurrentUser) -> None:
    """Raise 403 if the current user is not a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Superuser access required",
                "details": {},
            },
        )


def _create_audit_log(
    session: SessionDep,
    admin_user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: UUID | None = None,
    gym_id: UUID | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """Create an audit log entry for an admin action."""
    audit_log = AuditLog(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        gym_id=gym_id,
        details=details or {},
    )
    session.add(audit_log)
    return audit_log


# =============================================================================
# Response schemas
# =============================================================================


class AdminGymListItem(SQLModel):
    """Gym summary for admin listing."""

    id: UUID
    name: str
    slug: str
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    province: str | None = None
    subscription_tier: GymSubscriptionTier
    is_marketplace_enabled: bool
    is_active: bool
    created_at: datetime


class AdminGymListResponse(SQLModel):
    """Paginated gym list for admin."""

    items: list[AdminGymListItem]
    total: int
    skip: int
    limit: int


class AdminGymActionResponse(SQLModel):
    """Response for gym approve/reject/suspend/reactivate actions."""

    gym_id: UUID
    action: str
    message: str


class ComplaintListResponse(SQLModel):
    """Paginated complaint list."""

    items: list[ComplaintPublic]
    total: int
    skip: int
    limit: int


class CreditIssueResponse(SQLModel):
    """Response after issuing credits."""

    credit_log: CreditLogPublic
    new_classes_remaining: int


class PlatformHealthResponse(SQLModel):
    """Platform health statistics dashboard."""

    total_gyms: int
    active_gyms: int
    inactive_gyms: int
    total_consumers: int
    total_staff: int
    total_bookings: int
    active_marketplace_subscriptions: int
    open_complaints: int
    total_payments_completed: int
    timestamp: datetime


class GymDataMembersItem(SQLModel):
    """Member info for admin gym data access."""

    consumer_id: UUID
    email: str | None = None
    first_name: str
    last_name: str
    membership_status: str | None = None


class GymDataBookingItem(SQLModel):
    """Booking info for admin gym data access."""

    id: UUID
    consumer_id: UUID
    session_id: UUID
    status: str
    created_at: datetime


class GymDataPaymentItem(SQLModel):
    """Payment info for admin gym data access."""

    id: UUID
    consumer_id: UUID
    amount_cents: int
    status: str
    payment_type: str
    created_at: datetime


class GymDataResponse(SQLModel):
    """Aggregated gym data for admin support access."""

    gym_id: UUID
    gym_name: str
    members: list[GymDataMembersItem]
    recent_bookings: list[GymDataBookingItem]
    recent_payments: list[GymDataPaymentItem]
    total_members: int
    total_bookings: int
    total_revenue_cents: int


class AuditLogListResponse(SQLModel):
    """Paginated audit log list."""

    items: list[AuditLogPublic]
    total: int
    skip: int
    limit: int


# =============================================================================
# Story 11.1 & 11.2: Gym Application Review & Platform Gym Management
# =============================================================================


@router.get("/gyms", response_model=AdminGymListResponse)
def list_gyms(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    search: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
    subscription_tier: GymSubscriptionTier | None = Query(default=None),
    is_marketplace_enabled: bool | None = Query(default=None),
) -> AdminGymListResponse:
    """List all gyms with search and filter capabilities.

    Supports filtering by active status, subscription tier,
    and marketplace participation. Search matches against
    gym name, slug, email, and city.
    """
    _require_superuser(current_user)

    stmt = select(Gym)

    if search:
        search_term = f"%{search}%"
        stmt = stmt.where(
            (col(Gym.name).ilike(search_term))
            | (col(Gym.slug).ilike(search_term))
            | (col(Gym.email).ilike(search_term))
            | (col(Gym.city).ilike(search_term))
        )

    if is_active is not None:
        stmt = stmt.where(Gym.is_active == is_active)

    if subscription_tier is not None:
        stmt = stmt.where(Gym.subscription_tier == subscription_tier)

    if is_marketplace_enabled is not None:
        stmt = stmt.where(Gym.is_marketplace_enabled == is_marketplace_enabled)

    # Count total matching
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.exec(count_stmt).one()

    # Fetch page
    gyms = session.exec(
        stmt.order_by(col(Gym.created_at).desc()).offset(skip).limit(limit)
    ).all()

    items = [
        AdminGymListItem(
            id=g.id,
            name=g.name,
            slug=g.slug,
            email=g.email,
            phone=g.phone,
            city=g.city,
            province=g.province,
            subscription_tier=g.subscription_tier,
            is_marketplace_enabled=g.is_marketplace_enabled,
            is_active=g.is_active,
            created_at=g.created_at,
        )
        for g in gyms
    ]

    return AdminGymListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/gyms/{gym_id}/approve", response_model=AdminGymActionResponse)
def approve_gym(
    session: SessionDep,
    current_user: CurrentUser,
    gym_id: UUID,
) -> AdminGymActionResponse:
    """Approve a gym application by setting is_active=True."""
    _require_superuser(current_user)

    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    if gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GYM_ALREADY_ACTIVE",
                "message": "Gym is already active/approved",
                "details": {},
            },
        )

    gym.is_active = True
    gym.deleted_at = None
    settings_data = dict(gym.settings or {})
    settings_data["approved_at"] = datetime.now(timezone.utc).isoformat()
    settings_data["approved_by"] = str(current_user.id)
    gym.settings = settings_data

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="approve_gym",
        resource_type="gym",
        resource_id=gym.id,
        gym_id=gym.id,
        details={"gym_name": gym.name},
    )

    session.add(gym)
    session.commit()

    return AdminGymActionResponse(
        gym_id=gym.id,
        action="approved",
        message=f"Gym '{gym.name}' has been approved and activated.",
    )


@router.post("/gyms/{gym_id}/reject", response_model=AdminGymActionResponse)
def reject_gym(
    session: SessionDep,
    current_user: CurrentUser,
    gym_id: UUID,
    reason: str = Query(max_length=1000),
) -> AdminGymActionResponse:
    """Reject a gym application with a reason."""
    _require_superuser(current_user)

    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    gym.is_active = False
    settings_data = dict(gym.settings or {})
    settings_data["rejected_at"] = datetime.now(timezone.utc).isoformat()
    settings_data["rejected_by"] = str(current_user.id)
    settings_data["rejection_reason"] = reason
    gym.settings = settings_data

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="reject_gym",
        resource_type="gym",
        resource_id=gym.id,
        gym_id=gym.id,
        details={"gym_name": gym.name, "reason": reason},
    )

    session.add(gym)
    session.commit()

    return AdminGymActionResponse(
        gym_id=gym.id,
        action="rejected",
        message=f"Gym '{gym.name}' has been rejected. Reason: {reason}",
    )


@router.post("/gyms/{gym_id}/suspend", response_model=AdminGymActionResponse)
def suspend_gym(
    session: SessionDep,
    current_user: CurrentUser,
    gym_id: UUID,
    reason: str = Query(max_length=1000),
) -> AdminGymActionResponse:
    """Suspend an active gym."""
    _require_superuser(current_user)

    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    if not gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GYM_ALREADY_INACTIVE",
                "message": "Gym is already suspended/inactive",
                "details": {},
            },
        )

    gym.is_active = False
    gym.deleted_at = datetime.now(timezone.utc)
    settings_data = dict(gym.settings or {})
    settings_data["suspended_at"] = datetime.now(timezone.utc).isoformat()
    settings_data["suspended_by"] = str(current_user.id)
    settings_data["suspension_reason"] = reason
    gym.settings = settings_data

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="suspend_gym",
        resource_type="gym",
        resource_id=gym.id,
        gym_id=gym.id,
        details={"gym_name": gym.name, "reason": reason},
    )

    session.add(gym)
    session.commit()

    return AdminGymActionResponse(
        gym_id=gym.id,
        action="suspended",
        message=f"Gym '{gym.name}' has been suspended. Reason: {reason}",
    )


@router.post("/gyms/{gym_id}/reactivate", response_model=AdminGymActionResponse)
def reactivate_gym(
    session: SessionDep,
    current_user: CurrentUser,
    gym_id: UUID,
) -> AdminGymActionResponse:
    """Reactivate a suspended gym."""
    _require_superuser(current_user)

    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    if gym.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GYM_ALREADY_ACTIVE",
                "message": "Gym is already active",
                "details": {},
            },
        )

    gym.is_active = True
    gym.deleted_at = None
    settings_data = dict(gym.settings or {})
    settings_data["reactivated_at"] = datetime.now(timezone.utc).isoformat()
    settings_data["reactivated_by"] = str(current_user.id)
    # Clear suspension reason
    settings_data.pop("suspension_reason", None)
    settings_data.pop("suspended_at", None)
    settings_data.pop("suspended_by", None)
    gym.settings = settings_data

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="reactivate_gym",
        resource_type="gym",
        resource_id=gym.id,
        gym_id=gym.id,
        details={"gym_name": gym.name},
    )

    session.add(gym)
    session.commit()

    return AdminGymActionResponse(
        gym_id=gym.id,
        action="reactivated",
        message=f"Gym '{gym.name}' has been reactivated.",
    )


# =============================================================================
# Story 11.3: Consumer Complaint Handling
# =============================================================================


@router.get("/complaints", response_model=ComplaintListResponse)
def list_complaints(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status_filter: ComplaintStatus | None = Query(default=None, alias="status"),
    consumer_id: UUID | None = Query(default=None),
    gym_id: UUID | None = Query(default=None),
    assigned_to: UUID | None = Query(default=None),
) -> ComplaintListResponse:
    """List complaints with optional filters."""
    _require_superuser(current_user)

    stmt = select(Complaint)

    if status_filter is not None:
        stmt = stmt.where(Complaint.status == status_filter)
    if consumer_id is not None:
        stmt = stmt.where(Complaint.consumer_id == consumer_id)
    if gym_id is not None:
        stmt = stmt.where(Complaint.gym_id == gym_id)
    if assigned_to is not None:
        stmt = stmt.where(Complaint.assigned_to == assigned_to)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.exec(count_stmt).one()

    complaints = session.exec(
        stmt.order_by(col(Complaint.created_at).desc()).offset(skip).limit(limit)
    ).all()

    items = [
        ComplaintPublic(
            id=c.id,
            consumer_id=c.consumer_id,
            gym_id=c.gym_id,
            description=c.description,
            status=c.status,
            assigned_to=c.assigned_to,
            notes=c.notes,
            resolution=c.resolution,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in complaints
    ]

    return ComplaintListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/complaints",
    response_model=ComplaintPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_complaint(
    session: SessionDep,
    current_user: CurrentUser,
    payload: ComplaintCreate,
) -> ComplaintPublic:
    """Create a new complaint on behalf of a consumer."""
    _require_superuser(current_user)

    # Validate consumer exists
    consumer = session.get(Consumer, payload.consumer_id)
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONSUMER_NOT_FOUND",
                "message": "Consumer not found",
                "details": {},
            },
        )

    # Validate gym exists (if provided)
    if payload.gym_id:
        gym = session.get(Gym, payload.gym_id)
        if not gym:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "GYM_NOT_FOUND",
                    "message": "Gym not found",
                    "details": {},
                },
            )

    complaint = Complaint(
        consumer_id=payload.consumer_id,
        gym_id=payload.gym_id,
        description=payload.description,
    )
    session.add(complaint)

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="create_complaint",
        resource_type="complaint",
        resource_id=None,
        gym_id=payload.gym_id,
        details={"consumer_id": str(payload.consumer_id)},
    )

    session.commit()
    session.refresh(complaint)

    return ComplaintPublic(
        id=complaint.id,
        consumer_id=complaint.consumer_id,
        gym_id=complaint.gym_id,
        description=complaint.description,
        status=complaint.status,
        assigned_to=complaint.assigned_to,
        notes=complaint.notes,
        resolution=complaint.resolution,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


@router.get("/complaints/{complaint_id}", response_model=ComplaintPublic)
def get_complaint(
    session: SessionDep,
    current_user: CurrentUser,
    complaint_id: UUID,
) -> ComplaintPublic:
    """Get a specific complaint by ID."""
    _require_superuser(current_user)

    complaint = session.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "COMPLAINT_NOT_FOUND",
                "message": "Complaint not found",
                "details": {},
            },
        )

    return ComplaintPublic(
        id=complaint.id,
        consumer_id=complaint.consumer_id,
        gym_id=complaint.gym_id,
        description=complaint.description,
        status=complaint.status,
        assigned_to=complaint.assigned_to,
        notes=complaint.notes,
        resolution=complaint.resolution,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


@router.put("/complaints/{complaint_id}", response_model=ComplaintPublic)
def update_complaint(
    session: SessionDep,
    current_user: CurrentUser,
    complaint_id: UUID,
    payload: ComplaintUpdate,
) -> ComplaintPublic:
    """Update a complaint: assign, change status, add notes, resolve."""
    _require_superuser(current_user)

    complaint = session.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "COMPLAINT_NOT_FOUND",
                "message": "Complaint not found",
                "details": {},
            },
        )

    changes: dict[str, Any] = {}

    if payload.status is not None:
        complaint.status = payload.status
        changes["status"] = payload.status.value

    if payload.assigned_to is not None:
        complaint.assigned_to = payload.assigned_to
        if complaint.status == ComplaintStatus.OPEN:
            complaint.status = ComplaintStatus.ASSIGNED
            changes["status"] = ComplaintStatus.ASSIGNED.value
        changes["assigned_to"] = str(payload.assigned_to)

    if payload.resolution is not None:
        complaint.resolution = payload.resolution
        changes["resolution"] = payload.resolution

    if payload.note:
        # Append note to the notes list
        notes = list(complaint.notes)
        notes.append(
            {
                "admin_id": str(current_user.id),
                "text": payload.note,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        complaint.notes = notes
        changes["note_added"] = True

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="update_complaint",
        resource_type="complaint",
        resource_id=complaint.id,
        gym_id=complaint.gym_id,
        details=changes,
    )

    session.add(complaint)
    session.commit()
    session.refresh(complaint)

    return ComplaintPublic(
        id=complaint.id,
        consumer_id=complaint.consumer_id,
        gym_id=complaint.gym_id,
        description=complaint.description,
        status=complaint.status,
        assigned_to=complaint.assigned_to,
        notes=complaint.notes,
        resolution=complaint.resolution,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


# =============================================================================
# Story 11.4: Account Credit Issuance
# =============================================================================


@router.post(
    "/consumers/{consumer_id}/credits",
    response_model=CreditIssueResponse,
    status_code=status.HTTP_201_CREATED,
)
def issue_credits(
    session: SessionDep,
    current_user: CurrentUser,
    consumer_id: UUID,
    payload: CreditLogCreate,
) -> CreditIssueResponse:
    """Issue class credits to a consumer's marketplace subscription.

    If marketplace_subscription_id is not provided, credits are applied
    to the consumer's active marketplace subscription (if any).
    """
    _require_superuser(current_user)

    # Validate consumer exists
    consumer = session.get(Consumer, consumer_id)
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONSUMER_NOT_FOUND",
                "message": "Consumer not found",
                "details": {},
            },
        )

    # Find or validate subscription
    subscription: MarketplaceSubscription | None = None
    if payload.marketplace_subscription_id:
        subscription = session.get(
            MarketplaceSubscription, payload.marketplace_subscription_id
        )
        if not subscription or subscription.consumer_id != consumer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "SUBSCRIPTION_NOT_FOUND",
                    "message": "Marketplace subscription not found for this consumer",
                    "details": {},
                },
            )
    else:
        # Find active subscription for consumer
        subscription = session.exec(
            select(MarketplaceSubscription).where(
                MarketplaceSubscription.consumer_id == consumer_id,
                MarketplaceSubscription.status == "active",
            )
        ).first()
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "NO_ACTIVE_SUBSCRIPTION",
                    "message": "Consumer has no active marketplace subscription",
                    "details": {},
                },
            )

    # Apply credits
    subscription.classes_remaining += payload.amount
    session.add(subscription)

    # Create credit log
    credit_log = CreditLog(
        consumer_id=consumer_id,
        admin_user_id=current_user.id,
        amount=payload.amount,
        reason=payload.reason,
        marketplace_subscription_id=subscription.id,
    )
    session.add(credit_log)

    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="issue_credit",
        resource_type="consumer",
        resource_id=consumer_id,
        details={
            "amount": payload.amount,
            "reason": payload.reason,
            "subscription_id": str(subscription.id),
        },
    )

    session.commit()
    session.refresh(credit_log)
    session.refresh(subscription)

    return CreditIssueResponse(
        credit_log=CreditLogPublic(
            id=credit_log.id,
            consumer_id=credit_log.consumer_id,
            admin_user_id=credit_log.admin_user_id,
            amount=credit_log.amount,
            reason=credit_log.reason,
            marketplace_subscription_id=credit_log.marketplace_subscription_id,
            created_at=credit_log.created_at,
        ),
        new_classes_remaining=subscription.classes_remaining,
    )


# =============================================================================
# Story 11.5: Platform Health Monitoring
# =============================================================================


@router.get("/health", response_model=PlatformHealthResponse)
def platform_health(
    session: SessionDep,
    current_user: CurrentUser,
) -> PlatformHealthResponse:
    """Platform health statistics dashboard.

    Returns aggregate counts for gyms, consumers, bookings,
    subscriptions, complaints, and payments.
    """
    _require_superuser(current_user)

    total_gyms = session.exec(select(func.count()).select_from(Gym)).one()

    active_gyms = session.exec(
        select(func.count()).select_from(Gym).where(col(Gym.is_active).is_(True))
    ).one()

    total_consumers = session.exec(select(func.count()).select_from(Consumer)).one()

    total_staff = session.exec(select(func.count()).select_from(Staff)).one()

    total_bookings = session.exec(select(func.count()).select_from(Booking)).one()

    active_subscriptions = session.exec(
        select(func.count())
        .select_from(MarketplaceSubscription)
        .where(MarketplaceSubscription.status == "active")
    ).one()

    open_complaints = session.exec(
        select(func.count())
        .select_from(Complaint)
        .where(
            col(Complaint.status).in_([ComplaintStatus.OPEN, ComplaintStatus.ASSIGNED])
        )
    ).one()

    completed_payments = session.exec(
        select(func.count())
        .select_from(Payment)
        .where(Payment.status == PaymentStatus.COMPLETED)
    ).one()

    return PlatformHealthResponse(
        total_gyms=total_gyms,
        active_gyms=active_gyms,
        inactive_gyms=total_gyms - active_gyms,
        total_consumers=total_consumers,
        total_staff=total_staff,
        total_bookings=total_bookings,
        active_marketplace_subscriptions=active_subscriptions,
        open_complaints=open_complaints,
        total_payments_completed=completed_payments,
        timestamp=datetime.now(timezone.utc),
    )


# =============================================================================
# Story 11.6: Gym-Level Data Access for Support
# =============================================================================


@router.get("/gyms/{gym_id}/data", response_model=GymDataResponse)
def get_gym_data(
    session: SessionDep,
    current_user: CurrentUser,
    gym_id: UUID,
    members_limit: int = Query(default=50, ge=1, le=200),
    bookings_limit: int = Query(default=50, ge=1, le=200),
    payments_limit: int = Query(default=50, ge=1, le=200),
) -> GymDataResponse:
    """Access gym-level data for support purposes.

    Returns members, recent bookings, and recent payments
    for the specified gym. Creates an audit log entry.
    """
    _require_superuser(current_user)

    gym = session.get(Gym, gym_id)
    if not gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GYM_NOT_FOUND",
                "message": "Gym not found",
                "details": {},
            },
        )

    # Log the data access
    _create_audit_log(
        session,
        admin_user_id=current_user.id,
        action="view_gym_data",
        resource_type="gym",
        resource_id=gym_id,
        gym_id=gym_id,
        details={"gym_name": gym.name},
    )

    # Fetch members via gym memberships
    memberships = session.exec(
        select(GymMembership, Consumer)
        .join(Consumer, col(GymMembership.consumer_id) == col(Consumer.id))
        .where(GymMembership.gym_id == gym_id)
        .order_by(col(GymMembership.created_at).desc())
        .limit(members_limit)
    ).all()

    members = [
        GymDataMembersItem(
            consumer_id=membership.consumer_id,
            email=consumer.email,
            first_name=consumer.first_name,
            last_name=consumer.last_name,
            membership_status=membership.status.value if membership.status else None,
        )
        for membership, consumer in memberships
    ]

    # Fetch recent bookings
    bookings = session.exec(
        select(Booking)
        .where(Booking.gym_id == gym_id)
        .order_by(col(Booking.created_at).desc())
        .limit(bookings_limit)
    ).all()

    recent_bookings = [
        GymDataBookingItem(
            id=b.id,
            consumer_id=b.consumer_id,
            session_id=b.session_id,
            status=b.status.value,
            created_at=b.created_at,
        )
        for b in bookings
    ]

    # Fetch recent payments
    payments = session.exec(
        select(Payment)
        .where(Payment.gym_id == gym_id)
        .order_by(col(Payment.created_at).desc())
        .limit(payments_limit)
    ).all()

    recent_payments = [
        GymDataPaymentItem(
            id=p.id,
            consumer_id=p.consumer_id,
            amount_cents=p.amount_cents,
            status=p.status.value,
            payment_type=p.payment_type.value,
            created_at=p.created_at,
        )
        for p in payments
    ]

    # Totals
    total_members = session.exec(
        select(func.count())
        .select_from(GymMembership)
        .where(GymMembership.gym_id == gym_id)
    ).one()

    total_bookings_count = session.exec(
        select(func.count()).select_from(Booking).where(Booking.gym_id == gym_id)
    ).one()

    total_revenue_value: int = session.exec(
        select(func.coalesce(func.sum(Payment.amount_cents), 0)).where(
            Payment.gym_id == gym_id,
            Payment.status == PaymentStatus.COMPLETED,
        )
    ).one()

    session.commit()  # Commit audit log

    return GymDataResponse(
        gym_id=gym.id,
        gym_name=gym.name,
        members=members,
        recent_bookings=recent_bookings,
        recent_payments=recent_payments,
        total_members=total_members,
        total_bookings=total_bookings_count,
        total_revenue_cents=total_revenue_value,
    )


# =============================================================================
# Audit Logs
# =============================================================================


@router.get("/audit_logs", response_model=AuditLogListResponse)
def list_audit_logs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    admin_user_id: UUID | None = Query(default=None),
    action: str | None = Query(default=None, max_length=100),
    resource_type: str | None = Query(default=None, max_length=100),
    gym_id: UUID | None = Query(default=None),
) -> AuditLogListResponse:
    """List audit logs with optional filters."""
    _require_superuser(current_user)

    stmt = select(AuditLog)

    if admin_user_id is not None:
        stmt = stmt.where(AuditLog.admin_user_id == admin_user_id)
    if action is not None:
        stmt = stmt.where(AuditLog.action == action)
    if resource_type is not None:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    if gym_id is not None:
        stmt = stmt.where(AuditLog.gym_id == gym_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.exec(count_stmt).one()

    logs = session.exec(
        stmt.order_by(col(AuditLog.created_at).desc()).offset(skip).limit(limit)
    ).all()

    items = [
        AuditLogPublic(
            id=log.id,
            admin_user_id=log.admin_user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            gym_id=log.gym_id,
            details=log.details,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return AuditLogListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
