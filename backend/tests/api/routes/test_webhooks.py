from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Gym, StaffRole
from tests.api.routes.test_staff_memberships import _staff_headers


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
