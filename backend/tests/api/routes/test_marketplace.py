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
    start_hour: int = 9,
    duration_hours: int = 1,
    capacity: int = 20,
    spots_booked: int = 0,
    price_cents: int = 15000,
) -> ClassSession:
    space = Space(gym_id=gym.id, name=f"Market-{uuid4().hex[:6]}", capacity=capacity)
    db.add(space)
    db.commit()
    db.refresh(space)

    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(days=days_ahead)).replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=duration_hours)

    cs = ClassSession(
        gym_id=gym.id,
        space_id=space.id,
        title=title,
        start_time=start_time,
        end_time=end_time,
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


def test_filter_marketplace_classes_by_location(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    cpt_gym = Gym(
        name=f"CPT Gym {uuid4().hex[:6]}",
        slug=f"cpt-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
        city="Cape Town",
        province="Western Cape",
    )
    jhb_gym = Gym(
        name=f"JHB Gym {uuid4().hex[:6]}",
        slug=f"jhb-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
        city="Johannesburg",
        province="Gauteng",
    )
    db.add(cpt_gym)
    db.add(jhb_gym)
    db.commit()
    db.refresh(cpt_gym)
    db.refresh(jhb_gym)

    _create_marketplace_session(db, cpt_gym, title="CPT Pilates")
    _create_marketplace_session(db, jhb_gym, title="JHB Pilates")

    res = client.get(
        "/api/v1/marketplace/classes",
        params={"city": "cape town", "province": "western cape"},
        headers=headers,
    )
    assert res.status_code == 200
    titles = [item["title"] for item in res.json()]
    assert "CPT Pilates" in titles
    assert "JHB Pilates" not in titles


def test_filter_marketplace_classes_by_date_and_time(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Date Gym {uuid4().hex[:6]}",
        slug=f"date-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    _create_marketplace_session(db, gym, title="Morning Run", days_ahead=2, start_hour=6)
    target = _create_marketplace_session(db, gym, title="Noon Strength", days_ahead=2, start_hour=12)
    _create_marketplace_session(db, gym, title="Late Pilates", days_ahead=3, start_hour=18)

    res = client.get(
        "/api/v1/marketplace/classes",
        params={
            "start_date": target.start_time.date().isoformat(),
            "end_date": target.start_time.date().isoformat(),
            "start_time_from": "11:00:00",
            "start_time_to": "13:00:00",
        },
        headers=headers,
    )
    assert res.status_code == 200
    titles = [item["title"] for item in res.json()]
    assert titles == ["Noon Strength"]

    invalid = client.get(
        "/api/v1/marketplace/classes",
        params={"start_date": "2026-12-01", "end_date": "2026-01-01"},
        headers=headers,
    )
    assert invalid.status_code == 400


def test_filter_marketplace_classes_by_price_and_availability(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Price Gym {uuid4().hex[:6]}",
        slug=f"price-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    _create_marketplace_session(db, gym, title="Budget", price_cents=10000, capacity=10, spots_booked=10)
    _create_marketplace_session(db, gym, title="Standard", price_cents=18000, capacity=20, spots_booked=2)
    _create_marketplace_session(db, gym, title="Premium", price_cents=30000, capacity=20, spots_booked=1)

    res = client.get(
        "/api/v1/marketplace/classes",
        params={"min_price_cents": 15000, "max_price_cents": 25000, "only_available": True},
        headers=headers,
    )
    assert res.status_code == 200
    titles = [item["title"] for item in res.json()]
    assert "Standard" in titles
    assert "Budget" not in titles
    assert "Premium" not in titles

    invalid = client.get(
        "/api/v1/marketplace/classes",
        params={"min_price_cents": 30000, "max_price_cents": 20000},
        headers=headers,
    )
    assert invalid.status_code == 400
