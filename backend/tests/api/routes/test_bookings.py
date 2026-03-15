from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import ClassSession, Gym, Space, StaffRole
from app.models.digital_waiver import DigitalWaiverAcceptance
from tests.api.routes.test_staff_memberships import _consumer_headers, _staff_headers


def _create_session(db: Session, gym: Gym) -> ClassSession:
    space = Space(gym_id=gym.id, name=f"Studio-{uuid4().hex[:6]}", capacity=20)
    db.add(space)
    db.commit()
    db.refresh(space)

    cs = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        title="Epic6 Class",
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
        capacity=1,
        spots_booked=0,
        waitlist_enabled=True,
        price_cents=12000,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def test_membership_booking_cancel_waitlist_flow(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    plan = client.post(
        "/api/v1/gyms/me/membership_plans",
        json={"name": "Epic6Plan", "description": "P", "price_cents": 30000, "billing_cycle": "monthly"},
        headers=owner_headers,
    ).json()

    c1_headers, c1 = _consumer_headers(client, db)
    c2_headers, c2 = _consumer_headers(client, db)

    m1 = client.post(
        "/api/v1/gyms/consumer/memberships",
        json={"gym_id": str(gym.id), "membership_plan_id": plan["id"], "payment_method_last4": "1111"},
        headers=c1_headers,
    ).json()
    m2 = client.post(
        "/api/v1/gyms/consumer/memberships",
        json={"gym_id": str(gym.id), "membership_plan_id": plan["id"], "payment_method_last4": "2222"},
        headers=c2_headers,
    ).json()

    for consumer, membership in [(c1, m1), (c2, m2)]:
        db.add(
            DigitalWaiverAcceptance(
                gym_id=gym.id,
                consumer_id=consumer.id,
                gym_membership_id=membership["id"],
                waiver_version="v1",
            )
        )
    db.commit()

    class_session = _create_session(db, gym)

    b1 = client.post(
        "/api/v1/gyms/consumer/bookings/membership",
        json={"gym_id": str(gym.id), "session_id": str(class_session.id), "source": "direct"},
        headers=c1_headers,
    )
    assert b1.status_code == 200

    wl = client.post(
        "/api/v1/gyms/consumer/waitlist",
        json={"gym_id": str(gym.id), "session_id": str(class_session.id)},
        headers=c2_headers,
    )
    assert wl.status_code == 200

    cancelled = client.post(f"/api/v1/gyms/consumer/bookings/{b1.json()['id']}/cancel", headers=c1_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    offered = client.get("/api/v1/gyms/me/check_ins/search", params={"q": c2.first_name[:2]}, headers=owner_headers)
    assert offered.status_code == 200

    accept = client.post(f"/api/v1/gyms/consumer/waitlist/{wl.json()['id']}/accept", headers=c2_headers)
    assert accept.status_code in (200, 400)


def test_list_consumer_bookings(client: TestClient, db: Session) -> None:
    """Test GET /consumer/bookings — list, pagination, status filtering."""
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    c_headers, _ = _consumer_headers(client, db)
    session1 = _create_session(db, gym)

    # Create a pay-per-class booking (no membership needed)
    b1 = client.post(
        "/api/v1/gyms/consumer/bookings/pay_per_class",
        json={
            "gym_id": str(gym.id),
            "session_id": str(session1.id),
            "amount_cents": 12000,
        },
        headers=c_headers,
    )
    assert b1.status_code == 200
    booking_id = b1.json()["id"]

    # List bookings — should include the new booking
    res = client.get(
        "/api/v1/gyms/consumer/bookings",
        headers=c_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    ids = [item["id"] for item in data["items"]]
    assert booking_id in ids

    # Filter by status=booked — should include it
    res_booked = client.get(
        "/api/v1/gyms/consumer/bookings",
        params={"status": "booked"},
        headers=c_headers,
    )
    assert res_booked.status_code == 200
    booked_ids = [item["id"] for item in res_booked.json()["items"]]
    assert booking_id in booked_ids

    # Filter by status=cancelled — should not include it
    res_cancelled = client.get(
        "/api/v1/gyms/consumer/bookings",
        params={"status": "cancelled"},
        headers=c_headers,
    )
    assert res_cancelled.status_code == 200
    cancelled_ids = [item["id"] for item in res_cancelled.json()["items"]]
    assert booking_id not in cancelled_ids

    # Verify response shape
    item = next(i for i in res_booked.json()["items"] if i["id"] == booking_id)
    assert item["status"] == "booked"
    assert item["booking_type"] == "pay_per_class"
    assert item["class_name"] == "Epic6 Class"
    assert item["price_paid_cents"] == 12000
    assert "start_time" in item
    assert "end_time" in item
    assert "gym_name" in item

    # Test pagination — limit=1
    res_page = client.get(
        "/api/v1/gyms/consumer/bookings",
        params={"limit": 1},
        headers=c_headers,
    )
    assert res_page.status_code == 200
    assert len(res_page.json()["items"]) <= 1

    # Cancel and verify it moves to cancelled status
    cancel_res = client.post(
        f"/api/v1/gyms/consumer/bookings/{booking_id}/cancel",
        headers=c_headers,
    )
    assert cancel_res.status_code == 200

    res_after_cancel = client.get(
        "/api/v1/gyms/consumer/bookings",
        params={"status": "cancelled"},
        headers=c_headers,
    )
    assert res_after_cancel.status_code == 200
    cancelled_ids_after = [item["id"] for item in res_after_cancel.json()["items"]]
    assert booking_id in cancelled_ids_after


def test_pay_per_class_and_source_tracking(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    c_headers, _ = _consumer_headers(client, db)
    class_session = _create_session(db, gym)

    res = client.post(
        "/api/v1/gyms/consumer/bookings/pay_per_class",
        json={
            "gym_id": str(gym.id),
            "session_id": str(class_session.id),
            "amount_cents": 12000,
            "source": "marketplace",
        },
        headers=c_headers,
    )
    assert res.status_code == 200
    assert res.json()["booking_type"] == "pay_per_class"
    assert res.json()["source"] == "marketplace"


def test_qr_and_manual_check_in(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    c_headers, consumer = _consumer_headers(client, db)

    plan = client.post(
        "/api/v1/gyms/me/membership_plans",
        json={"name": "CheckInPlan", "description": "P", "price_cents": 30000, "billing_cycle": "monthly"},
        headers=owner_headers,
    ).json()
    membership = client.post(
        "/api/v1/gyms/consumer/memberships",
        json={"gym_id": str(gym.id), "membership_plan_id": plan["id"], "payment_method_last4": "4444"},
        headers=c_headers,
    ).json()
    db.add(
        DigitalWaiverAcceptance(
            gym_id=gym.id,
            consumer_id=consumer.id,
            gym_membership_id=membership["id"],
            waiver_version="v1",
        )
    )
    db.commit()

    qr = client.get("/api/v1/gyms/consumer/qr_code", headers=c_headers)
    assert qr.status_code == 200
    assert qr.json()["token"]

    scan = client.post("/api/v1/gyms/me/check_ins/scan_qr", json={"token": qr.json()["token"]}, headers=owner_headers)
    assert scan.status_code == 200
    assert scan.json()["source"] == "qr"

    manual = client.post(
        "/api/v1/gyms/me/check_ins/manual",
        json={"consumer_id": str(consumer.id)},
        headers=owner_headers,
    )
    assert manual.status_code == 200


def test_offline_check_in_sync(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    c_headers, consumer = _consumer_headers(client, db)

    plan = client.post(
        "/api/v1/gyms/me/membership_plans",
        json={"name": "OfflinePlan", "description": "P", "price_cents": 30000, "billing_cycle": "monthly"},
        headers=owner_headers,
    ).json()
    membership = client.post(
        "/api/v1/gyms/consumer/memberships",
        json={"gym_id": str(gym.id), "membership_plan_id": plan["id"], "payment_method_last4": "5555"},
        headers=c_headers,
    ).json()
    db.add(
        DigitalWaiverAcceptance(
            gym_id=gym.id,
            consumer_id=consumer.id,
            gym_membership_id=membership["id"],
            waiver_version="v1",
        )
    )
    db.commit()

    res = client.post(
        "/api/v1/gyms/me/check_ins/offline_sync",
        json={
            "records": [
                {
                    "consumer_id": str(consumer.id),
                    "offline_recorded_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        },
        headers=owner_headers,
    )
    assert res.status_code == 200
    assert res.json()["synced"] == 1
