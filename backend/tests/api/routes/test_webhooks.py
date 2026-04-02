from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Gym, StaffRole
from tests.api.routes.test_staff_memberships import _staff_headers

# ---------------------------------------------------------------------------
# CRUD + delivery tests
# ---------------------------------------------------------------------------


def test_webhook_create_and_list(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    # Create
    create_res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=headers,
        json={"url": "https://example.com/hook1", "events": ["booking.created"]},
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert "secret" in data
    assert data["endpoint"]["url"] == "https://example.com/hook1"
    webhook_id = data["endpoint"]["id"]

    # List
    list_res = client.get(f"/api/v1/gyms/{gym.id}/webhooks", headers=headers)
    assert list_res.status_code == 200
    ids = [ep["id"] for ep in list_res.json()["items"]]
    assert webhook_id in ids

    # Cleanup
    client.delete(f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers)


def test_webhook_get_detail(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    create_res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=headers,
        json={"url": "https://example.com/detail", "events": ["booking.cancelled"]},
    )
    webhook_id = create_res.json()["endpoint"]["id"]

    detail = client.get(
        f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers
    )
    assert detail.status_code == 200
    assert detail.json()["url"] == "https://example.com/detail"
    assert detail.json()["events"] == ["booking.cancelled"]

    client.delete(f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers)


def test_webhook_update(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    create_res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=headers,
        json={"url": "https://example.com/old", "events": ["booking.created"]},
    )
    webhook_id = create_res.json()["endpoint"]["id"]

    update_res = client.patch(
        f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}",
        headers=headers,
        json={"url": "https://example.com/new", "events": ["booking.created", "booking.cancelled"]},
    )
    assert update_res.status_code == 200
    assert update_res.json()["url"] == "https://example.com/new"
    assert len(update_res.json()["events"]) == 2

    client.delete(f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers)


def test_webhook_delete(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    create_res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=headers,
        json={"url": "https://example.com/delete-me", "events": []},
    )
    webhook_id = create_res.json()["endpoint"]["id"]

    del_res = client.delete(
        f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers
    )
    assert del_res.status_code == 204

    # Re-fetch should 404
    get_res = client.get(
        f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers
    )
    assert get_res.status_code == 404


def test_webhook_test_delivery(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    create_res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=headers,
        json={"url": "https://httpbin.org/post", "events": ["test.ping"]},
    )
    webhook_id = create_res.json()["endpoint"]["id"]

    # Mock the HTTP call to avoid real network requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"ok": true}'

    with patch("httpx.Client") as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_instance.__enter__ = lambda self: self
        mock_client_instance.__exit__ = MagicMock(return_value=False)
        mock_client_instance.post.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        test_res = client.post(
            f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}/test", headers=headers
        )

    assert test_res.status_code == 200
    assert test_res.json()["status"] == "delivered"
    assert test_res.json()["response_status_code"] == 200

    client.delete(f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers)


def test_webhook_list_deliveries(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    headers = _staff_headers(client, db, gym, StaffRole.OWNER)

    create_res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=headers,
        json={"url": "https://httpbin.org/post", "events": ["test.ping"]},
    )
    webhook_id = create_res.json()["endpoint"]["id"]

    # Trigger a test delivery (mocked)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "{}"

    with patch("httpx.Client") as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_instance.__enter__ = lambda self: self
        mock_client_instance.__exit__ = MagicMock(return_value=False)
        mock_client_instance.post.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        client.post(
            f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}/test", headers=headers
        )

    deliveries_res = client.get(
        f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}/deliveries", headers=headers
    )
    assert deliveries_res.status_code == 200
    assert deliveries_res.json()["total"] >= 1
    assert deliveries_res.json()["items"][0]["event_type"] == "test.ping"

    client.delete(f"/api/v1/gyms/{gym.id}/webhooks/{webhook_id}", headers=headers)


def test_webhook_role_requires_owner(client: TestClient, db: Session) -> None:
    gym = db.exec(select(Gym)).first()
    assert gym is not None
    manager_headers = _staff_headers(client, db, gym, StaffRole.MANAGER)

    res = client.post(
        f"/api/v1/gyms/{gym.id}/webhooks",
        headers=manager_headers,
        json={"url": "https://example.com/forbidden", "events": []},
    )
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Cross-tenant access control (existing tests)
# ---------------------------------------------------------------------------


def test_webhooks_denies_cross_tenant_list_access(client: TestClient, db: Session) -> None:
    gym_a = db.exec(select(Gym)).first()
    assert gym_a is not None

    gym_b = Gym(
        name=f"Webhook Gym {uuid4().hex[:6]}",
        slug=f"webhook-gym-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym_b)
    db.commit()
    db.refresh(gym_b)

    owner_headers = _staff_headers(client, db, gym_a, StaffRole.OWNER)

    response = client.get(f"/api/v1/gyms/{gym_b.id}/webhooks", headers=owner_headers)

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["code"] == "FORBIDDEN"
    assert "Access denied to this gym" in body["detail"]["message"]


def test_webhooks_denies_cross_tenant_test_event_access(
    client: TestClient, db: Session
) -> None:
    gym_a = db.exec(select(Gym)).first()
    assert gym_a is not None

    gym_b = Gym(
        name=f"Webhook Other Gym {uuid4().hex[:6]}",
        slug=f"webhook-other-{uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(gym_b)
    db.commit()
    db.refresh(gym_b)

    owner_headers = _staff_headers(client, db, gym_a, StaffRole.OWNER)

    create_res = client.post(
        f"/api/v1/gyms/{gym_a.id}/webhooks",
        headers=owner_headers,
        json={
            "url": "https://example.invalid/webhook",
            "events": ["booking.created"],
        },
    )
    assert create_res.status_code == 201
    webhook_id = create_res.json()["endpoint"]["id"]

    response = client.post(
        f"/api/v1/gyms/{gym_b.id}/webhooks/{webhook_id}/test",
        headers=owner_headers,
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"]["code"] == "FORBIDDEN"
    assert "Access denied to this gym" in body["detail"]["message"]

    delete_res = client.delete(
        f"/api/v1/gyms/{gym_a.id}/webhooks/{webhook_id}",
        headers=owner_headers,
    )
    assert delete_res.status_code == 204
