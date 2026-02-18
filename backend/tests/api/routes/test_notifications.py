"""Tests for Story 9-1: Notification Infrastructure Setup.

Validates:
- Health check endpoint
- Notification model CRUD (create, read, mark_sent/delivered/failed/read)
- Service layer: create_notification, dispatch_notification, send_multi_channel
- Consumer preference checks (_is_channel_enabled)
- Template rendering
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import (
    Gym,
    Notification,
    NotificationChannel,
    NotificationPreference,
    NotificationStatus,
    NotificationType,
    StaffRole,
)
from app.services.notifications.service import (
    _is_channel_enabled,
    create_notification,
    dispatch_notification,
    get_consumer_preferences,
    render_template,
    send_multi_channel,
)
from tests.api.routes.test_staff_memberships import _consumer_headers, _staff_headers


# ---------------------------------------------------------------------------
# Story 9-1: Health check
# ---------------------------------------------------------------------------


def test_notification_health_check(client: TestClient) -> None:
    res = client.get("/api/v1/notifications/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["service"] == "notifications"


# ---------------------------------------------------------------------------
# Model lifecycle
# ---------------------------------------------------------------------------


def test_notification_model_lifecycle(db: Session) -> None:
    """Create a Notification, mark sent, delivered, read, and verify timestamps."""
    headers_unused, consumer = _get_or_create_consumer(db)

    notif = Notification(
        consumer_id=consumer.id,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        channel=NotificationChannel.IN_APP,
        title="Test Title",
        body="Test Body",
        data={"key": "value"},
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    assert notif.id is not None
    assert notif.status == NotificationStatus.PENDING
    assert notif.is_read is False

    notif.mark_sent()
    db.add(notif)
    db.commit()
    db.refresh(notif)
    assert notif.status == NotificationStatus.SENT
    assert notif.sent_at is not None

    notif.mark_delivered()
    db.add(notif)
    db.commit()
    db.refresh(notif)
    assert notif.status == NotificationStatus.DELIVERED
    assert notif.delivered_at is not None

    notif.mark_read()
    db.add(notif)
    db.commit()
    db.refresh(notif)
    assert notif.is_read is True
    assert notif.read_at is not None

    # Clean up
    db.delete(notif)
    db.commit()


def test_notification_mark_failed(db: Session) -> None:
    _headers, consumer = _get_or_create_consumer(db)

    notif = Notification(
        consumer_id=consumer.id,
        notification_type=NotificationType.GYM_MESSAGE,
        channel=NotificationChannel.EMAIL,
        title="Fail Test",
        body="Should fail",
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    notif.mark_failed("SMTP timeout")
    db.add(notif)
    db.commit()
    db.refresh(notif)

    assert notif.status == NotificationStatus.FAILED
    assert notif.failed_at is not None
    assert notif.failure_reason == "SMTP timeout"

    db.delete(notif)
    db.commit()


# ---------------------------------------------------------------------------
# Service layer
# ---------------------------------------------------------------------------


def test_create_notification_service(db: Session) -> None:
    _headers, consumer = _get_or_create_consumer(db)

    notif = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.CLASS_REMINDER,
        channel=NotificationChannel.PUSH,
        title="Reminder",
        body="Your class starts soon",
    )
    assert notif.id is not None
    assert notif.status == NotificationStatus.PENDING
    assert notif.consumer_id == consumer.id

    db.delete(notif)
    db.commit()


def test_dispatch_notification_in_app(db: Session) -> None:
    _headers, consumer = _get_or_create_consumer(db)

    notif = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        channel=NotificationChannel.IN_APP,
        title="Booked",
        body="You are booked",
    )
    dispatched = dispatch_notification(db, notif)
    assert dispatched.status == NotificationStatus.SENT
    assert dispatched.sent_at is not None

    db.delete(dispatched)
    db.commit()


def test_dispatch_notification_push_stub(db: Session) -> None:
    _headers, consumer = _get_or_create_consumer(db)

    notif = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.CLASS_REMINDER,
        channel=NotificationChannel.PUSH,
        title="Push Test",
        body="Push body",
    )
    dispatched = dispatch_notification(db, notif)
    assert dispatched.status == NotificationStatus.SENT

    db.delete(dispatched)
    db.commit()


def test_dispatch_notification_whatsapp_stub(db: Session) -> None:
    _headers, consumer = _get_or_create_consumer(db)

    notif = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.EMERGENCY_CLOSURE,
        channel=NotificationChannel.WHATSAPP,
        title="Emergency",
        body="Studio closed",
    )
    dispatched = dispatch_notification(db, notif)
    assert dispatched.status == NotificationStatus.SENT

    db.delete(dispatched)
    db.commit()


def test_dispatch_notification_email_stub(db: Session) -> None:
    """Email dispatch with SMTP disabled should still mark sent."""
    _headers, consumer = _get_or_create_consumer(db)

    notif = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.PAYMENT_REMINDER,
        channel=NotificationChannel.EMAIL,
        title="Payment Due",
        body="Please pay",
        data={"email": "test@example.com"},
    )
    dispatched = dispatch_notification(db, notif)
    assert dispatched.status == NotificationStatus.SENT

    db.delete(dispatched)
    db.commit()


def test_send_multi_channel(db: Session) -> None:
    _headers, consumer = _get_or_create_consumer(db)

    results = send_multi_channel(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH],
        title="Multi Test",
        body="Multi body",
    )
    assert len(results) == 2
    assert all(n.status == NotificationStatus.SENT for n in results)

    for n in results:
        db.delete(n)
    db.commit()


# ---------------------------------------------------------------------------
# Preference checks
# ---------------------------------------------------------------------------


def test_is_channel_enabled_defaults() -> None:
    """Without preferences, all channels are enabled."""
    assert _is_channel_enabled(None, NotificationType.BOOKING_CONFIRMATION, NotificationChannel.PUSH) is True
    assert _is_channel_enabled(None, NotificationType.BOOKING_CONFIRMATION, NotificationChannel.EMAIL) is True
    assert _is_channel_enabled(None, NotificationType.BOOKING_CONFIRMATION, NotificationChannel.IN_APP) is True


def test_is_channel_enabled_critical_always_on() -> None:
    """Critical notification types are always enabled regardless of prefs."""
    pref = NotificationPreference(
        consumer_id=uuid4(),
        booking_push=False,
        booking_email=False,
        whatsapp_enabled=False,
    )
    assert _is_channel_enabled(pref, NotificationType.PAYMENT_FAILURE, NotificationChannel.PUSH) is True
    assert _is_channel_enabled(pref, NotificationType.CLASS_CANCELLED, NotificationChannel.EMAIL) is True
    assert _is_channel_enabled(pref, NotificationType.EMERGENCY_CLOSURE, NotificationChannel.WHATSAPP) is True


def test_is_channel_enabled_respects_prefs() -> None:
    """Preferences correctly disable non-critical channels."""
    pref = NotificationPreference(
        consumer_id=uuid4(),
        booking_push=False,
        booking_email=True,
    )
    assert _is_channel_enabled(pref, NotificationType.BOOKING_CONFIRMATION, NotificationChannel.PUSH) is False
    assert _is_channel_enabled(pref, NotificationType.BOOKING_CONFIRMATION, NotificationChannel.EMAIL) is True
    assert _is_channel_enabled(pref, NotificationType.BOOKING_CONFIRMATION, NotificationChannel.IN_APP) is True


def test_send_multi_channel_respects_prefs(db: Session) -> None:
    """Multi-channel send skips disabled channels."""
    _headers, consumer = _get_or_create_consumer(db)

    # Create preference disabling push for bookings
    pref = NotificationPreference(consumer_id=consumer.id, booking_push=False)
    db.add(pref)
    db.commit()

    results = send_multi_channel(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH],
        title="Pref Test",
        body="Should skip push",
    )
    # Only IN_APP should be sent (push disabled)
    assert len(results) == 1
    assert results[0].channel == NotificationChannel.IN_APP

    for n in results:
        db.delete(n)
    db.delete(pref)
    db.commit()


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------


def test_render_template() -> None:
    result = render_template(
        "Hello $name, your class $class starts at $time",
        {"name": "Thandi", "class": "Yoga", "time": "09:00"},
    )
    assert result == "Hello Thandi, your class Yoga starts at 09:00"


def test_render_template_missing_vars() -> None:
    """Missing variables should be left as-is (safe_substitute)."""
    result = render_template("Hello $name, $missing_var", {"name": "Test"})
    assert "Test" in result
    assert "$missing_var" in result


# ---------------------------------------------------------------------------
# Consumer preferences CRUD via API
# ---------------------------------------------------------------------------


def test_get_preferences_creates_defaults(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)

    res = client.get("/api/v1/notifications/me/preferences", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["booking_push"] is True
    assert body["booking_email"] is True
    assert body["whatsapp_enabled"] is True

    # Clean up created preference
    pref = db.exec(
        select(NotificationPreference).where(NotificationPreference.consumer_id == consumer.id)
    ).first()
    if pref:
        db.delete(pref)
        db.commit()


def test_update_preferences(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)

    # Ensure defaults exist
    client.get("/api/v1/notifications/me/preferences", headers=headers)

    res = client.patch(
        "/api/v1/notifications/me/preferences",
        json={"booking_push": False, "whatsapp_enabled": False},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["booking_push"] is False
    assert body["whatsapp_enabled"] is False
    assert body["booking_email"] is True  # unchanged

    # Clean up
    pref = db.exec(
        select(NotificationPreference).where(NotificationPreference.consumer_id == consumer.id)
    ).first()
    if pref:
        db.delete(pref)
        db.commit()


# ---------------------------------------------------------------------------
# In-app notification center (list + mark read)
# ---------------------------------------------------------------------------


def test_list_notifications_empty(client: TestClient, db: Session) -> None:
    headers, _consumer = _consumer_headers(client, db)

    res = client.get("/api/v1/notifications/me", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 0
    assert body["unread_count"] == 0
    assert body["notifications"] == []


def test_list_and_mark_read_notifications(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)

    # Create two in-app notifications directly
    n1 = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        channel=NotificationChannel.IN_APP,
        title="Notif 1",
        body="Body 1",
    )
    dispatch_notification(db, n1)

    n2 = create_notification(
        db,
        consumer_id=consumer.id,
        notification_type=NotificationType.CLASS_REMINDER,
        channel=NotificationChannel.IN_APP,
        title="Notif 2",
        body="Body 2",
    )
    dispatch_notification(db, n2)

    # List all
    res = client.get("/api/v1/notifications/me", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert body["unread_count"] == 2

    # Filter unread only
    res = client.get("/api/v1/notifications/me?unread_only=true", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["notifications"]) == 2

    # Mark one as read
    res = client.post(
        "/api/v1/notifications/me/mark-read",
        json={"notification_ids": [str(n1.id)]},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["updated_count"] == 1

    # Verify unread count dropped
    res = client.get("/api/v1/notifications/me", headers=headers)
    assert res.json()["unread_count"] == 1

    # Clean up
    db.delete(n1)
    db.delete(n2)
    db.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from app.core.security import get_password_hash
from app.models import Consumer


def _get_or_create_consumer(db: Session) -> tuple[dict[str, str], Consumer]:
    """Get an existing consumer or create one for service-layer tests."""
    consumer = db.exec(select(Consumer)).first()
    if consumer:
        return {}, consumer

    consumer = Consumer(
        email=f"notif-test-{uuid4().hex[:8]}@example.com",
        first_name="Notif",
        last_name="Tester",
        hashed_password=get_password_hash("S3curePass!123"),
        is_email_verified=True,
        is_active=True,
    )
    db.add(consumer)
    db.commit()
    db.refresh(consumer)
    return {}, consumer
