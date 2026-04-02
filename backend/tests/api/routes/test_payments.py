import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import (
    Booking,
    BookingStatus,
    ClassSession,
    Gym,
    GymMembership,
    GymMembershipStatus,
    MarketplaceSubscription,
    MarketplaceSubscriptionStatus,
    Payment,
    PaymentStatus,
    PaymentType,
    Space,
    StaffRole,
)
from app.services.payments.providers import build_webhook_signature
from tests.api.routes.test_staff_memberships import _consumer_headers, _staff_headers


class _MockStitchProvider:
    def initiate(self, payment: Payment):
        class _Result:
            provider_reference = "stitch-pir-123"
            redirect_url = "https://secure.stitch.money/checkout/abc"

        return _Result()

    def verify(self, payload, signature=None):
        class _Verification:
            is_valid = True
            provider_reference = payload.get("provider_reference")
            failure_reason = None

        return _Verification()

    def refund(self, payment: Payment, amount_cents: int | None = None):
        class _Verification:
            is_valid = True
            provider_reference = f"stitch-refund-{payment.id}"
            failure_reason = None

        return _Verification()


def test_story_8_1_and_8_2_initiate_payment_flow(
    client: TestClient, db: Session
) -> None:
    headers, consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "membership",
            "amount_cents": 49900,
            "description": "Premium membership",
            "return_url": "https://app.studioloop.test/payments/return",
            "cancel_url": "https://app.studioloop.test/payments/cancel",
            "webhook_url": "https://api.studioloop.test/payments/webhook",
            "provider": "ozow",
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "pending"
    assert body["provider"] == "ozow"
    assert "redirect_url" in body

    payment = db.get(Payment, body["payment_id"])
    assert payment is not None
    assert payment.consumer_id == consumer.id
    assert payment.status == PaymentStatus.PENDING


def test_story_8_3_webhook_processing_idempotent(
    client: TestClient, db: Session
) -> None:
    headers, _consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    init_res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "membership",
            "amount_cents": 29900,
            "description": "Membership payment",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "ozow",
        },
        headers=headers,
    )
    payment_id = init_res.json()["payment_id"]

    event_id = f"evt-{uuid4()}"
    signature = build_webhook_signature(event_id, UUID(payment_id), "completed")
    payload = {
        "event_id": event_id,
        "payment_id": payment_id,
        "status": "completed",
        "provider_reference": "provider-ok-1",
    }
    first = client.post(
        "/api/v1/payments/webhooks/ozow",
        json=payload,
        headers={"X-Signature": signature},
    )
    assert first.status_code == 200, first.text

    second = client.post(
        "/api/v1/payments/webhooks/ozow",
        json=payload,
        headers={"X-Signature": signature},
    )
    assert second.status_code == 200
    assert second.json()["status"] == "already_processed"


def test_story_8_4_dashboard_and_detail(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    consumer_headers, consumer = _consumer_headers(client, db)

    init = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 15000,
            "description": "Class booking",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
        },
        headers=consumer_headers,
    )
    payment_id = init.json()["payment_id"]

    dashboard = client.get(f"/api/v1/payments/gyms/{gym.id}", headers=staff_headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["items"]

    detail = client.get(
        f"/api/v1/payments/gyms/{gym.id}/{payment_id}", headers=staff_headers
    )
    assert detail.status_code == 200
    assert detail.json()["member_name"] == f"{consumer.first_name} {consumer.last_name}"


def test_story_8_5_failed_detection_updates_membership(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    consumer_headers, consumer = _consumer_headers(client, db)

    membership = GymMembership(
        gym_id=gym.id, consumer_id=consumer.id, status=GymMembershipStatus.ACTIVE
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    init = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "membership",
            "amount_cents": 9900,
            "description": "Membership renewal",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "related_entity_id": str(membership.id),
        },
        headers=consumer_headers,
    )
    payment_id = init.json()["payment_id"]

    event_id = f"evt-{uuid4()}"
    signature = build_webhook_signature(event_id, UUID(payment_id), "failed")
    failed = client.post(
        "/api/v1/payments/webhooks/ozow",
        json={
            "event_id": event_id,
            "payment_id": payment_id,
            "status": "failed",
            "failure_reason": "insufficient_funds",
        },
        headers={"X-Signature": signature},
    )
    assert failed.status_code == 200

    refreshed = db.get(GymMembership, membership.id)
    assert refreshed is not None
    db.refresh(refreshed)
    assert refreshed.status == GymMembershipStatus.INACTIVE

    items = client.get(
        f"/api/v1/payments/gyms/{gym.id}/failed/action-items", headers=staff_headers
    )
    assert items.status_code == 200
    assert any(i["payment_id"] == payment_id for i in items.json())


def test_story_8_6_retry_worker(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer_headers, _consumer = _consumer_headers(client, db)

    init = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "membership",
            "amount_cents": 19900,
            "description": "Retry me",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
        },
        headers=consumer_headers,
    )
    payment = db.get(Payment, init.json()["payment_id"])
    assert payment is not None
    payment.status = PaymentStatus.FAILED
    payment.next_retry_at = datetime.now(UTC) - timedelta(minutes=1)
    payment.extra_data = {"force_success_on_retry": True}
    db.add(payment)
    db.commit()

    run = client.post("/api/v1/payments/retries/run")
    assert run.status_code == 200
    assert str(payment.id) in {str(pid) for pid in run.json()["processed_payment_ids"]}

    updated = db.get(Payment, payment.id)
    assert updated is not None
    assert updated.status == PaymentStatus.COMPLETED


def test_story_8_7_8_8_8_9_reports_history_receipt(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    consumer_headers, _consumer = _consumer_headers(client, db)

    init = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 22000,
            "description": "Marketplace class booking",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
        },
        headers=consumer_headers,
    )
    payment_id = init.json()["payment_id"]

    payment = db.get(Payment, payment_id)
    assert payment is not None
    payment.status = PaymentStatus.COMPLETED
    payment.extra_data = {"class_name": "Sunrise Yoga"}
    payment.completed_at = datetime.now(UTC)
    db.add(payment)
    db.commit()

    report = client.get(
        f"/api/v1/payments/gyms/{gym.id}/reports/marketplace-payout",
        headers=staff_headers,
    )
    assert report.status_code == 200
    assert report.json()["gross_revenue_cents"] >= 22000

    history = client.get("/api/v1/payments/me/history", headers=consumer_headers)
    assert history.status_code == 200
    assert any(item["payment_id"] == payment_id for item in history.json()["items"])

    receipt = client.get(
        f"/api/v1/payments/me/{payment_id}/receipt", headers=consumer_headers
    )
    assert receipt.status_code == 200
    assert "VAT" in receipt.json()["rendered_text"]


def test_payments_denies_cross_tenant_dashboard_access(
    client: TestClient, db: Session
) -> None:
    gym_a = db.exec(select(Gym)).first()
    assert gym_a is not None

    gym_b = Gym(
        name=f"Payments Gym {uuid4().hex[:6]}",
        slug=f"payments-gym-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym_b)
    db.commit()
    db.refresh(gym_b)

    staff_headers = _staff_headers(client, db, gym_a, StaffRole.OWNER)

    response = client.get(f"/api/v1/payments/gyms/{gym_b.id}", headers=staff_headers)

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["code"] == "FORBIDDEN"
    assert "Access denied to this gym" in body["detail"]["message"]


def test_stitch_initiate_payment_and_get_status_endpoint(
    client: TestClient, db: Session, monkeypatch
) -> None:
    from app.api.routes import payments as payments_route

    monkeypatch.setattr(
        payments_route, "get_payment_provider", lambda _name: _MockStitchProvider()
    )

    headers, consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 12500,
            "description": "Stitch Pay By Bank",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "stitch",
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "stitch"
    assert body["provider_reference"] == "stitch-pir-123"

    status_res = client.get(f"/api/v1/payments/{body['payment_id']}", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["payment_id"] == body["payment_id"]

    payment = db.get(Payment, body["payment_id"])
    assert payment is not None
    assert payment.consumer_id == consumer.id


def test_stitch_webhook_endpoint_with_svix_headers(
    client: TestClient, db: Session, monkeypatch
) -> None:
    from app.api.routes import payments as payments_route

    class _RecordingProvider(_MockStitchProvider):
        captured_payload = None

        def verify(self, payload, signature=None):
            self.captured_payload = payload
            return super().verify(payload, signature)

    provider = _RecordingProvider()
    monkeypatch.setattr(payments_route, "get_payment_provider", lambda _name: provider)

    headers, _consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    init_res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 8000,
            "description": "Webhook target",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "stitch",
        },
        headers=headers,
    )
    payment_id = init_res.json()["payment_id"]

    payload = {
        "event_id": f"evt-{uuid4()}",
        "payment_id": payment_id,
        "status": "completed",
        "provider_reference": "stitch-pir-123",
    }
    webhook = client.post(
        "/api/v1/payments/webhook",
        json=payload,
        headers={
            "svix-id": "msg_123",
            "svix-timestamp": "1700000000",
            "svix-signature": "v1,abc",
        },
    )
    assert webhook.status_code == 200, webhook.text
    assert webhook.json()["status"] == "processed"
    assert provider.captured_payload is not None
    assert provider.captured_payload.get("_svix_id") == "msg_123"
    assert provider.captured_payload.get("_svix_signature") == "v1,abc"
    assert provider.captured_payload.get("_raw_body")
    assert payload["event_id"] in str(provider.captured_payload.get("_raw_body"))


def test_stitch_webhook_rejects_invalid_svix_signature(
    client: TestClient, db: Session, monkeypatch
) -> None:
    from app.api.routes import payments as payments_route

    headers, _consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    init_res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 8000,
            "description": "Webhook signature negative",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "ozow",
        },
        headers=headers,
    )
    payment_id = init_res.json()["payment_id"]

    payload = {
        "event_id": f"evt-{uuid4()}",
        "payment_id": payment_id,
        "status": "completed",
        "provider_reference": "stitch-pir-123",
    }
    body = json.dumps(payload, separators=(",", ":"))

    monkeypatch.setattr(
        payments_route.settings, "STITCH_WEBHOOK_SECRET", "whsec_dGVzdHNlY3JldA=="
    )

    webhook = client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={
            "content-type": "application/json",
            "svix-id": "msg_123",
            "svix-timestamp": str(int(datetime.now(UTC).timestamp())),
            "svix-signature": "v1,invalidsig",
        },
    )
    assert webhook.status_code == 400
    assert webhook.json()["detail"] == "Invalid webhook signature"


def test_stitch_webhook_valid_svix_signature_is_idempotent(
    client: TestClient, db: Session, monkeypatch
) -> None:
    from app.api.routes import payments as payments_route

    headers, _consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    init_res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 8000,
            "description": "Webhook signature positive",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "ozow",
        },
        headers=headers,
    )
    payment_id = init_res.json()["payment_id"]

    monkeypatch.setattr(
        payments_route.settings, "STITCH_WEBHOOK_SECRET", "whsec_dGVzdHNlY3JldA=="
    )

    payload = {
        "event_id": f"evt-{uuid4()}",
        "payment_id": payment_id,
        "status": "completed",
        "provider_reference": "stitch-pir-123",
    }
    body = json.dumps(payload, separators=(",", ":"))
    svix_id = "msg_123"
    svix_timestamp = str(int(datetime.now(UTC).timestamp()))
    signed = f"{svix_id}.{svix_timestamp}.{body}"
    signature = base64.b64encode(
        hmac.new(
            base64.b64decode("dGVzdHNlY3JldA=="), signed.encode(), hashlib.sha256
        ).digest()
    ).decode()

    first = client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={
            "content-type": "application/json",
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": f"v1,{signature}",
        },
    )
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "processed"

    second = client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={
            "content-type": "application/json",
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": f"v1,{signature}",
        },
    )
    assert second.status_code == 200
    assert second.json()["status"] == "already_processed"


def test_stitch_sandbox_callback_signature_is_accepted(
    client: TestClient, db: Session, monkeypatch
) -> None:
    """Validate signature handling against a Stitch sandbox-style callback."""
    from app.api.routes import payments as payments_route

    headers, _consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    init_res = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 8000,
            "description": "Sandbox callback verification",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "ozow",
        },
        headers=headers,
    )
    payment_id = init_res.json()["payment_id"]

    monkeypatch.setattr(
        payments_route.settings, "STITCH_WEBHOOK_SECRET", "whsec_dGVzdHNlY3JldA=="
    )

    payload = {
        "event_id": f"evt-{uuid4()}",
        "event_type": "payment.completed",
        "payment_id": payment_id,
        "status": "completed",
        "provider_reference": "pir_sandbox_123",
    }
    body = json.dumps(payload, separators=(",", ":"))
    svix_id = "msg_sandbox_123"
    svix_timestamp = str(int(datetime.now(UTC).timestamp()))
    signed = f"{svix_id}.{svix_timestamp}.{body}"
    good_signature = base64.b64encode(
        hmac.new(
            base64.b64decode("dGVzdHNlY3JldA=="), signed.encode(), hashlib.sha256
        ).digest()
    ).decode()

    # Stitch/Svix can include multiple signatures in one header value.
    webhook = client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={
            "content-type": "application/json",
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": f"v1,invalidsig v1,{good_signature}",
        },
    )
    assert webhook.status_code == 200, webhook.text
    assert webhook.json()["status"] == "processed"


def test_stitch_subscription_endpoint_creates_membership_payment(
    client: TestClient, db: Session, monkeypatch
) -> None:
    from app.api.routes import payments as payments_route

    monkeypatch.setattr(
        payments_route, "get_payment_provider", lambda _name: _MockStitchProvider()
    )

    headers, _consumer = _consumer_headers(client, db)
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    res = client.post(
        "/api/v1/payments/subscriptions",
        json={
            "gym_id": str(gym.id),
            "amount_cents": 35900,
            "description": "VRP monthly membership",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "provider": "stitch",
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "stitch"

    payment = db.get(Payment, body["payment_id"])
    assert payment is not None
    assert payment.payment_type.value == "membership"
    assert payment.provider.value == "stitch"


def test_payments_root_list_endpoint_is_gym_scoped(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    ok = client.get(f"/api/v1/payments/?gym_id={gym.id}", headers=staff_headers)
    assert ok.status_code == 200, ok.text
    assert "summary" in ok.json()
    assert "items" in ok.json()


def test_webhook_completes_pending_booking(client: TestClient, db: Session) -> None:
    """Webhook COMPLETED event activates a PENDING_PAYMENT booking."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer_headers, consumer = _consumer_headers(client, db)

    space = Space(gym_id=gym.id, name=f"PayTest-{uuid4().hex[:6]}", capacity=20)
    db.add(space)
    db.commit()
    db.refresh(space)
    class_session = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        title="Payment Test Class",
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, hours=1),
        capacity=20,
        spots_booked=0,
        price_cents=15000,
    )
    db.add(class_session)
    db.commit()
    db.refresh(class_session)

    booking = Booking(
        gym_id=gym.id,
        consumer_id=consumer.id,
        session_id=class_session.id,
        booking_type="pay_per_class",
        status=BookingStatus.PENDING_PAYMENT,
        price_paid_cents=15000,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    init = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 15000,
            "description": "Class booking",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "related_entity_id": str(booking.id),
        },
        headers=consumer_headers,
    )
    payment_id = init.json()["payment_id"]

    event_id = f"evt-{uuid4()}"
    signature = build_webhook_signature(event_id, UUID(payment_id), "completed")
    res = client.post(
        "/api/v1/payments/webhooks/ozow",
        json={
            "event_id": event_id,
            "payment_id": payment_id,
            "status": "completed",
            "provider_reference": "ref-booking-ok",
        },
        headers={"X-Signature": signature},
    )
    assert res.status_code == 200

    db.refresh(booking)
    assert booking.status == BookingStatus.BOOKED


def test_webhook_fails_pending_booking_releases_spot(
    client: TestClient, db: Session
) -> None:
    """Webhook FAILED event cancels a PENDING_PAYMENT booking and releases the spot."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer_headers, consumer = _consumer_headers(client, db)

    space = Space(gym_id=gym.id, name=f"FailTest-{uuid4().hex[:6]}", capacity=20)
    db.add(space)
    db.commit()
    db.refresh(space)
    class_session = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        title="Fail Test Class",
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, hours=1),
        capacity=20,
        spots_booked=1,
        price_cents=15000,
    )
    db.add(class_session)
    db.commit()
    db.refresh(class_session)

    booking = Booking(
        gym_id=gym.id,
        consumer_id=consumer.id,
        session_id=class_session.id,
        booking_type="pay_per_class",
        status=BookingStatus.PENDING_PAYMENT,
        price_paid_cents=15000,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    init = client.post(
        "/api/v1/payments/initiate",
        json={
            "gym_id": str(gym.id),
            "payment_type": "class_booking",
            "amount_cents": 15000,
            "description": "Class booking",
            "return_url": "https://app.test/return",
            "cancel_url": "https://app.test/cancel",
            "webhook_url": "https://api.test/webhook",
            "related_entity_id": str(booking.id),
        },
        headers=consumer_headers,
    )
    payment_id = init.json()["payment_id"]

    event_id = f"evt-{uuid4()}"
    signature = build_webhook_signature(event_id, UUID(payment_id), "failed")
    res = client.post(
        "/api/v1/payments/webhooks/ozow",
        json={
            "event_id": event_id,
            "payment_id": payment_id,
            "status": "failed",
            "failure_reason": "declined",
        },
        headers={"X-Signature": signature},
    )
    assert res.status_code == 200

    db.refresh(booking)
    assert booking.status == BookingStatus.CANCELLED

    db.refresh(class_session)
    assert class_session.spots_booked == 0


def test_webhook_completes_pending_marketplace_subscription(
    client: TestClient, db: Session
) -> None:
    """Webhook COMPLETED event activates a PENDING_PAYMENT marketplace subscription."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer_headers, consumer = _consumer_headers(client, db)

    subscription = MarketplaceSubscription(
        consumer_id=consumer.id,
        plan_tier="twelve",
        classes_total=12,
        classes_remaining=12,
        status=MarketplaceSubscriptionStatus.PENDING_PAYMENT,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    # Create payment with gym_id=None (platform-level)
    payment = Payment(
        gym_id=None,
        consumer_id=consumer.id,
        amount_cents=99900,
        currency="ZAR",
        payment_type=PaymentType.MARKETPLACE_SUBSCRIPTION,
        status=PaymentStatus.PENDING,
        provider="ozow",
        description="Marketplace twelve plan",
        related_entity_id=subscription.id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    event_id = f"evt-{uuid4()}"
    signature = build_webhook_signature(event_id, payment.id, "completed")
    res = client.post(
        "/api/v1/payments/webhooks/ozow",
        json={
            "event_id": event_id,
            "payment_id": str(payment.id),
            "status": "completed",
            "provider_reference": "ref-sub-ok",
        },
        headers={"X-Signature": signature},
    )
    assert res.status_code == 200

    db.refresh(subscription)
    assert subscription.status == MarketplaceSubscriptionStatus.ACTIVE
