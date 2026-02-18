from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import (
    Gym,
    GymMembership,
    GymMembershipStatus,
    Payment,
    PaymentStatus,
    StaffRole,
)
from app.services.payments.providers import build_webhook_signature
from tests.api.routes.test_staff_memberships import _consumer_headers, _staff_headers


def test_story_8_1_and_8_2_initiate_payment_flow(client: TestClient, db: Session) -> None:
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


def test_story_8_3_webhook_processing_idempotent(client: TestClient, db: Session) -> None:
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
    first = client.post("/api/v1/payments/webhooks/ozow", json=payload, headers={"X-Signature": signature})
    assert first.status_code == 200, first.text

    second = client.post("/api/v1/payments/webhooks/ozow", json=payload, headers={"X-Signature": signature})
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

    detail = client.get(f"/api/v1/payments/gyms/{gym.id}/{payment_id}", headers=staff_headers)
    assert detail.status_code == 200
    assert detail.json()["member_name"] == f"{consumer.first_name} {consumer.last_name}"


def test_story_8_5_failed_detection_updates_membership(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    consumer_headers, consumer = _consumer_headers(client, db)

    membership = GymMembership(gym_id=gym.id, consumer_id=consumer.id, status=GymMembershipStatus.ACTIVE)
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

    items = client.get(f"/api/v1/payments/gyms/{gym.id}/failed/action-items", headers=staff_headers)
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


def test_story_8_7_8_8_8_9_reports_history_receipt(client: TestClient, db: Session) -> None:
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

    report = client.get(f"/api/v1/payments/gyms/{gym.id}/reports/marketplace-payout", headers=staff_headers)
    assert report.status_code == 200
    assert report.json()["gross_revenue_cents"] >= 22000

    history = client.get("/api/v1/payments/me/history", headers=consumer_headers)
    assert history.status_code == 200
    assert any(item["payment_id"] == payment_id for item in history.json()["items"])

    receipt = client.get(f"/api/v1/payments/me/{payment_id}/receipt", headers=consumer_headers)
    assert receipt.status_code == 200
    assert "VAT" in receipt.json()["rendered_text"]
