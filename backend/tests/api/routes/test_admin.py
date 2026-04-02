"""Tests for admin endpoints (Epic 11).

Covers gym management, complaints, credits, health, gym data, and audit logs.
All endpoints require CurrentSuperUser auth.
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Consumer, Gym
from app.models.marketplace_subscription import MarketplaceSubscription

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_inactive_gym(db: Session) -> Gym:
    """Create a fresh inactive gym for approve/reject/suspend tests."""
    gym = Gym(
        name=f"TestGym-{uuid4().hex[:6]}",
        slug=f"test-gym-{uuid4().hex[:8]}",
        is_active=False,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym


def _get_consumer(db: Session) -> Consumer:
    """Return any existing consumer from seeded data."""
    consumer = db.exec(select(Consumer)).first()
    assert consumer is not None
    return consumer


# ---------------------------------------------------------------------------
# Gym management
# ---------------------------------------------------------------------------


def test_admin_list_gyms(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    res = client.get("/api/v1/admin/gyms", headers=superuser_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert "id" in data["items"][0]
    assert "name" in data["items"][0]


def test_admin_list_gyms_filter_active(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    res = client.get(
        "/api/v1/admin/gyms",
        params={"is_active": True},
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["is_active"] is True


def test_admin_approve_gym(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = _create_inactive_gym(db)
    res = client.post(
        f"/api/v1/admin/gyms/{gym.id}/approve", headers=superuser_token_headers
    )
    assert res.status_code == 200
    assert res.json()["action"] == "approved"

    db.refresh(gym)
    assert gym.is_active is True


def test_admin_approve_already_active_gym(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = Gym(
        name=f"ActiveGym-{uuid4().hex[:6]}",
        slug=f"active-gym-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    res = client.post(
        f"/api/v1/admin/gyms/{gym.id}/approve", headers=superuser_token_headers
    )
    assert res.status_code == 400


def test_admin_reject_gym(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = _create_inactive_gym(db)
    res = client.post(
        f"/api/v1/admin/gyms/{gym.id}/reject",
        params={"reason": "Incomplete documentation"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    assert res.json()["action"] == "rejected"


def test_admin_suspend_gym(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = Gym(
        name=f"SuspendGym-{uuid4().hex[:6]}",
        slug=f"suspend-gym-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    res = client.post(
        f"/api/v1/admin/gyms/{gym.id}/suspend",
        params={"reason": "Terms violation"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    assert res.json()["action"] == "suspended"

    db.refresh(gym)
    assert gym.is_active is False


def test_admin_suspend_already_inactive_gym(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = _create_inactive_gym(db)
    res = client.post(
        f"/api/v1/admin/gyms/{gym.id}/suspend",
        params={"reason": "test"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 400


def test_admin_reactivate_gym(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = _create_inactive_gym(db)
    res = client.post(
        f"/api/v1/admin/gyms/{gym.id}/reactivate", headers=superuser_token_headers
    )
    assert res.status_code == 200
    assert res.json()["action"] == "reactivated"

    db.refresh(gym)
    assert gym.is_active is True


def test_admin_gym_action_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    fake_id = uuid4()
    res = client.post(
        f"/api/v1/admin/gyms/{fake_id}/approve", headers=superuser_token_headers
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Complaints
# ---------------------------------------------------------------------------


def test_admin_create_complaint(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    consumer = _get_consumer(db)
    res = client.post(
        "/api/v1/admin/complaints",
        json={
            "consumer_id": str(consumer.id),
            "description": "Issue with booking cancellation",
        },
        headers=superuser_token_headers,
    )
    assert res.status_code == 201
    assert res.json()["status"] == "open"
    assert res.json()["consumer_id"] == str(consumer.id)


def test_admin_list_complaints(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    # Ensure at least one complaint exists
    consumer = _get_consumer(db)
    client.post(
        "/api/v1/admin/complaints",
        json={
            "consumer_id": str(consumer.id),
            "description": "List test complaint",
        },
        headers=superuser_token_headers,
    )

    res = client.get("/api/v1/admin/complaints", headers=superuser_token_headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1


def test_admin_list_complaints_filter_status(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    res = client.get(
        "/api/v1/admin/complaints",
        params={"status": "open"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["status"] == "open"


def test_admin_get_complaint(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    consumer = _get_consumer(db)
    create_res = client.post(
        "/api/v1/admin/complaints",
        json={
            "consumer_id": str(consumer.id),
            "description": "Detail test complaint",
        },
        headers=superuser_token_headers,
    )
    complaint_id = create_res.json()["id"]

    res = client.get(
        f"/api/v1/admin/complaints/{complaint_id}", headers=superuser_token_headers
    )
    assert res.status_code == 200
    assert res.json()["id"] == complaint_id
    assert res.json()["description"] == "Detail test complaint"


def test_admin_update_complaint(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    consumer = _get_consumer(db)
    create_res = client.post(
        "/api/v1/admin/complaints",
        json={
            "consumer_id": str(consumer.id),
            "description": "Update test complaint",
        },
        headers=superuser_token_headers,
    )
    complaint_id = create_res.json()["id"]

    # Add a note
    res = client.put(
        f"/api/v1/admin/complaints/{complaint_id}",
        json={"note": "Investigating the issue"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    assert len(res.json()["notes"]) >= 1

    # Change status to resolved with resolution
    res2 = client.put(
        f"/api/v1/admin/complaints/{complaint_id}",
        json={
            "status": "resolved",
            "resolution": "Refund processed",
        },
        headers=superuser_token_headers,
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "resolved"
    assert res2.json()["resolution"] == "Refund processed"


# ---------------------------------------------------------------------------
# Credits
# ---------------------------------------------------------------------------


def test_admin_issue_credits(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    consumer = _get_consumer(db)

    # Create an active marketplace subscription for this consumer
    sub = MarketplaceSubscription(
        consumer_id=consumer.id,
        classes_total=8,
        classes_remaining=3,
        status="active",
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    res = client.post(
        f"/api/v1/admin/consumers/{consumer.id}/credits",
        json={
            "amount": 5,
            "reason": "Compensation for service disruption",
            "marketplace_subscription_id": str(sub.id),
        },
        headers=superuser_token_headers,
    )
    assert res.status_code == 201
    assert res.json()["credit_log"]["amount"] == 5
    assert res.json()["new_classes_remaining"] == 8  # 3 + 5


def test_admin_issue_credits_no_subscription(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Credits should fail when consumer has no active subscription."""
    from app.core.security import get_password_hash

    consumer = Consumer(
        email=f"no-sub-{uuid4().hex[:6]}@example.com",
        first_name="No",
        last_name="Sub",
        hashed_password=get_password_hash("Pass1234!"),
        is_email_verified=True,
        is_active=True,
    )
    db.add(consumer)
    db.commit()
    db.refresh(consumer)

    res = client.post(
        f"/api/v1/admin/consumers/{consumer.id}/credits",
        json={"amount": 1, "reason": "test"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Platform health
# ---------------------------------------------------------------------------


def test_admin_platform_health(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    res = client.get("/api/v1/admin/health", headers=superuser_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_gyms"] > 0
    assert data["total_consumers"] > 0
    assert "timestamp" in data
    assert data["active_gyms"] + data["inactive_gyms"] == data["total_gyms"]


# ---------------------------------------------------------------------------
# Gym data access
# ---------------------------------------------------------------------------


def test_admin_get_gym_data(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    gym = db.exec(select(Gym).where(Gym.is_active == True)).first()  # noqa: E712
    assert gym is not None

    res = client.get(
        f"/api/v1/admin/gyms/{gym.id}/data", headers=superuser_token_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["gym_id"] == str(gym.id)
    assert data["gym_name"] == gym.name
    assert "members" in data
    assert "recent_bookings" in data
    assert "recent_payments" in data
    assert "total_revenue_cents" in data


def test_admin_get_gym_data_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    res = client.get(
        f"/api/v1/admin/gyms/{uuid4()}/data", headers=superuser_token_headers
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# Audit logs
# ---------------------------------------------------------------------------


def test_admin_list_audit_logs(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    # Trigger an audit log by approving a gym
    gym = _create_inactive_gym(db)
    client.post(
        f"/api/v1/admin/gyms/{gym.id}/approve", headers=superuser_token_headers
    )

    res = client.get("/api/v1/admin/audit_logs", headers=superuser_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(
        log["action"] == "approve_gym" for log in data["items"]
    )


def test_admin_list_audit_logs_filter_action(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    res = client.get(
        "/api/v1/admin/audit_logs",
        params={"action": "approve_gym"},
        headers=superuser_token_headers,
    )
    assert res.status_code == 200
    for log in res.json()["items"]:
        assert log["action"] == "approve_gym"


# ---------------------------------------------------------------------------
# Auth enforcement
# ---------------------------------------------------------------------------


def test_admin_requires_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    res = client.get("/api/v1/admin/health", headers=normal_user_token_headers)
    assert res.status_code in (401, 403)
