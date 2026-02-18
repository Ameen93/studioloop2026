"""Tests for gym onboarding endpoints (Stories 2.1 and 2.2)."""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import Gym, Staff, StaffRole

API_PREFIX = "/api/v1/gyms/register"


def test_register_gym_creates_gym_and_owner(client: TestClient, db: Session) -> None:
    unique = uuid4().hex[:8]
    payload = {
        "owner_email": f"owner-{unique}@example.com",
        "owner_password": "S3curePass!123",
        "owner_first_name": "Ayesha",
        "owner_last_name": "Molefe",
        "gym_name": f"Pulse Studio {unique}",
        "gym_slug": f"pulse-studio-{unique}",
        "contact_email": f"hello-{unique}@pulsestudio.co.za",
        "contact_phone": "+27 82 123 4567",
    }

    response = client.post(API_PREFIX, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert "gym_id" in body
    assert "owner_staff_id" in body

    gym = db.exec(select(Gym).where(Gym.slug == payload["gym_slug"])).first()
    assert gym is not None
    assert gym.email == payload["contact_email"]
    assert gym.phone == "+27821234567"

    owner = db.exec(select(Staff).where(Staff.email == payload["owner_email"])).first()
    assert owner is not None
    assert owner.gym_id == gym.id
    assert owner.role == StaffRole.OWNER
    assert owner.is_email_verified is False
    assert verify_password(payload["owner_password"], owner.hashed_password)


def test_register_gym_rejects_duplicate_slug(client: TestClient) -> None:
    unique = uuid4().hex[:8]
    slug = f"fit-space-{unique}"
    base_payload = {
        "owner_password": "S3curePass!123",
        "owner_first_name": "Neo",
        "owner_last_name": "Mokoena",
        "gym_name": "Fit Space",
        "gym_slug": slug,
        "contact_phone": "+27 82 555 1212",
    }

    first = {
        **base_payload,
        "owner_email": f"one-{unique}@example.com",
        "contact_email": f"one-{unique}@fitspace.co.za",
    }
    second = {
        **base_payload,
        "owner_email": f"two-{unique}@example.com",
        "contact_email": f"two-{unique}@fitspace.co.za",
    }

    assert client.post(API_PREFIX, json=first).status_code == 201

    response = client.post(API_PREFIX, json=second)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "GYM_SLUG_ALREADY_EXISTS"


def test_register_gym_rejects_duplicate_owner_email(client: TestClient) -> None:
    unique = uuid4().hex[:8]
    owner_email = f"owner-{unique}@example.com"

    first = {
        "owner_email": owner_email,
        "owner_password": "S3curePass!123",
        "owner_first_name": "Lerato",
        "owner_last_name": "Ndlovu",
        "gym_name": "Momentum Fitness",
        "gym_slug": f"momentum-fitness-{unique}",
        "contact_email": f"hello-{unique}@momentumfit.co.za",
        "contact_phone": "+27 82 321 4321",
    }
    second = {
        **first,
        "gym_name": "Momentum Fitness 2",
        "gym_slug": f"momentum-fitness-2-{unique}",
        "contact_email": f"hello2-{unique}@momentumfit.co.za",
    }

    assert client.post(API_PREFIX, json=first).status_code == 201

    response = client.post(API_PREFIX, json=second)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "OWNER_EMAIL_ALREADY_EXISTS"


def test_register_gym_rejects_invalid_sa_phone(client: TestClient) -> None:
    unique = uuid4().hex[:8]
    payload = {
        "owner_email": f"owner-{unique}@example.com",
        "owner_password": "S3curePass!123",
        "owner_first_name": "Amahle",
        "owner_last_name": "Khumalo",
        "gym_name": "Core Movement",
        "gym_slug": f"core-movement-{unique}",
        "contact_email": f"hello-{unique}@coremovement.co.za",
        "contact_phone": "+1 555 123 4567",
    }

    response = client.post(API_PREFIX, json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"


def _staff_token_headers(
    client: TestClient,
    db: Session,
    gym: Gym,
    role: StaffRole = StaffRole.OWNER,
) -> dict[str, str]:
    email = f"{role.value}-{uuid4().hex[:8]}@example.com"
    password = "S3curePass!123"
    staff = Staff(
        gym_id=gym.id,
        email=email,
        hashed_password=get_password_hash(password),
        first_name="Gym",
        last_name="Owner",
        role=role,
        is_active=True,
        is_email_verified=True,
    )
    db.add(staff)
    db.commit()

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/staff/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_my_gym_profile_success(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    payload = {
        "name": "Pulse Studio Rosebank",
        "description": "Boutique training studio in central Johannesburg.",
        "tagline": "Train stronger, recover smarter",
        "contact_email": "hello@pulse-rosebank.co.za",
        "contact_phone": "+27 82 456 7788",
        "logo_url": "https://cdn.studioloop.co.za/gyms/pulse/logo.png",
        "cover_photo_urls": [
            "https://cdn.studioloop.co.za/gyms/pulse/cover-1.jpg",
            "https://cdn.studioloop.co.za/gyms/pulse/cover-2.jpg",
        ],
        "address_line1": "1 Tyrwhitt Ave",
        "city": "Johannesburg",
        "province": "Gauteng",
        "postal_code": "2196",
        "country": "za",
        "latitude": -26.1467,
        "longitude": 28.0416,
    }

    response = client.patch("/api/v1/gyms/me/profile", json=payload, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["tagline"] == payload["tagline"]
    assert body["contact_phone"] == "+27824567788"
    assert body["country"] == "ZA"
    assert len(body["cover_photo_urls"]) == 2

    db_gym = db.get(Gym, gym.id)
    assert db_gym is not None
    assert db_gym.logo_url == payload["logo_url"]
    assert db_gym.city == "Johannesburg"


def test_get_public_gym_profile(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    gym.name = "Public Gym Name"
    gym.tagline = "Open to all fitness levels"
    gym.cover_photo_urls = ["https://cdn.studioloop.co.za/gyms/public/cover.jpg"]
    db.add(gym)
    db.commit()

    response = client.get(f"/api/v1/gyms/{gym.slug}/profile")

    assert response.status_code == 200
    body = response.json()
    assert body["gym_id"] == str(gym.id)
    assert body["slug"] == gym.slug
    assert body["tagline"] == "Open to all fitness levels"


def test_update_my_gym_profile_rejects_invalid_phone(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    response = client.patch(
        "/api/v1/gyms/me/profile",
        json={
            "name": "Invalid Phone Gym",
            "contact_phone": "+1 555 123 4567",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"


def test_get_my_gym_profile_success(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    headers = _staff_token_headers(client, db, gym, StaffRole.MANAGER)
    response = client.get("/api/v1/gyms/me/profile", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["gym_id"] == str(gym.id)
    assert body["slug"] == gym.slug


def test_update_my_gym_profile_rejects_front_desk_role(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None

    headers = _staff_token_headers(client, db, gym, StaffRole.FRONT_DESK)
    response = client.patch(
        "/api/v1/gyms/me/profile",
        json={"name": "Should Fail"},
        headers=headers,
    )

    assert response.status_code == 403


def test_update_my_gym_profile_keeps_other_gyms_unchanged(
    client: TestClient, db: Session
) -> None:
    gyms = db.exec(select(Gym)).all()
    assert len(gyms) >= 1

    gym_a = gyms[0]
    if len(gyms) > 1:
        gym_b = gyms[1]
    else:
        gym_b = Gym(
            name=f"Second Gym {uuid4().hex[:6]}",
            slug=f"second-gym-{uuid4().hex[:6]}",
            email="second@example.com",
            phone="+27820000000",
            is_active=True,
        )
        db.add(gym_b)
        db.commit()
        db.refresh(gym_b)
    original_name = gym_b.name

    headers = _staff_token_headers(client, db, gym_a, StaffRole.OWNER)
    response = client.patch(
        "/api/v1/gyms/me/profile",
        json={"name": "Gym A Updated"},
        headers=headers,
    )

    assert response.status_code == 200

    updated_b = db.get(Gym, gym_b.id)
    assert updated_b is not None
    assert updated_b.name == original_name


def test_update_operating_hours_success(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    payload = {
        "business_hours": {
            "monday": {"is_closed": False, "open_time": "06:00", "close_time": "21:00"},
            "sunday": {"is_closed": True, "open_time": None, "close_time": None},
        }
    }

    response = client.patch(
        "/api/v1/gyms/me/operating_hours",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["business_hours"]["monday"]["open_time"] == "06:00"


def test_update_operating_hours_rejects_invalid_day(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.MANAGER)

    response = client.patch(
        "/api/v1/gyms/me/operating_hours",
        json={
            "business_hours": {
                "funday": {"is_closed": False, "open_time": "08:00", "close_time": "18:00"}
            }
        },
        headers=headers,
    )

    assert response.status_code == 422
