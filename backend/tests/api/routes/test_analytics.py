from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import (
    Booking,
    BookingStatus,
    CheckInRecord,
    ClassSession,
    Gym,
    GymMembership,
    GymMembershipStatus,
    GymMembershipTier,
    Payment,
    PaymentStatus,
    PaymentType,
    Space,
    Staff,
    StaffRole,
)
from tests.api.routes.test_staff_memberships import _consumer_headers, _staff_headers


def _seed_space_and_session(
    db: Session,
    gym: Gym,
    instructor_id: UUID | None = None,
    title: str = "Yoga Flow",
    capacity: int = 20,
) -> ClassSession:
    space = Space(gym_id=gym.id, name=f"Space-{uuid4().hex[:5]}", capacity=max(capacity, 1))
    db.add(space)
    db.commit()
    db.refresh(space)

    session = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        instructor_staff_id=instructor_id,
        title=title,
        start_time=datetime.now(UTC) - timedelta(hours=1),
        end_time=datetime.now(UTC) + timedelta(hours=1),
        capacity=capacity,
        spots_booked=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def test_story_10_1_revenue_report_and_csv_export(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _consumer_headers_data, consumer = _consumer_headers(client, db)

    now = datetime.now(UTC)
    payments = [
        Payment(gym_id=gym.id, consumer_id=consumer.id, amount_cents=50000, payment_type=PaymentType.MEMBERSHIP, status=PaymentStatus.COMPLETED, description="Membership", completed_at=now),
        Payment(gym_id=gym.id, consumer_id=consumer.id, amount_cents=15000, payment_type=PaymentType.CLASS_BOOKING, status=PaymentStatus.COMPLETED, description="Class", completed_at=now),
        Payment(gym_id=gym.id, consumer_id=consumer.id, amount_cents=25000, payment_type=PaymentType.MARKETPLACE_SUBSCRIPTION, status=PaymentStatus.COMPLETED, description="Marketplace", completed_at=now),
    ]
    db.add_all(payments)
    db.commit()

    res = client.get(f"/api/v1/analytics/gyms/{gym.id}/revenue?period=monthly", headers=staff_headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total_revenue_cents"] >= 90000
    assert body["source_breakdown"]["memberships_cents"] >= 50000
    assert "growth_percent" in body

    csv_res = client.get(f"/api/v1/analytics/gyms/{gym.id}/revenue?period=monthly&export=csv", headers=staff_headers)
    assert csv_res.status_code == 200
    assert "date,revenue_cents" in csv_res.text


def test_story_10_2_attendance_report(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _consumer_headers_data, consumer = _consumer_headers(client, db)

    membership = GymMembership(gym_id=gym.id, consumer_id=consumer.id, membership_tier=GymMembershipTier.PREMIUM, status=GymMembershipStatus.ACTIVE)
    db.add(membership)

    record1 = CheckInRecord(gym_id=gym.id, consumer_id=consumer.id, checked_in_at=datetime.now(UTC) - timedelta(days=1))
    record2 = CheckInRecord(gym_id=gym.id, consumer_id=consumer.id, checked_in_at=datetime.now(UTC) - timedelta(hours=3))
    db.add(record1)
    db.add(record2)
    db.commit()

    res = client.get(f"/api/v1/analytics/gyms/{gym.id}/attendance?period=weekly&membership_tier=premium", headers=staff_headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total_check_ins"] >= 2
    assert body["average_daily_attendance"] >= 0
    assert "peak_hour" in body


def test_story_10_3_membership_health_report(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _headers_1, consumer_1 = _consumer_headers(client, db)
    _headers_2, consumer_2 = _consumer_headers(client, db)

    active = GymMembership(gym_id=gym.id, consumer_id=consumer_1.id, status=GymMembershipStatus.ACTIVE, started_at=datetime.now(UTC) - timedelta(days=3), membership_tier=GymMembershipTier.BASIC)
    cancelled = GymMembership(gym_id=gym.id, consumer_id=consumer_2.id, status=GymMembershipStatus.CANCELLED, started_at=datetime.now(UTC) - timedelta(days=30), ended_at=datetime.now(UTC) - timedelta(hours=1), membership_tier=GymMembershipTier.PREMIUM)
    db.add(active)
    db.add(cancelled)
    db.commit()

    res = client.get(f"/api/v1/analytics/gyms/{gym.id}/membership-health?period=monthly", headers=staff_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_active_members"] >= 1
    assert body["cancelled_this_period"] >= 1
    assert body["retention_rate_percent"] <= 100


def test_story_10_4_class_performance_report(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    staff_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _consumer_headers_data, consumer = _consumer_headers(client, db)

    session = _seed_space_and_session(db, gym, title="Morning Yoga", capacity=10)
    booking1 = Booking(gym_id=gym.id, consumer_id=consumer.id, session_id=session.id, status=BookingStatus.CHECKED_IN)
    booking2 = Booking(gym_id=gym.id, consumer_id=consumer.id, session_id=session.id, status=BookingStatus.BOOKED)
    db.add(booking1)
    db.add(booking2)
    db.commit()

    res = client.get(f"/api/v1/analytics/gyms/{gym.id}/class-performance?period=monthly&class_type=yoga", headers=staff_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["items"]
    assert "popular_classes" in body


def test_story_10_5_staff_performance_report(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _consumer_headers_data, consumer = _consumer_headers(client, db)

    instructor = Staff(
        gym_id=gym.id,
        email=f"inst-{uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        first_name="Inst",
        last_name="Ructor",
        role=StaffRole.INSTRUCTOR,
        is_email_verified=True,
        hourly_rate_cents=25000,
    )
    db.add(instructor)
    db.commit()
    db.refresh(instructor)

    session = _seed_space_and_session(db, gym, instructor_id=instructor.id, title="Spin", capacity=8)
    booking = Booking(gym_id=gym.id, consumer_id=consumer.id, session_id=session.id, status=BookingStatus.CHECKED_IN)
    db.add(booking)
    db.commit()

    res = client.get(f"/api/v1/analytics/gyms/{gym.id}/staff-performance?period=monthly&role=instructor", headers=owner_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body) >= 1
    instructor_row = next((row for row in body if row["staff_id"] == str(instructor.id)), None)
    assert instructor_row is not None
    assert instructor_row["classes_taught"] >= 1


def test_story_10_6_consumer_class_history(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer_headers, consumer = _consumer_headers(client, db)

    session = _seed_space_and_session(db, gym, title="Pilates")
    booking = Booking(
        gym_id=gym.id,
        consumer_id=consumer.id,
        session_id=session.id,
        status=BookingStatus.CHECKED_IN,
        checked_in_at=datetime.now(UTC) - timedelta(days=1),
    )
    db.add(booking)
    db.commit()

    res = client.get(f"/api/v1/analytics/me/class-history?gym_id={gym.id}&class_type=pilates", headers=consumer_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) >= 1
    assert body["total_attended_this_year"] >= 1


def test_story_10_7_consumer_stats_dashboard(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    consumer_headers, consumer = _consumer_headers(client, db)

    yoga = _seed_space_and_session(db, gym, title="Yoga")
    boxing = _seed_space_and_session(db, gym, title="Boxing")
    b1 = Booking(gym_id=gym.id, consumer_id=consumer.id, session_id=yoga.id, status=BookingStatus.CHECKED_IN, checked_in_at=datetime.now(UTC) - timedelta(days=7))
    b2 = Booking(gym_id=gym.id, consumer_id=consumer.id, session_id=yoga.id, status=BookingStatus.CHECKED_IN, checked_in_at=datetime.now(UTC) - timedelta(days=1))
    b3 = Booking(gym_id=gym.id, consumer_id=consumer.id, session_id=boxing.id, status=BookingStatus.CHECKED_IN, checked_in_at=datetime.now(UTC) - timedelta(days=14))
    db.add_all([b1, b2, b3])
    db.commit()

    res = client.get("/api/v1/analytics/me/stats", headers=consumer_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_classes_all_time"] >= 3
    assert body["favorite_class_type"] == "Yoga"
    assert body["average_classes_per_week"] > 0


def test_story_10_8_at_risk_detection_and_list(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _h1, c1 = _consumer_headers(client, db)
    _h2, c2 = _consumer_headers(client, db)

    m1 = GymMembership(gym_id=gym.id, consumer_id=c1.id, status=GymMembershipStatus.ACTIVE)
    m2 = GymMembership(gym_id=gym.id, consumer_id=c2.id, status=GymMembershipStatus.ACTIVE)
    db.add_all([m1, m2])
    db.commit()

    stale_check_in = CheckInRecord(gym_id=gym.id, consumer_id=c1.id, checked_in_at=datetime.now(UTC) - timedelta(days=20))
    recent_prev = CheckInRecord(gym_id=gym.id, consumer_id=c2.id, checked_in_at=datetime.now(UTC) - timedelta(days=40))
    db.add_all([stale_check_in, recent_prev])
    db.commit()

    run = client.post(f"/api/v1/analytics/gyms/{gym.id}/at-risk-members/run?inactivity_days=14&drop_percent=50", headers=owner_headers)
    assert run.status_code == 200
    assert run.json()["evaluated_members"] >= 2

    listed = client.get(f"/api/v1/analytics/gyms/{gym.id}/at-risk-members?inactivity_days=14&drop_percent=50", headers=owner_headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


def test_story_10_9_gym_owner_dashboard(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    owner_headers = _staff_headers(client, db, gym, StaffRole.OWNER)
    _consumer_headers_data, consumer = _consumer_headers(client, db)

    payment = Payment(
        gym_id=gym.id,
        consumer_id=consumer.id,
        amount_cents=10000,
        payment_type=PaymentType.MEMBERSHIP,
        status=PaymentStatus.FAILED,
        description="Failed renewal",
    )
    db.add(payment)

    membership = GymMembership(
        gym_id=gym.id,
        consumer_id=consumer.id,
        status=GymMembershipStatus.ACTIVE,
        ended_at=datetime.now(UTC) + timedelta(days=7),
    )
    db.add(membership)

    session = _seed_space_and_session(db, gym, title="Quiet class", capacity=10)
    session.spots_booked = 2
    db.add(session)

    check_in = CheckInRecord(gym_id=gym.id, consumer_id=consumer.id, checked_in_at=datetime.now(UTC) - timedelta(days=30))
    db.add(check_in)
    db.commit()

    res = client.get(f"/api/v1/analytics/gyms/{gym.id}/dashboard", headers=owner_headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["action_items"]["failed_payments"] >= 1
    assert "today_summary" in body
    assert "quick_metrics" in body


def test_analytics_denies_cross_tenant_dashboard_access(client: TestClient, db: Session) -> None:
    gym_a = db.exec(select(Gym)).first()
    assert gym_a is not None

    gym_b = Gym(
        name=f"Tenant Gym {uuid4().hex[:6]}",
        slug=f"tenant-gym-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym_b)
    db.commit()
    db.refresh(gym_b)

    owner_headers = _staff_headers(client, db, gym_a, StaffRole.OWNER)

    res = client.get(
        f"/api/v1/analytics/gyms/{gym_b.id}/dashboard",
        headers=owner_headers,
    )

    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "FORBIDDEN"
    assert "Access denied to this gym" in res.json()["detail"]["message"]


def test_analytics_denies_cross_tenant_revenue_access(client: TestClient, db: Session) -> None:
    gym_a = db.exec(select(Gym)).first()
    assert gym_a is not None

    gym_b = Gym(
        name=f"Revenue Gym {uuid4().hex[:6]}",
        slug=f"revenue-gym-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym_b)
    db.commit()
    db.refresh(gym_b)

    owner_headers = _staff_headers(client, db, gym_a, StaffRole.OWNER)

    res = client.get(
        f"/api/v1/analytics/gyms/{gym_b.id}/revenue?period=monthly",
        headers=owner_headers,
    )

    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "FORBIDDEN"
