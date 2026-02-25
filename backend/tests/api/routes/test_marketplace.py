from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import (
    ClassSession,
    ClassSessionStatus,
    Gym,
    MarketplacePlanTier,
    MarketplaceSubscription,
    MarketplaceSubscriptionStatus,
    ReferralInvite,
    Space,
)
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

    res = client.get(
        "/api/v1/marketplace/classes",
        params={
            "city": "cape town",
            "province": "western cape",
            "limit": 200,
        },
        headers=headers,
    )
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
    assert "Morning Yoga Flow" in titles
    assert "Evening Boxing" not in titles


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
    assert "Noon Strength" in titles
    assert "Morning Run" not in titles
    assert "Late Pilates" not in titles

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


def test_view_marketplace_gym_profile(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Profile Gym {uuid4().hex[:6]}",
        slug=f"profile-gym-{uuid4().hex[:6]}",
        description="Functional fitness",
        tagline="Train better",
        is_marketplace_enabled=True,
        city="Durban",
        province="KwaZulu-Natal",
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    res = client.get(f"/api/v1/marketplace/gyms/{gym.id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == gym.name


def test_view_marketplace_class_details(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Detail Gym {uuid4().hex[:6]}",
        slug=f"detail-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
        settings={"cancellation_policy": "24-hour cancellation window"},
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    class_session = _create_marketplace_session(db, gym, title="Detail Session", capacity=12, spots_booked=7)

    res = client.get(f"/api/v1/marketplace/classes/{class_session.id}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Detail Session"
    assert body["spots_remaining"] == 5
    assert body["booking_action"] == "book"
    assert body["cancellation_policy"] == "24-hour cancellation window"


def test_view_marketplace_gym_profile_includes_amenities_and_upcoming(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Amenity Gym {uuid4().hex[:6]}",
        slug=f"amenity-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
        latitude=-33.9249,
        longitude=18.4241,
        settings={"amenities": ["showers", "lockers", "parking"]},
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    _create_marketplace_session(db, gym, title="Profile Session", days_ahead=1)

    res = client.get(
        f"/api/v1/marketplace/gyms/{gym.id}",
        params={"current_latitude": -33.93, "current_longitude": 18.42},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["amenities"] == ["showers", "lockers", "parking"]
    assert len(body["upcoming_marketplace_classes"]) == 1
    assert body["distance_km"] is not None


def test_marketplace_subscribe_and_view_status(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)

    res = client.post("/api/v1/marketplace/subscriptions", json={"plan_tier": "twelve"}, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["plan_tier"] == "twelve"
    assert body["classes_remaining"] == 12

    status = client.get("/api/v1/marketplace/subscriptions/me", headers=headers)
    assert status.status_code == 200
    assert status.json()["plan_tier"] == "twelve"

    sub = db.exec(select(MarketplaceSubscription).where(MarketplaceSubscription.consumer_id == consumer.id)).first()
    assert sub is not None


def test_book_marketplace_class_with_subscription(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)

    gym = Gym(
        name=f"Sub Book Gym {uuid4().hex[:6]}",
        slug=f"sub-book-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    class_session = _create_marketplace_session(db, gym, title="Sub Credit Class")

    sub = MarketplaceSubscription(
        consumer_id=consumer.id,
        plan_tier=MarketplacePlanTier.EIGHT,
        classes_total=8,
        classes_remaining=2,
        status=MarketplaceSubscriptionStatus.ACTIVE,
    )
    db.add(sub)
    db.commit()

    res = client.post(
        "/api/v1/marketplace/bookings/subscription",
        json={"session_id": str(class_session.id)},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["source"] == "marketplace"

    db.refresh(sub)
    assert sub.classes_remaining == 1


def test_manage_marketplace_subscription_pause_and_cancel(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)
    sub = MarketplaceSubscription(
        consumer_id=consumer.id,
        plan_tier=MarketplacePlanTier.EIGHT,
        classes_total=8,
        classes_remaining=8,
        status=MarketplaceSubscriptionStatus.ACTIVE,
    )
    db.add(sub)
    db.commit()

    pause_res = client.post(
        "/api/v1/marketplace/subscriptions/me/manage",
        json={"action": "pause"},
        headers=headers,
    )
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "paused"

    cancel_res = client.post(
        "/api/v1/marketplace/subscriptions/me/manage",
        json={"action": "cancel"},
        headers=headers,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"


def test_share_class_details(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    gym = Gym(
        name=f"Share Gym {uuid4().hex[:6]}",
        slug=f"share-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    class_session = _create_marketplace_session(db, gym, title="Share Session")

    res = client.get(f"/api/v1/marketplace/classes/{class_session.id}/share", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "whatsapp" in body["channels"]
    assert str(class_session.id) in body["share_link"]


def test_referral_link_and_tracking(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)

    link_res = client.get("/api/v1/marketplace/referrals/me", headers=headers)
    assert link_res.status_code == 200
    code = link_res.json()["referral_code"]

    track_res = client.post(
        "/api/v1/marketplace/referrals/track-signup",
        json={"referral_code": code, "email": "friend@example.com"},
        headers=headers,
    )
    assert track_res.status_code == 200

    invite = db.exec(select(ReferralInvite).where(ReferralInvite.referral_code == code)).first()
    assert invite is not None


def test_cannot_create_duplicate_active_subscription(client: TestClient, db: Session) -> None:
    headers, _ = _consumer_headers(client, db)
    first = client.post("/api/v1/marketplace/subscriptions", json={"plan_tier": "eight"}, headers=headers)
    assert first.status_code == 200

    second = client.post("/api/v1/marketplace/subscriptions", json={"plan_tier": "twelve"}, headers=headers)
    assert second.status_code == 400


def test_cannot_book_same_class_twice_with_subscription(client: TestClient, db: Session) -> None:
    headers, consumer = _consumer_headers(client, db)
    gym = Gym(
        name=f"Dup Book Gym {uuid4().hex[:6]}",
        slug=f"dup-book-gym-{uuid4().hex[:6]}",
        is_marketplace_enabled=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    class_session = _create_marketplace_session(db, gym, title="Dup Credit Class")

    sub = MarketplaceSubscription(
        consumer_id=consumer.id,
        plan_tier=MarketplacePlanTier.EIGHT,
        classes_total=8,
        classes_remaining=2,
        status=MarketplaceSubscriptionStatus.ACTIVE,
    )
    db.add(sub)
    db.commit()

    first = client.post("/api/v1/marketplace/bookings/subscription", json={"session_id": str(class_session.id)}, headers=headers)
    assert first.status_code == 200

    second = client.post("/api/v1/marketplace/bookings/subscription", json={"session_id": str(class_session.id)}, headers=headers)
    assert second.status_code == 409
