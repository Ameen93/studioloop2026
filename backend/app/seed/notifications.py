"""Seed data for Notification entities.

Creates a realistic mix of notifications that consumers would receive:
booking confirmations, class reminders, payment receipts, gym messages, etc.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import Booking, Consumer, Gym, Notification
from app.models.booking import BookingStatus
from app.models.notification import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)

# Notification templates for each type
NOTIFICATION_TEMPLATES: dict[str, dict[str, str]] = {
    "BOOKING_CONFIRMATION": {
        "title": "Booking Confirmed",
        "body": "Your class booking has been confirmed. See you there!",
    },
    "CLASS_REMINDER": {
        "title": "Class Starting Soon",
        "body": "Your class starts in 1 hour. Don't forget your towel and water!",
    },
    "CLASS_CANCELLED": {
        "title": "Class Cancelled",
        "body": "Unfortunately, your upcoming class has been cancelled. You'll receive a full refund.",
    },
    "PAYMENT_REMINDER": {
        "title": "Payment Due",
        "body": "Your membership payment is due in 3 days. Please ensure your payment method is up to date.",
    },
    "PAYMENT_FAILURE": {
        "title": "Payment Failed",
        "body": "We couldn't process your payment. Please update your payment method to avoid service interruption.",
    },
    "GYM_MESSAGE": {
        "title": "Message from Your Gym",
        "body": "Check out our new schedule for next week! We've added extra yoga and spin classes.",
    },
    "WAITLIST_SPOT_AVAILABLE": {
        "title": "Spot Available!",
        "body": "Great news! A spot has opened up in the class you were waiting for. Book now before it fills up!",
    },
    "EMERGENCY_CLOSURE": {
        "title": "Emergency Closure Notice",
        "body": "Due to unforeseen circumstances, the gym will be closed today. We apologise for the inconvenience.",
    },
}


def seed_notifications(session: Session) -> int:
    """Seed notifications for consumers idempotently.

    Creates ~100-200 notifications across all types:
    - Booking confirmations for recent bookings
    - Class reminders for upcoming classes
    - Payment reminders and failures
    - Gym messages and announcements
    - A few emergency closures

    Channel mix: 40% IN_APP, 25% EMAIL, 20% PUSH, 15% WHATSAPP
    Status: 50% DELIVERED, 25% SENT, 15% PENDING, 10% FAILED

    Args:
        session: SQLModel database session

    Returns:
        Number of notifications created/found
    """
    existing = session.exec(select(Notification.id)).all()
    if len(existing) > 0:
        return len(existing)

    consumers = session.exec(select(Consumer)).all()
    gyms = session.exec(select(Gym)).all()
    if not consumers or not gyms:
        return 0

    now = datetime.now(timezone.utc)
    count = 0

    # --- Booking confirmations (from recent bookings) ---
    recent_bookings = session.exec(
        select(Booking).where(Booking.status == BookingStatus.BOOKED)
    ).all()

    for i, booking in enumerate(recent_bookings[:40]):
        tmpl = NOTIFICATION_TEMPLATES["BOOKING_CONFIRMATION"]
        channel, status, status_times = _pick_channel_and_status(i, now)

        notif = Notification(
            consumer_id=booking.consumer_id,
            gym_id=booking.gym_id,
            notification_type=NotificationType.BOOKING_CONFIRMATION,
            channel=channel,
            title=tmpl["title"],
            body=tmpl["body"],
            status=status,
            data={"booking_id": str(booking.id)},
            related_entity_id=booking.id,
            **status_times,
        )
        session.add(notif)
        count += 1

    # --- Class reminders (for upcoming bookings) ---
    for i, booking in enumerate(recent_bookings[10:30]):
        tmpl = NOTIFICATION_TEMPLATES["CLASS_REMINDER"]
        channel, status, status_times = _pick_channel_and_status(i + 40, now)

        notif = Notification(
            consumer_id=booking.consumer_id,
            gym_id=booking.gym_id,
            notification_type=NotificationType.CLASS_REMINDER,
            channel=channel,
            title=tmpl["title"],
            body=tmpl["body"],
            status=status,
            data={"booking_id": str(booking.id)},
            related_entity_id=booking.id,
            scheduled_for=now + timedelta(hours=1),
            **status_times,
        )
        session.add(notif)
        count += 1

    # --- Payment reminders (one per consumer who has a membership) ---
    for i, consumer in enumerate(consumers[:8]):
        tmpl = NOTIFICATION_TEMPLATES["PAYMENT_REMINDER"]
        gym = gyms[i % len(gyms)]
        channel, status, status_times = _pick_channel_and_status(i + 80, now)

        notif = Notification(
            consumer_id=consumer.id,
            gym_id=gym.id,
            notification_type=NotificationType.PAYMENT_REMINDER,
            channel=channel,
            title=tmpl["title"],
            body=tmpl["body"],
            status=status,
            **status_times,
        )
        session.add(notif)
        count += 1

    # --- Payment failures (a few) ---
    for i, consumer in enumerate(consumers[8:12]):
        tmpl = NOTIFICATION_TEMPLATES["PAYMENT_FAILURE"]
        gym = gyms[i % len(gyms)]
        channel, status, status_times = _pick_channel_and_status(i + 100, now)

        notif = Notification(
            consumer_id=consumer.id,
            gym_id=gym.id,
            notification_type=NotificationType.PAYMENT_FAILURE,
            channel=channel,
            title=tmpl["title"],
            body=tmpl["body"],
            status=status,
            **status_times,
        )
        session.add(notif)
        count += 1

    # --- Gym messages (announcements to all members per gym) ---
    for i, gym in enumerate(gyms):
        tmpl = NOTIFICATION_TEMPLATES["GYM_MESSAGE"]
        # Send to first 5 consumers for each gym
        for j in range(5):
            consumer = consumers[(i * 5 + j) % len(consumers)]
            channel, status, status_times = _pick_channel_and_status(
                i * 5 + j + 120, now
            )

            notif = Notification(
                consumer_id=consumer.id,
                gym_id=gym.id,
                notification_type=NotificationType.GYM_MESSAGE,
                channel=channel,
                title=tmpl["title"],
                body=tmpl["body"],
                status=status,
                is_read=j % 3 == 0,
                read_at=now - timedelta(hours=j) if j % 3 == 0 else None,
                **status_times,
            )
            session.add(notif)
            count += 1

    # --- Emergency closure (rare — just 2) ---
    for i in range(2):
        gym = gyms[i]
        tmpl = NOTIFICATION_TEMPLATES["EMERGENCY_CLOSURE"]
        for j, consumer in enumerate(consumers[:6]):
            channel, status, status_times = _pick_channel_and_status(
                i * 6 + j + 200, now
            )

            notif = Notification(
                consumer_id=consumer.id,
                gym_id=gym.id,
                notification_type=NotificationType.EMERGENCY_CLOSURE,
                channel=channel,
                title=tmpl["title"],
                body=tmpl["body"],
                status=status,
                **status_times,
            )
            session.add(notif)
            count += 1

    session.commit()
    return count


def _pick_channel_and_status(
    index: int, now: datetime
) -> tuple[NotificationChannel, NotificationStatus, dict]:
    """Pick a channel and status based on index for deterministic distribution."""
    # Channel: 40% IN_APP, 25% EMAIL, 20% PUSH, 15% WHATSAPP
    channel_roll = index % 20
    if channel_roll < 8:
        channel = NotificationChannel.IN_APP
    elif channel_roll < 13:
        channel = NotificationChannel.EMAIL
    elif channel_roll < 17:
        channel = NotificationChannel.PUSH
    else:
        channel = NotificationChannel.WHATSAPP

    # Status: 50% DELIVERED, 25% SENT, 15% PENDING, 10% FAILED
    status_roll = index % 20
    status_times: dict = {
        "sent_at": None,
        "delivered_at": None,
        "failed_at": None,
        "failure_reason": None,
    }

    if status_roll < 10:
        status = NotificationStatus.DELIVERED
        status_times["sent_at"] = now - timedelta(hours=(index % 48) + 1)
        status_times["delivered_at"] = status_times["sent_at"] + timedelta(seconds=5)
    elif status_roll < 15:
        status = NotificationStatus.SENT
        status_times["sent_at"] = now - timedelta(hours=(index % 24) + 1)
    elif status_roll < 18:
        status = NotificationStatus.PENDING
    else:
        status = NotificationStatus.FAILED
        status_times["sent_at"] = now - timedelta(hours=(index % 12) + 1)
        status_times["failed_at"] = status_times["sent_at"] + timedelta(seconds=10)
        status_times["failure_reason"] = "Delivery failed: recipient unreachable"

    return channel, status, status_times
