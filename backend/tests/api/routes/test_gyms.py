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


def test_add_list_and_delete_holiday_closures(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    create_response = client.post(
        "/api/v1/gyms/me/closures",
        json={"closure_date": "2027-03-15", "reason": "Test closure day"},
        headers=headers,
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["closure_date"] == "2027-03-15"
    assert body["reason"] == "Test closure day"

    list_response = client.get("/api/v1/gyms/me/closures", headers=headers)
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) >= 1
    assert any(item["closure_date"] == "2027-03-15" for item in listed)

    closure_id = body["id"]
    delete_response = client.delete(f"/api/v1/gyms/me/closures/{closure_id}", headers=headers)
    assert delete_response.status_code == 204


def test_add_holiday_closure_rejects_duplicate_date(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.MANAGER)

    first = client.post(
        "/api/v1/gyms/me/closures",
        json={"closure_date": "2027-06-10", "reason": "Test day"},
        headers=headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/gyms/me/closures",
        json={"closure_date": "2027-06-10", "reason": "Duplicate"},
        headers=headers,
    )
    assert second.status_code == 400
    assert second.json()["detail"]["code"] == "CLOSURE_ALREADY_EXISTS"


def test_public_profile_includes_holiday_closures(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    create = client.post(
        "/api/v1/gyms/me/closures",
        json={"closure_date": "2027-04-27", "reason": "Test Freedom Day"},
        headers=headers,
    )
    assert create.status_code == 201

    response = client.get(f"/api/v1/gyms/{gym.slug}/profile")
    assert response.status_code == 200
    body = response.json()
    assert "holiday_closures" in body
    assert any(
        c["closure_date"] == "2027-04-27" and c["reason"] == "Test Freedom Day"
        for c in body["holiday_closures"]
    )


def test_update_cancellation_policy_success(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    response = client.patch(
        "/api/v1/gyms/me/cancellation_policy",
        json={"cancellation_window_hours": 12, "no_show_penalty": "credit_lost"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cancellation_window_hours"] == 12
    assert body["no_show_penalty"] == "credit_lost"

    follow_up = client.get("/api/v1/gyms/me/cancellation_policy", headers=headers)
    assert follow_up.status_code == 200
    assert follow_up.json()["cancellation_window_hours"] == 12


def test_update_cancellation_policy_rejects_invalid_penalty(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    response = client.patch(
        "/api/v1/gyms/me/cancellation_policy",
        json={"cancellation_window_hours": 12, "no_show_penalty": "invalid"},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_cancellation_policy_rejects_front_desk(
    client: TestClient, db: Session
) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.FRONT_DESK)

    response = client.patch(
        "/api/v1/gyms/me/cancellation_policy",
        json={"cancellation_window_hours": 6, "no_show_penalty": "none"},
        headers=headers,
    )
    assert response.status_code == 403


def test_marketplace_toggle_updates_settings(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    response = client.patch(
        "/api/v1/gyms/me/marketplace",
        json={"marketplace_enabled": True},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["marketplace_enabled"] is True


def test_subscription_details_view(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    response = client.get("/api/v1/gyms/me/subscription", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["subscription_tier"] in {"starter", "growth", "pro"}
    assert "current_staff_count" in body


def test_space_crud_and_soft_delete(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.MANAGER)

    created = client.post(
        "/api/v1/gyms/me/spaces",
        json={"name": "Studio A", "capacity": 20, "description": "Main floor"},
        headers=headers,
    )
    assert created.status_code == 201
    space_id = created.json()["id"]

    updated = client.patch(
        f"/api/v1/gyms/me/spaces/{space_id}",
        json={"capacity": 25},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["capacity"] == 25

    deleted = client.delete(f"/api/v1/gyms/me/spaces/{space_id}", headers=headers)
    assert deleted.status_code == 204


def test_space_amenities_update(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    created = client.post(
        "/api/v1/gyms/me/spaces",
        json={"name": "Yoga Room", "capacity": 12, "description": "Quiet room"},
        headers=headers,
    )
    assert created.status_code == 201
    space_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/gyms/me/spaces/{space_id}/amenities",
        json={
            "amenities": ["mirrors", "ac"],
            "equipment": ["mats", "weights"],
            "custom_amenities": ["natural_light"],
            "custom_equipment": ["trx"],
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert "mats" in response.json()["equipment"]


def test_space_double_booking_prevention(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    s1 = client.post(
        "/api/v1/gyms/me/spaces",
        json={"name": "Spin Room", "capacity": 18, "description": "Bikes"},
        headers=headers,
    ).json()
    s2 = client.post(
        "/api/v1/gyms/me/spaces",
        json={"name": "Pilates Room", "capacity": 14, "description": "Core"},
        headers=headers,
    ).json()

    first = client.post(
        "/api/v1/gyms/me/class_sessions",
        json={
            "space_id": s1["id"],
            "title": "Morning Spin",
            "start_time": "2026-02-20T08:00:00Z",
            "end_time": "2026-02-20T09:00:00Z",
        },
        headers=headers,
    )
    assert first.status_code == 201

    conflict = client.post(
        "/api/v1/gyms/me/class_sessions",
        json={
            "space_id": s1["id"],
            "title": "Overlap",
            "start_time": "2026-02-20T08:30:00Z",
            "end_time": "2026-02-20T09:30:00Z",
        },
        headers=headers,
    )
    assert conflict.status_code == 409
    details = conflict.json()["detail"]
    assert details["code"] == "SPACE_TIME_CONFLICT"
    assert any(a["space_id"] == s2["id"] for a in details["alternative_spaces"])


def test_cancelled_session_does_not_block_new_booking(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    space = client.post(
        "/api/v1/gyms/me/spaces",
        json={"name": "Box Room", "capacity": 10, "description": "Bag work"},
        headers=headers,
    ).json()

    created = client.post(
        "/api/v1/gyms/me/class_sessions",
        json={
            "space_id": space["id"],
            "title": "Boxing 1",
            "start_time": "2026-02-21T10:00:00Z",
            "end_time": "2026-02-21T11:00:00Z",
        },
        headers=headers,
    ).json()

    cancelled = client.post(
        f"/api/v1/gyms/me/class_sessions/{created['id']}/cancel",
        headers=headers,
    )
    assert cancelled.status_code == 200

    replacement = client.post(
        "/api/v1/gyms/me/class_sessions",
        json={
            "space_id": space["id"],
            "title": "Boxing 2",
            "start_time": "2026-02-21T10:00:00Z",
            "end_time": "2026-02-21T11:00:00Z",
        },
        headers=headers,
    )
    assert replacement.status_code == 201


def test_member_import_preview_and_confirm_csv(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_token_headers(client, db, gym, StaffRole.OWNER)

    csv_content = (
        "name,email,phone,membership_tier\n"
        "Alice,alice-import@example.com,+27820000001,premium\n"
        "Bob,bob-import@example.com,+27820000002,basic\n"
    )
    preview = client.post(
        "/api/v1/gyms/me/members/import/preview",
        files={"file": ("members.csv", csv_content, "text/csv")},
        headers=headers,
    )
    assert preview.status_code == 200
    rows = preview.json()["detected_members"]
    assert len(rows) == 2

    confirm = client.post(
        "/api/v1/gyms/me/members/import/confirm",
        json={
            "column_mapping": {
                "name": "name",
                "email": "email",
                "phone": "phone",
                "membership_tier": "membership_tier",
            },
            "rows": rows,
        },
        headers=headers,
    )
    assert confirm.status_code == 200
    assert confirm.json()["success_count"] == 2
