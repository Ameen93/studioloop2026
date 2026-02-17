"""Tests for gym onboarding endpoints (Story 2.1)."""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import verify_password
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
