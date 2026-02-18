"""Notification service for multi-channel dispatch.

Handles creating, sending, and tracking notifications across
in-app, email, push, and WhatsApp channels.

Push (FCM/APNs) and WhatsApp are stubbed for MVP — they log
and record the notification but do not call external APIs.
Email uses the existing SMTP infrastructure from app.utils.
"""

import logging
from datetime import datetime, timezone
from string import Template
from uuid import UUID

from sqlmodel import Session, select

from app.models.notification import (
    GymMessage,
    Notification,
    NotificationChannel,
    NotificationPreference,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
)

logger = logging.getLogger(__name__)

# Map notification types to preference field prefixes
_TYPE_TO_PREF_PREFIX: dict[NotificationType, str] = {
    NotificationType.BOOKING_CONFIRMATION: "booking",
    NotificationType.CLASS_REMINDER: "reminder",
    NotificationType.WAITLIST_SPOT_AVAILABLE: "waitlist",
    NotificationType.PAYMENT_REMINDER: "payment",
    NotificationType.PAYMENT_FAILURE: "payment",
    NotificationType.GYM_MESSAGE: "gym_message",
}

# Types that cannot be fully disabled (critical)
CRITICAL_TYPES: set[NotificationType] = {
    NotificationType.PAYMENT_FAILURE,
    NotificationType.CLASS_CANCELLED,
    NotificationType.EMERGENCY_CLOSURE,
}


def _is_channel_enabled(
    pref: NotificationPreference | None,
    notification_type: NotificationType,
    channel: NotificationChannel,
) -> bool:
    """Check if a channel is enabled for a notification type per consumer prefs."""
    if notification_type in CRITICAL_TYPES:
        return True  # Critical notifications always enabled

    if pref is None:
        return True  # Default: all enabled

    prefix = _TYPE_TO_PREF_PREFIX.get(notification_type)
    if prefix is None:
        return True

    if channel == NotificationChannel.PUSH:
        return getattr(pref, f"{prefix}_push", True)
    elif channel == NotificationChannel.EMAIL:
        return getattr(pref, f"{prefix}_email", True)
    elif channel == NotificationChannel.WHATSAPP:
        return pref.whatsapp_enabled
    elif channel == NotificationChannel.IN_APP:
        return True  # In-app always enabled

    return True


def render_template(template_str: str, context: dict[str, str]) -> str:
    """Render a notification template with context variables."""
    return Template(template_str).safe_substitute(context)


def get_consumer_preferences(
    session: Session, consumer_id: UUID
) -> NotificationPreference | None:
    """Get notification preferences for a consumer."""
    stmt = select(NotificationPreference).where(
        NotificationPreference.consumer_id == consumer_id
    )
    return session.exec(stmt).first()


def create_notification(
    session: Session,
    *,
    consumer_id: UUID,
    notification_type: NotificationType,
    channel: NotificationChannel,
    title: str,
    body: str,
    gym_id: UUID | None = None,
    data: dict[str, str | int | bool | None] | None = None,
    template_id: str | None = None,
    related_entity_id: UUID | None = None,
    scheduled_for: datetime | None = None,
) -> Notification:
    """Create and persist a notification record."""
    notification = Notification(
        consumer_id=consumer_id,
        gym_id=gym_id,
        notification_type=notification_type,
        channel=channel,
        title=title,
        body=body,
        data=data or {},
        template_id=template_id,
        related_entity_id=related_entity_id,
        scheduled_for=scheduled_for,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


def dispatch_notification(
    session: Session, notification: Notification
) -> Notification:
    """Dispatch a notification via its channel.

    For MVP: email uses SMTP, push and WhatsApp are stubbed (logged).
    In-app notifications are marked sent immediately (read from DB).
    """
    try:
        if notification.channel == NotificationChannel.IN_APP:
            notification.mark_sent()
        elif notification.channel == NotificationChannel.EMAIL:
            _send_email_notification(notification)
            notification.mark_sent()
        elif notification.channel == NotificationChannel.PUSH:
            # MVP stub — log and mark sent
            logger.info(
                "PUSH stub: consumer=%s title=%s",
                notification.consumer_id,
                notification.title,
            )
            notification.mark_sent()
        elif notification.channel == NotificationChannel.WHATSAPP:
            # MVP stub — log and mark sent
            logger.info(
                "WHATSAPP stub: consumer=%s title=%s",
                notification.consumer_id,
                notification.title,
            )
            notification.mark_sent()
        else:
            notification.mark_failed(f"Unknown channel: {notification.channel}")
    except Exception as exc:
        notification.mark_failed(str(exc)[:500])
        logger.exception("Failed to dispatch notification %s", notification.id)

    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


def _send_email_notification(notification: Notification) -> None:
    """Send notification via email using existing SMTP infra."""
    from app.core.config import settings

    if not settings.emails_enabled:
        logger.info(
            "EMAIL stub (SMTP not configured): consumer=%s title=%s",
            notification.consumer_id,
            notification.title,
        )
        return

    from app.utils import send_email

    send_email(
        email_to=notification.data.get("email", ""),  # type: ignore[arg-type]
        subject=notification.title,
        html_content=f"<p>{notification.body}</p>",
    )


def send_multi_channel(
    session: Session,
    *,
    consumer_id: UUID,
    notification_type: NotificationType,
    channels: list[NotificationChannel],
    title: str,
    body: str,
    gym_id: UUID | None = None,
    data: dict[str, str | int | bool | None] | None = None,
    related_entity_id: UUID | None = None,
) -> list[Notification]:
    """Send a notification across multiple channels, respecting preferences."""
    pref = get_consumer_preferences(session, consumer_id)
    results: list[Notification] = []

    for channel in channels:
        if not _is_channel_enabled(pref, notification_type, channel):
            continue
        notif = create_notification(
            session,
            consumer_id=consumer_id,
            notification_type=notification_type,
            channel=channel,
            title=title,
            body=body,
            gym_id=gym_id,
            data=data,
            related_entity_id=related_entity_id,
        )
        dispatched = dispatch_notification(session, notif)
        results.append(dispatched)

    return results


def get_template(
    session: Session,
    name: str,
) -> NotificationTemplate | None:
    """Get an active notification template by name."""
    stmt = select(NotificationTemplate).where(
        NotificationTemplate.name == name,
        NotificationTemplate.is_active == True,  # noqa: E712
    )
    return session.exec(stmt).first()


def send_gym_message(
    session: Session,
    *,
    gym_message: GymMessage,
    consumer_ids: list[UUID],
) -> list[Notification]:
    """Dispatch a gym message to a list of consumers."""
    results: list[Notification] = []
    channels = [NotificationChannel(c) for c in gym_message.channels]

    for consumer_id in consumer_ids:
        for channel in channels:
            pref = get_consumer_preferences(session, consumer_id)
            if not _is_channel_enabled(
                pref, NotificationType.GYM_MESSAGE, channel
            ):
                continue
            notif = create_notification(
                session,
                consumer_id=consumer_id,
                notification_type=NotificationType.GYM_MESSAGE,
                channel=channel,
                title=gym_message.subject,
                body=gym_message.body,
                gym_id=gym_message.gym_id,
                related_entity_id=gym_message.id,
            )
            dispatched = dispatch_notification(session, notif)
            results.append(dispatched)

    gym_message.sent_at = datetime.now(timezone.utc)
    gym_message.total_recipients = len(consumer_ids)
    gym_message.delivered_count = sum(
        1 for n in results if n.status == NotificationStatus.SENT
    )
    gym_message.failed_count = sum(
        1 for n in results if n.status == NotificationStatus.FAILED
    )
    session.add(gym_message)
    session.commit()

    return results
