from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Consumer, Gym, Staff, StaffRole


def _staff_headers(client: TestClient, db: Session, gym: Gym, role: StaffRole) -> dict[str, str]:
    password = "S3curePass!123"
    staff = Staff(
        gym_id=gym.id,
        email=f"{role.value}-{uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash(password),
        first_name="Test",
        last_name="Staff",
        role=role,
        is_email_verified=True,
        is_active=True,
    )
    db.add(staff)
    db.commit()
    res = client.post(f"{settings.API_V1_STR}/auth/staff/login", json={"email": staff.email, "password": password})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _consumer_headers(client: TestClient, db: Session) -> tuple[dict[str, str], Consumer]:
    password = "S3curePass!123"
    consumer = Consumer(
        email=f"consumer-{uuid4().hex[:8]}@example.com",
        first_name="Con",
        last_name="Sumer",
        hashed_password=get_password_hash(password),
        is_email_verified=True,
        is_active=True,
    )
    db.add(consumer)
    db.commit()
    res = client.post(f"{settings.API_V1_STR}/auth/consumer/login", json={"email": consumer.email, "password": password})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}, consumer


def test_add_staff_member_and_pending_status(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    payload = {
        "email": f"new-{uuid4().hex[:6]}@example.com",
        "first_name": "Naledi",
        "last_name": "Sithole",
        "phone": "+27825551234",
        "role": "instructor",
    }
    res = client.post("/api/v1/gyms/me/staff", json=payload, headers=headers)
    assert res.status_code == 201
    assert res.json()["invitation_status"] == "pending"


def test_staff_role_assignment_owner_only_for_manager(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    manager_headers = _staff_headers(client, db, gym, StaffRole.MANAGER)

    created = client.post(
        "/api/v1/gyms/me/staff",
        json={"email": f"staff-{uuid4().hex[:6]}@example.com", "first_name": "A", "last_name": "B", "role": "front_desk"},
        headers=owner_headers,
    )
    staff_id = created.json()["id"]

    forbidden = client.patch(f"/api/v1/gyms/me/staff/{staff_id}/role", json={"role": "manager"}, headers=manager_headers)
    assert forbidden.status_code == 403


def test_configure_working_hours_and_pay_rate(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    staff_res = client.post(
        "/api/v1/gyms/me/staff",
        json={"email": f"inst-{uuid4().hex[:6]}@example.com", "first_name": "I", "last_name": "N", "role": "instructor"},
        headers=headers,
    )
    staff_id = staff_res.json()["id"]

    hours = {
        "working_hours": {
            "monday": {"is_closed": False, "open_time": "08:00", "close_time": "17:00"}
        }
    }
    hours_res = client.patch(f"/api/v1/gyms/me/staff/{staff_id}/working_hours", json=hours, headers=headers)
    assert hours_res.status_code == 200
    assert "monday" in hours_res.json()["working_hours"]

    pay_res = client.patch(f"/api/v1/gyms/me/staff/{staff_id}/pay_rate", json={"hourly_rate_cents": 35000}, headers=headers)
    assert pay_res.status_code == 200
    assert pay_res.json()["hourly_rate_cents"] == 35000


def test_instructor_schedule_and_earnings(client: TestClient, db: Session) -> None:
    from app.models import ClassSession

    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    instructor_resp = client.post(
        "/api/v1/gyms/me/staff",
        json={"email": f"inst2-{uuid4().hex[:6]}@example.com", "first_name": "I", "last_name": "N", "role": "instructor"},
        headers=owner_headers,
    )
    inst_id = instructor_resp.json()["id"]
    client.patch(f"/api/v1/gyms/me/staff/{inst_id}/pay_rate", json={"hourly_rate_cents": 20000}, headers=owner_headers)

    instructor = db.get(Staff, inst_id)
    assert instructor is not None
    instructor_password = "TeachPass123!"
    instructor.hashed_password = get_password_hash(instructor_password)
    instructor.is_email_verified = True
    instructor.invitation_status = "accepted"
    db.add(instructor)

    from app.models import Space

    space = Space(gym_id=gym.id, name="Studio A", capacity=20)
    db.add(space)
    db.commit()
    db.refresh(space)

    session = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        instructor_staff_id=instructor.id,
        title="Morning Yoga",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(session)
    db.commit()

    login = client.post(f"{settings.API_V1_STR}/auth/staff/login", json={"email": instructor.email, "password": instructor_password})
    assert login.status_code == 200
    inst_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    schedule = client.get("/api/v1/gyms/me/instructor/schedule", headers=inst_headers)
    assert schedule.status_code == 200
    assert len(schedule.json()) >= 1

    earnings = client.get("/api/v1/gyms/me/instructor/earnings", headers=inst_headers)
    assert earnings.status_code == 200
    assert earnings.json()["estimated_earnings_cents"] >= 20000


def test_membership_plan_enroll_change_and_waiver(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    create_plan = client.post(
        "/api/v1/gyms/me/membership_plans",
        json={"name": "Premium", "description": "Premium plan", "price_cents": 89900, "billing_cycle": "monthly"},
        headers=owner_headers,
    )
    assert create_plan.status_code == 201
    plan_id = create_plan.json()["id"]

    benefits = client.patch(f"/api/v1/gyms/me/membership_plans/{plan_id}/benefits", json={"benefits": ["sauna", "pool"]}, headers=owner_headers)
    assert benefits.status_code == 200

    rules = client.patch(
        f"/api/v1/gyms/me/membership_plans/{plan_id}/rules",
        json={"rules": {"freeze_allowed": True}, "usage_limits": {"classes_per_week": 7}},
        headers=owner_headers,
    )
    assert rules.status_code == 200

    consumer_headers, _ = _consumer_headers(client, db)

    enroll = client.post("/api/v1/gyms/consumer/memberships", json={"gym_id": str(gym.id), "membership_plan_id": plan_id, "payment_method_last4": "4242"}, headers=consumer_headers)
    assert enroll.status_code == 201
    membership_id = enroll.json()["id"]

    list_m = client.get("/api/v1/gyms/consumer/memberships", headers=consumer_headers)
    assert list_m.status_code == 200
    assert len(list_m.json()) >= 1

    benefits_view = client.get(f"/api/v1/gyms/consumer/memberships/{membership_id}/benefits", headers=consumer_headers)
    assert benefits_view.status_code == 200
    assert "sauna" in benefits_view.json()["benefits"]

    change = client.post(
        f"/api/v1/gyms/consumer/memberships/{membership_id}/change",
        json={"membership_plan_id": plan_id},
        headers=consumer_headers,
    )
    assert change.status_code == 200

    waiver = client.post(
        "/api/v1/gyms/consumer/memberships/waiver_acceptance",
        json={"gym_membership_id": membership_id, "waiver_version": "v1"},
        headers=consumer_headers,
    )
    assert waiver.status_code == 201


def test_gym_member_list_and_detail(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    plan = client.post(
        "/api/v1/gyms/me/membership_plans",
        json={"name": "Basic", "description": "Basic plan", "price_cents": 49900, "billing_cycle": "monthly"},
        headers=owner_headers,
    ).json()

    consumer_headers, _ = _consumer_headers(client, db)
    membership = client.post(
        "/api/v1/gyms/consumer/memberships",
        json={"gym_id": str(gym.id), "membership_plan_id": plan["id"], "payment_method_last4": "1111"},
        headers=consumer_headers,
    ).json()

    list_resp = client.get("/api/v1/gyms/me/members", headers=owner_headers)
    assert list_resp.status_code == 200
    assert any(row["membership_id"] == membership["id"] for row in list_resp.json())

    detail = client.get(f"/api/v1/gyms/me/members/{membership['id']}", headers=owner_headers)
    assert detail.status_code == 200
    assert detail.json()["membership"]["id"] == membership["id"]
