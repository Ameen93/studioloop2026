"""Tests for class scheduling endpoints (Epic 5)."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import ClassSession, ClassTemplate, Gym, Space, Staff, StaffRole

API = f"{settings.API_V1_STR}/gyms/me"


def _staff_token_headers(
    client: TestClient,
    db: Session,
    gym: Gym,
    role: StaffRole = StaffRole.OWNER,
) -> tuple[dict[str, str], Staff]:
    email = f"{role.value}-{uuid4().hex[:8]}@example.com"
    password = "S3curePass!123"
    staff = Staff(
        gym_id=gym.id,
        email=email,
        hashed_password=get_password_hash(password),
        first_name="Test",
        last_name="Staff",
        role=role,
        is_active=True,
        is_email_verified=True,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/staff/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, staff


def _get_gym_and_space(db: Session) -> tuple[Gym, Space]:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    # Use a dedicated test space to avoid collisions with seeded class sessions.
    space = Space(
        gym_id=gym.id,
        name=f"Test Space {uuid4().hex[:8]}",
        capacity=40,
        is_active=True,
    )
    db.add(space)
    db.commit()
    db.refresh(space)
    return gym, space


def _future_time(hours: int = 48) -> tuple[str, str]:
    start = datetime.now(timezone.utc) + timedelta(hours=hours)
    end = start + timedelta(minutes=60)
    return start.isoformat(), end.isoformat()


# =========================================================================
# ClassTemplate CRUD
# =========================================================================


def test_create_class_template(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    payload = {
        "name": "Test Yoga Flow",
        "class_type": "yoga",
        "default_duration_minutes": 60,
        "default_capacity": 25,
        "default_price_cents": 5000,
        "color": "#10B981",
        "default_space_id": str(space.id),
    }

    response = client.post(f"{API}/class_templates", json=payload, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Test Yoga Flow"
    assert body["class_type"] == "yoga"
    assert body["color"] == "#10B981"
    assert body["default_space_id"] == str(space.id)


def test_list_class_templates(client: TestClient, db: Session) -> None:
    gym, _ = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.INSTRUCTOR)

    response = client.get(f"{API}/class_templates", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_class_template(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.MANAGER)

    # Create first
    create_resp = client.post(
        f"{API}/class_templates",
        json={"name": "Update Me", "class_type": "hiit", "color": "#EF4444"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    template_id = create_resp.json()["id"]

    # Update
    update_resp = client.patch(
        f"{API}/class_templates/{template_id}",
        json={"name": "Updated HIIT", "default_capacity": 30},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated HIIT"
    assert update_resp.json()["default_capacity"] == 30


def test_delete_class_template(client: TestClient, db: Session) -> None:
    gym, _ = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    create_resp = client.post(
        f"{API}/class_templates",
        json={"name": "Delete Me", "color": "#000000"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    template_id = create_resp.json()["id"]

    del_resp = client.delete(
        f"{API}/class_templates/{template_id}", headers=headers
    )
    assert del_resp.status_code == 204

    # Should not appear in list anymore
    get_resp = client.get(
        f"{API}/class_templates/{template_id}", headers=headers
    )
    assert get_resp.status_code == 404


# =========================================================================
# Enhanced class session creation
# =========================================================================


def test_create_class_session_with_new_fields(
    client: TestClient, db: Session
) -> None:
    gym, space = _get_gym_and_space(db)
    headers, staff = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    # Pick a future slot that is not already occupied in this seeded DB.
    start_dt = datetime.now(timezone.utc) + timedelta(days=60)
    start_dt = start_dt.replace(hour=3, minute=0, second=0, microsecond=0)
    for _ in range(30):
        end_dt = start_dt + timedelta(minutes=60)
        conflict = db.exec(
            select(ClassSession.id).where(
                ClassSession.gym_id == gym.id,
                ClassSession.space_id == space.id,
                start_dt < ClassSession.end_time,
                end_dt > ClassSession.start_time,
            )
        ).first()
        if conflict is None:
            break
        start_dt += timedelta(days=1)
    end_dt = start_dt + timedelta(minutes=60)
    payload = {
        "space_id": str(space.id),
        "title": "New Session",
        "description": "A test class",
        "class_type": "yoga",
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "capacity": 30,
        "price_cents": 5000,
        "waitlist_capacity": 5,
        "marketplace_visible": True,
    }

    resp = client.post(f"{API}/class_sessions", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["description"] == "A test class"
    assert body["class_type"] == "yoga"
    assert body["capacity"] == 30
    assert body["waitlist_capacity"] == 5
    assert body["approval_status"] == "auto_approved"
    assert body["created_by_staff_id"] == str(staff.id)


def test_create_class_session_instructor_pending(
    client: TestClient, db: Session
) -> None:
    """Instructor-created sessions should be pending_approval."""
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.INSTRUCTOR)

    start, end = _future_time(200)
    payload = {
        "space_id": str(space.id),
        "title": "Instructor Class",
        "start_time": start,
        "end_time": end,
    }

    resp = client.post(f"{API}/class_sessions", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["approval_status"] == "pending_approval"


def test_create_class_session_space_conflict(
    client: TestClient, db: Session
) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    # Use far-future 3AM slot to avoid seed data conflicts
    start_dt = datetime.now(timezone.utc) + timedelta(days=60)
    start_dt = start_dt.replace(hour=3, minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(minutes=60)
    start, end = start_dt.isoformat(), end_dt.isoformat()

    payload = {
        "space_id": str(space.id),
        "title": "First",
        "start_time": start,
        "end_time": end,
    }
    resp1 = client.post(f"{API}/class_sessions", json=payload, headers=headers)
    assert resp1.status_code == 201

    # Same time, same space
    payload["title"] = "Conflict"
    resp2 = client.post(f"{API}/class_sessions", json=payload, headers=headers)
    assert resp2.status_code == 409
    assert resp2.json()["detail"]["code"] == "SPACE_TIME_CONFLICT"


# =========================================================================
# Recurring scheduling
# =========================================================================


def test_create_recurring_sessions(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    start_date = (datetime.now(timezone.utc) + timedelta(days=30)).date()
    end_date = start_date + timedelta(days=14)

    payload = {
        "space_id": str(space.id),
        "title": "Recurring Yoga",
        "class_type": "yoga",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days_of_week": [0, 2, 4],  # Mon, Wed, Fri
        "start_time_hour": 10,
        "start_time_minute": 0,
        "duration_minutes": 60,
        "capacity": 20,
    }

    resp = client.post(
        f"{API}/class_sessions/recurring", json=payload, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["created_count"] > 0
    assert body["recurrence_group_id"] is not None
    assert len(body["sessions"]) == body["created_count"]
    # All sessions share the same recurrence group
    group_ids = {s["recurrence_group_id"] for s in body["sessions"]}
    assert len(group_ids) == 1


# =========================================================================
# Instructor assignment
# =========================================================================


def test_assign_instructor(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, owner = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    # Create instructor
    _, instructor = _staff_token_headers(client, db, gym, StaffRole.INSTRUCTOR)

    start, end = _future_time(400)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Assign Test",
            "start_time": start,
            "end_time": end,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["id"]

    # Assign instructor
    assign_resp = client.patch(
        f"{API}/class_sessions/{session_id}/instructor",
        json={"instructor_staff_id": str(instructor.id)},
        headers=headers,
    )
    assert assign_resp.status_code == 200
    assert assign_resp.json()["instructor_staff_id"] == str(instructor.id)


def test_assign_instructor_conflict(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)
    _, instructor = _staff_token_headers(client, db, gym, StaffRole.INSTRUCTOR)

    start, end = _future_time(500)

    # Create two sessions at the same time
    s1 = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Session 1",
            "start_time": start,
            "end_time": end,
            "instructor_staff_id": str(instructor.id),
        },
        headers=headers,
    )
    assert s1.status_code == 201

    # Use another dedicated space for the second session.
    other_space = Space(
        gym_id=gym.id,
        name=f"Test Space {uuid4().hex[:8]}",
        capacity=40,
        is_active=True,
    )
    db.add(other_space)
    db.commit()
    db.refresh(other_space)

    s2 = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(other_space.id),
            "title": "Session 2",
            "start_time": start,
            "end_time": end,
        },
        headers=headers,
    )
    assert s2.status_code == 201

    # Try to assign the same instructor
    assign = client.patch(
        f"{API}/class_sessions/{s2.json()['id']}/instructor",
        json={"instructor_staff_id": str(instructor.id)},
        headers=headers,
    )
    assert assign.status_code == 409
    assert assign.json()["detail"]["code"] == "INSTRUCTOR_TIME_CONFLICT"


# =========================================================================
# Approval workflow
# =========================================================================


def test_approval_workflow(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    instr_headers, _ = _staff_token_headers(client, db, gym, StaffRole.INSTRUCTOR)
    mgr_headers, _ = _staff_token_headers(client, db, gym, StaffRole.MANAGER)

    start, end = _future_time(600)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Pending Class",
            "start_time": start,
            "end_time": end,
        },
        headers=instr_headers,
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["id"]
    assert create_resp.json()["approval_status"] == "pending_approval"

    # List pending
    pending_resp = client.get(
        f"{API}/class_sessions/pending", headers=mgr_headers
    )
    assert pending_resp.status_code == 200
    pending_ids = [s["id"] for s in pending_resp.json()]
    assert session_id in pending_ids

    # Approve
    approve_resp = client.patch(
        f"{API}/class_sessions/{session_id}/approval",
        json={"approval_status": "approved"},
        headers=mgr_headers,
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["approval_status"] == "approved"


# =========================================================================
# Enhanced cancellation
# =========================================================================


def test_cancel_class_session_with_reason(
    client: TestClient, db: Session
) -> None:
    gym, space = _get_gym_and_space(db)
    headers, staff = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    start, end = _future_time(700)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Cancel Me",
            "start_time": start,
            "end_time": end,
            "capacity": 20,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["id"]

    cancel_resp = client.post(
        f"{API}/class_sessions/{session_id}/cancel",
        json={"reason": "Instructor sick"},
        headers=headers,
    )
    assert cancel_resp.status_code == 200
    body = cancel_resp.json()
    assert body["status"] == "cancelled"
    assert body["cancellation_reason"] == "Instructor sick"
    assert body["cancelled_by_staff_id"] == str(staff.id)
    assert "booking_count" in body


def test_cancel_already_cancelled(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    start, end = _future_time(800)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Double Cancel",
            "start_time": start,
            "end_time": end,
        },
        headers=headers,
    )
    session_id = create_resp.json()["id"]
    client.post(f"{API}/class_sessions/{session_id}/cancel", headers=headers)
    resp2 = client.post(f"{API}/class_sessions/{session_id}/cancel", headers=headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"]["code"] == "ALREADY_CANCELLED"


# =========================================================================
# Capacity management
# =========================================================================


def test_update_capacity(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    start, end = _future_time(900)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Cap Test",
            "start_time": start,
            "end_time": end,
            "capacity": 20,
        },
        headers=headers,
    )
    session_id = create_resp.json()["id"]

    cap_resp = client.patch(
        f"{API}/class_sessions/{session_id}/capacity",
        json={"capacity": 35, "waitlist_capacity": 10},
        headers=headers,
    )
    assert cap_resp.status_code == 200
    assert cap_resp.json()["capacity"] == 35
    assert cap_resp.json()["waitlist_capacity"] == 10


# =========================================================================
# Marketplace pricing
# =========================================================================


def test_update_pricing(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    start, end = _future_time(1000)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Pricing Test",
            "start_time": start,
            "end_time": end,
        },
        headers=headers,
    )
    session_id = create_resp.json()["id"]

    price_resp = client.patch(
        f"{API}/class_sessions/{session_id}/pricing",
        json={"price_cents": 15000, "marketplace_visible": False},
        headers=headers,
    )
    assert price_resp.status_code == 200
    assert price_resp.json()["price_cents"] == 15000
    assert price_resp.json()["marketplace_visible"] is False


# =========================================================================
# Calendar endpoint
# =========================================================================


def test_calendar_endpoint(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    today = datetime.now(timezone.utc).date()
    start = today.isoformat()
    end = (today + timedelta(days=7)).isoformat()

    resp = client.get(
        f"{API}/class_sessions/calendar?start_date={start}&end_date={end}",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    if body:
        assert "date" in body[0]
        assert "sessions" in body[0]
        assert len(body[0]["sessions"]) > 0


def test_calendar_filters(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    today = datetime.now(timezone.utc).date()
    start = today.isoformat()
    end = (today + timedelta(days=7)).isoformat()

    resp = client.get(
        f"{API}/class_sessions/calendar?start_date={start}&end_date={end}&space_id={space.id}",
        headers=headers,
    )
    assert resp.status_code == 200


def test_calendar_range_too_large(client: TestClient, db: Session) -> None:
    gym, _ = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    today = datetime.now(timezone.utc).date()
    resp = client.get(
        f"{API}/class_sessions/calendar?start_date={today.isoformat()}&end_date={(today + timedelta(days=100)).isoformat()}",
        headers=headers,
    )
    assert resp.status_code == 400


# =========================================================================
# List and get class sessions
# =========================================================================


def test_list_class_sessions(client: TestClient, db: Session) -> None:
    gym, _ = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.INSTRUCTOR)

    resp = client.get(f"{API}/class_sessions", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_class_session(client: TestClient, db: Session) -> None:
    gym, space = _get_gym_and_space(db)
    headers, _ = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    start, end = _future_time(1100)
    create_resp = client.post(
        f"{API}/class_sessions",
        json={
            "space_id": str(space.id),
            "title": "Get Me",
            "start_time": start,
            "end_time": end,
        },
        headers=headers,
    )
    session_id = create_resp.json()["id"]

    get_resp = client.get(
        f"{API}/class_sessions/{session_id}", headers=headers
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == session_id
    assert get_resp.json()["title"] == "Get Me"
