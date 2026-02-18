"""Notification & communication routes (Epic 9).

Covers:
- Notification infrastructure (9-1)
- Booking confirmations (9-2)
- Class reminders (9-3)
- Waitlist notifications (9-4)
- Payment reminders (9-5)
- Payment failure notifications (9-6)
- Gym-to-member messaging (9-7)
- WhatsApp critical notifications (9-8)
- Consumer notification preferences (9-9)
- In-app notification center (9-10)
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Session, col, select

from app.api.deps import (
    CurrentConsumer,
    CurrentStaff,
    RequireOwnerOrManager,
    SessionDep,
    StaffGymDep,
)
from app.models.booking import Booking, BookingStatus  # session_id -> ClassSession
from app.models.class_session import ClassSession  # title, start_time
from app.models.consumer import Consumer
from app.models.gym import Gym
from app.models.gym_membership import GymMembership, GymMembershipStatus
from app.models.notification import (
    GymMessage,
    Notification,
    NotificationChannel,
    NotificationPreference,
    NotificationStatus,
    NotificationType,
)
from app.models.payment import Payment, PaymentStatus
from app.services.notifications.service import (
    create_notification,
    dispatch_notification,
    get_consumer_preferences,
    send_gym_message,
    send_multi_channel,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------


class NotificationPublic(PydanticBaseModel):
    id: UUID
    notification_type: str
    channel: str
    title: str
    body: str
    status: str
    is_read: bool
    read_at: datetime | None
    sent_at: datetime | None
    created_at: datetime
    data: dict[str, str | int | bool | None]
    related_entity_id: UUID | None


class NotificationListResponse(PydanticBaseModel):
    notifications: list[NotificationPublic]
    total: int
    unread_count: int


class MarkReadRequest(PydanticBaseModel):
    notification_ids: list[UUID]


class MarkReadResponse(PydanticBaseModel):
    updated_count: int


class PreferencesPublic(PydanticBaseModel):
    booking_push: bool
    booking_email: bool
    reminder_push: bool
    reminder_email: bool
    reminder_timing_hours: str
    waitlist_push: bool
    waitlist_email: bool
    payment_push: bool
    payment_email: bool
    gym_message_push: bool
    gym_message_email: bool
    whatsapp_enabled: bool


class PreferencesUpdate(PydanticBaseModel):
    booking_push: bool | None = None
    booking_email: bool | None = None
    reminder_push: bool | None = None
    reminder_email: bool | None = None
    reminder_timing_hours: str | None = None
    waitlist_push: bool | None = None
    waitlist_email: bool | None = None
    payment_push: bool | None = None
    payment_email: bool | None = None
    gym_message_push: bool | None = None
    gym_message_email: bool | None = None
    whatsapp_enabled: bool | None = None


class GymMessageRequest(PydanticBaseModel):
    subject: str
    body: str
    recipient_filter: str = "all"  # all | plan:<uuid> | individual
    recipient_ids: list[str] = []
    channels: list[str] = ["in_app"]
    scheduled_for: datetime | None = None


class GymMessagePublic(PydanticBaseModel):
    id: UUID
    gym_id: UUID
    subject: str
    body: str
    recipient_filter: str
    channels: list[str]
    scheduled_for: datetime | None
    sent_at: datetime | None
    total_recipients: int
    delivered_count: int
    failed_count: int
    created_at: datetime


class SendBookingConfirmationRequest(PydanticBaseModel):
    booking_id: UUID
    class_name: str
    gym_name: str
    date: str
    time: str
    instructor: str | None = None


class SendReminderRequest(PydanticBaseModel):
    booking_id: UUID
    class_name: str
    gym_name: str
    time: str
    location: str | None = None
    hours_before: int = 2


class SendWaitlistNotificationRequest(PydanticBaseModel):
    consumer_id: UUID
    class_name: str
    gym_name: str
    time_to_respond_minutes: int = 30
    related_entity_id: UUID | None = None


class SendPaymentReminderRequest(PydanticBaseModel):
    consumer_id: UUID
    amount_display: str
    due_date: str
    membership_name: str


class SendPaymentFailureRequest(PydanticBaseModel):
    consumer_id: UUID
    description: str
    failure_reason: str | None = None
    payment_id: UUID | None = None


class WhatsAppCriticalRequest(PydanticBaseModel):
    consumer_ids: list[UUID]
    notification_type: str  # class_cancelled | emergency_closure
    title: str
    body: str
    gym_id: UUID


class TriggerRemindersResponse(PydanticBaseModel):
    reminders_sent: int
    booking_ids: list[str]


class TriggerPaymentRemindersResponse(PydanticBaseModel):
    reminders_sent: int
    consumer_ids: list[str]


# ---------------------------------------------------------------------------
# Story 9-1: Infrastructure health check
# ---------------------------------------------------------------------------


@router.get("/health")
def notification_health() -> dict[str, str]:
    return {"status": "ok", "service": "notifications"}


# ---------------------------------------------------------------------------
# Story 9-2: Booking confirmation notifications
# ---------------------------------------------------------------------------


@router.post("/booking-confirmation")
def send_booking_confirmation(
    req: SendBookingConfirmationRequest,
    session: SessionDep,
    consumer: CurrentConsumer,
) -> dict[str, str | int]:
    instructor_part = f", Instructor: {req.instructor}" if req.instructor else ""
    title = "Booking Confirmed"
    body = (
        f"You're booked for {req.class_name} at {req.gym_name}, "
        f"{req.date} {req.time}{instructor_part}"
    )
    channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.PUSH]
    results = send_multi_channel(
        session,
        consumer_id=consumer.id,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        channels=channels,
        title=title,
        body=body,
        data={
            "booking_id": str(req.booking_id),
            "class_name": req.class_name,
            "gym_name": req.gym_name,
            "email": consumer.email,
        },
        related_entity_id=req.booking_id,
    )
    return {"status": "sent", "channels_dispatched": len(results)}


# ---------------------------------------------------------------------------
# Story 9-3: Class reminder notifications
# ---------------------------------------------------------------------------


@router.post("/reminders/trigger")
def trigger_class_reminders(
    session: SessionDep,
    _staff: StaffGymDep,
    hours_before: int = Query(default=2, ge=1, le=48),
) -> TriggerRemindersResponse:
    """Trigger class reminders for bookings starting within hours_before."""
    now = datetime.now(timezone.utc)
    window_start = now
    window_end = now + timedelta(hours=hours_before)

    stmt = (
        select(Booking, ClassSession)
        .join(ClassSession, Booking.session_id == ClassSession.id)  # type: ignore[arg-type]
        .where(
            Booking.status == BookingStatus.BOOKED,
            col(ClassSession.start_time) >= window_start,
            col(ClassSession.start_time) <= window_end,
        )
    )
    rows = session.exec(stmt).all()

    sent_ids: list[str] = []
    for booking, class_session in rows:
        consumer = session.get(Consumer, booking.consumer_id)
        gym = session.get(Gym, class_session.gym_id)
        if not consumer or not gym:
            continue
        title = "Class Reminder"
        body = (
            f"Your class {class_session.title} at {gym.name} "
            f"starts at {class_session.start_time.strftime('%H:%M')}"
        )
        send_multi_channel(
            session,
            consumer_id=consumer.id,
            notification_type=NotificationType.CLASS_REMINDER,
            channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH],
            title=title,
            body=body,
            gym_id=gym.id,
            related_entity_id=booking.id,
        )
        sent_ids.append(str(booking.id))

    return TriggerRemindersResponse(reminders_sent=len(sent_ids), booking_ids=sent_ids)


# ---------------------------------------------------------------------------
# Story 9-4: Waitlist notifications
# ---------------------------------------------------------------------------


@router.post("/waitlist-spot")
def send_waitlist_notification(
    req: SendWaitlistNotificationRequest,
    session: SessionDep,
    _staff: StaffGymDep,
) -> dict[str, str | int]:
    title = "Waitlist Spot Available!"
    body = (
        f"A spot opened for {req.class_name} at {req.gym_name}. "
        f"Confirm within {req.time_to_respond_minutes} minutes."
    )
    channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.PUSH]
    results = send_multi_channel(
        session,
        consumer_id=req.consumer_id,
        notification_type=NotificationType.WAITLIST_SPOT_AVAILABLE,
        channels=channels,
        title=title,
        body=body,
        data={"time_to_respond_minutes": req.time_to_respond_minutes},
        related_entity_id=req.related_entity_id,
    )
    return {"status": "sent", "channels_dispatched": len(results)}


# ---------------------------------------------------------------------------
# Story 9-5: Payment reminder notifications
# ---------------------------------------------------------------------------


@router.post("/payment-reminders/trigger")
def trigger_payment_reminders(
    session: SessionDep,
    _staff: StaffGymDep,
    days_before: int = Query(default=3, ge=1, le=14),
) -> TriggerPaymentRemindersResponse:
    """Trigger payment reminders for memberships renewing within days_before."""
    now = datetime.now(timezone.utc)
    window_end = now + timedelta(days=days_before)

    stmt = select(GymMembership).where(
        GymMembership.status == GymMembershipStatus.ACTIVE,
        col(GymMembership.end_date) >= now,
        col(GymMembership.end_date) <= window_end,
    )
    memberships = session.exec(stmt).all()

    sent_consumer_ids: list[str] = []
    for membership in memberships:
        consumer = session.get(Consumer, membership.consumer_id)
        gym = session.get(Gym, membership.gym_id)
        if not consumer or not gym:
            continue

        title = "Payment Due Soon"
        body = (
            f"Your membership at {gym.name} renews on "
            f"{membership.end_date.strftime('%d %b %Y')}."
        )
        send_multi_channel(
            session,
            consumer_id=consumer.id,
            notification_type=NotificationType.PAYMENT_REMINDER,
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.PUSH],
            title=title,
            body=body,
            gym_id=gym.id,
        )
        sent_consumer_ids.append(str(consumer.id))

    return TriggerPaymentRemindersResponse(
        reminders_sent=len(sent_consumer_ids),
        consumer_ids=sent_consumer_ids,
    )


# ---------------------------------------------------------------------------
# Story 9-6: Payment failure notifications
# ---------------------------------------------------------------------------


@router.post("/payment-failure")
def send_payment_failure_notification(
    req: SendPaymentFailureRequest,
    session: SessionDep,
    _staff: StaffGymDep,
) -> dict[str, str | int]:
    title = "Payment Failed"
    body = f"Your payment for {req.description} failed."
    if req.failure_reason:
        body += f" Reason: {req.failure_reason}."
    body += " Please update your payment method."

    channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL, NotificationChannel.PUSH]
    results = send_multi_channel(
        session,
        consumer_id=req.consumer_id,
        notification_type=NotificationType.PAYMENT_FAILURE,
        channels=channels,
        title=title,
        body=body,
        related_entity_id=req.payment_id,
    )
    return {"status": "sent", "channels_dispatched": len(results)}


# ---------------------------------------------------------------------------
# Story 9-7: Gym-to-member messaging
# ---------------------------------------------------------------------------


@router.post("/gyms/{gym_id}/messages", dependencies=[RequireOwnerOrManager])
def send_gym_message_route(
    gym_id: UUID,
    req: GymMessageRequest,
    session: SessionDep,
    staff: StaffGymDep,
) -> GymMessagePublic:
    # Resolve recipient consumer IDs
    consumer_ids: list[UUID] = []
    if req.recipient_filter == "all":
        stmt = select(GymMembership.consumer_id).where(
            GymMembership.gym_id == gym_id,
            GymMembership.status == GymMembershipStatus.ACTIVE,
        )
        consumer_ids = list(session.exec(stmt).all())
    elif req.recipient_filter.startswith("plan:"):
        plan_id = req.recipient_filter.split(":", 1)[1]
        stmt = select(GymMembership.consumer_id).where(
            GymMembership.gym_id == gym_id,
            GymMembership.membership_plan_id == UUID(plan_id),
            GymMembership.status == GymMembershipStatus.ACTIVE,
        )
        consumer_ids = list(session.exec(stmt).all())
    elif req.recipient_filter == "individual":
        consumer_ids = [UUID(cid) for cid in req.recipient_ids]

    msg = GymMessage(
        gym_id=gym_id,
        sender_staff_id=staff.id,
        subject=req.subject,
        body=req.body,
        recipient_filter=req.recipient_filter,
        recipient_ids=req.recipient_ids,
        channels=req.channels,
        scheduled_for=req.scheduled_for,
    )
    session.add(msg)
    session.commit()
    session.refresh(msg)

    if not req.scheduled_for:
        send_gym_message(session, gym_message=msg, consumer_ids=consumer_ids)
        session.refresh(msg)

    return GymMessagePublic(
        id=msg.id,
        gym_id=msg.gym_id,
        subject=msg.subject,
        body=msg.body,
        recipient_filter=msg.recipient_filter,
        channels=msg.channels,
        scheduled_for=msg.scheduled_for,
        sent_at=msg.sent_at,
        total_recipients=msg.total_recipients,
        delivered_count=msg.delivered_count,
        failed_count=msg.failed_count,
        created_at=msg.created_at,
    )


# ---------------------------------------------------------------------------
# Story 9-8: WhatsApp critical notifications
# ---------------------------------------------------------------------------


@router.post("/whatsapp/critical", dependencies=[RequireOwnerOrManager])
def send_whatsapp_critical(
    req: WhatsAppCriticalRequest,
    session: SessionDep,
    _staff: StaffGymDep,
) -> dict[str, str | int]:
    notif_type_map: dict[str, NotificationType] = {
        "class_cancelled": NotificationType.CLASS_CANCELLED,
        "emergency_closure": NotificationType.EMERGENCY_CLOSURE,
    }
    notif_type = notif_type_map.get(
        req.notification_type, NotificationType.EMERGENCY_CLOSURE
    )

    total_sent = 0
    for consumer_id in req.consumer_ids:
        results = send_multi_channel(
            session,
            consumer_id=consumer_id,
            notification_type=notif_type,
            channels=[
                NotificationChannel.WHATSAPP,
                NotificationChannel.EMAIL,  # fallback
                NotificationChannel.IN_APP,
            ],
            title=req.title,
            body=req.body,
            gym_id=req.gym_id,
        )
        total_sent += len(results)

    return {"status": "sent", "total_notifications": total_sent}


# ---------------------------------------------------------------------------
# Story 9-9: Consumer notification preferences
# ---------------------------------------------------------------------------


@router.get("/me/preferences")
def get_preferences(
    session: SessionDep,
    consumer: CurrentConsumer,
) -> PreferencesPublic:
    pref = get_consumer_preferences(session, consumer.id)
    if pref is None:
        pref = NotificationPreference(consumer_id=consumer.id)
        session.add(pref)
        session.commit()
        session.refresh(pref)

    return PreferencesPublic(
        booking_push=pref.booking_push,
        booking_email=pref.booking_email,
        reminder_push=pref.reminder_push,
        reminder_email=pref.reminder_email,
        reminder_timing_hours=pref.reminder_timing_hours,
        waitlist_push=pref.waitlist_push,
        waitlist_email=pref.waitlist_email,
        payment_push=pref.payment_push,
        payment_email=pref.payment_email,
        gym_message_push=pref.gym_message_push,
        gym_message_email=pref.gym_message_email,
        whatsapp_enabled=pref.whatsapp_enabled,
    )


@router.patch("/me/preferences")
def update_preferences(
    req: PreferencesUpdate,
    session: SessionDep,
    consumer: CurrentConsumer,
) -> PreferencesPublic:
    pref = get_consumer_preferences(session, consumer.id)
    if pref is None:
        pref = NotificationPreference(consumer_id=consumer.id)
        session.add(pref)
        session.commit()
        session.refresh(pref)

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pref, field, value)

    pref.updated_at = datetime.now(timezone.utc)
    session.add(pref)
    session.commit()
    session.refresh(pref)

    return PreferencesPublic(
        booking_push=pref.booking_push,
        booking_email=pref.booking_email,
        reminder_push=pref.reminder_push,
        reminder_email=pref.reminder_email,
        reminder_timing_hours=pref.reminder_timing_hours,
        waitlist_push=pref.waitlist_push,
        waitlist_email=pref.waitlist_email,
        payment_push=pref.payment_push,
        payment_email=pref.payment_email,
        gym_message_push=pref.gym_message_push,
        gym_message_email=pref.gym_message_email,
        whatsapp_enabled=pref.whatsapp_enabled,
    )


# ---------------------------------------------------------------------------
# Story 9-10: In-app notification center
# ---------------------------------------------------------------------------


@router.get("/me")
def list_my_notifications(
    session: SessionDep,
    consumer: CurrentConsumer,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    unread_only: bool = Query(default=False),
) -> NotificationListResponse:
    stmt = select(Notification).where(
        Notification.consumer_id == consumer.id,
        Notification.channel == NotificationChannel.IN_APP,
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712

    # Total & unread counts
    from sqlalchemy import func

    count_stmt = select(func.count()).select_from(Notification).where(
        Notification.consumer_id == consumer.id,
        Notification.channel == NotificationChannel.IN_APP,
    )
    total = session.exec(count_stmt).one()

    unread_stmt = select(func.count()).select_from(Notification).where(
        Notification.consumer_id == consumer.id,
        Notification.channel == NotificationChannel.IN_APP,
        Notification.is_read == False,  # noqa: E712
    )
    unread_count = session.exec(unread_stmt).one()

    stmt = stmt.order_by(col(Notification.created_at).desc()).offset(skip).limit(limit)
    notifications = session.exec(stmt).all()

    return NotificationListResponse(
        notifications=[
            NotificationPublic(
                id=n.id,
                notification_type=n.notification_type,
                channel=n.channel,
                title=n.title,
                body=n.body,
                status=n.status,
                is_read=n.is_read,
                read_at=n.read_at,
                sent_at=n.sent_at,
                created_at=n.created_at,
                data=n.data,
                related_entity_id=n.related_entity_id,
            )
            for n in notifications
        ],
        total=total,
        unread_count=unread_count,
    )


@router.post("/me/mark-read")
def mark_notifications_read(
    req: MarkReadRequest,
    session: SessionDep,
    consumer: CurrentConsumer,
) -> MarkReadResponse:
    updated = 0
    for nid in req.notification_ids:
        stmt = select(Notification).where(
            Notification.id == nid,
            Notification.consumer_id == consumer.id,
        )
        notif = session.exec(stmt).first()
        if notif and not notif.is_read:
            notif.mark_read()
            session.add(notif)
            updated += 1

    session.commit()
    return MarkReadResponse(updated_count=updated)
