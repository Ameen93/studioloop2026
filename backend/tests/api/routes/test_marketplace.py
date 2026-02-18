from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import ClassSession, ClassSessionStatus, Gym, Space
from tests.api.routes.test_staff_memberships import _consumer_headers


def _create_marketplace_session(
    db: Session,
    gym: Gym,
    *,
    title: str = "Marketplace HIIT",
    days_ahead: int = 1,
    capacity: int = 20,
    spots_booked: int = 0,
    price_cents: int = 15000,
) -> ClassSession:
    space = Space(gym_id=gym.id, name=f"Market-{uuid4().hex[:6]}", capacity=capacity)
    db.add(space)
    db.commit()
    db.refresh(space)

    cs = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        title=title,
        start_time=datetime.now(timezone.utc) + timedelta(days=days_ahead),
        end_time=datetime.now(timezone.utc) + timedelta(days=days_ahead, hours=1),
        capacity=capacity,
        spots_booked=spots_booked,
        waitlist_enabled=True,
        price_cents=price_cents,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def test_browse_marketplace_classes_only_enabled_gyms(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    enabled_gym = Gym(
        name=f"Enabled {uuid4().hex[:6]}",
        slug=f"enabled-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
        city="Cape Town",
        province="Western Cape",
    )
    disabled_gym = Gym(
        name=f"Disabled {uuid4().hex[:6]}",
        slug=f"disabled-{uuid4().hex[:6]}",
        is_marketplace_enabled=False,
        city="Pretoria",
        province="Gauteng",
    )
    db.add(enabled_gym)
    db.add(disabled_gym)
    db.commit()
    db.refresh(enabled_gym)
    db.refresh(disabled_gym)

    enabled = _create_marketplace_session(db, enabled_gym, title="Enabled Class")
    _create_marketplace_session(db, disabled_gym, title="Disabled Class")

    enabled.status = ClassSessionStatus.CANCELLED
    db.add(enabled)
    db.commit()

    _create_marketplace_session(db, enabled_gym, title="Enabled Replacement")

    res = client.get("/api/v1/marketplace/classes", headers=headers)
    assert res.status_code == 200

    titles = [item["title"] for item in res.json()]
    assert "Enabled Class" not in titles
    assert "Enabled Replacement" in titles
    assert "Disabled Class" not in titles


def test_filter_marketplace_classes_by_type(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Type Gym {uuid4().hex[:6]}",
        slug=f"type-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    _create_marketplace_session(db, gym, title="Morning Yoga Flow")
    _create_marketplace_session(db, gym, title="Evening Boxing")

    res = client.get("/api/v1/marketplace/classes", params={"class_type": "yoga"}, headers=headers)
    assert res.status_code == 200
    titles = [item["title"] for item in res.json()]
    assert titles == ["Morning Yoga Flow"]
