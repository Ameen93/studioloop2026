"""Tests for real-time WebSocket endpoints (Epic 11, Stories 11.7 & 11.8).

Tests WebSocket connections for class availability and waitlist updates.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from starlette.websockets import WebSocketDisconnect

from app.models import ClassSession


def _get_seeded_session_id(db: Session) -> str:
    """Get a class session ID from seeded data."""
    cs = db.exec(select(ClassSession).where(ClassSession.is_active == True)).first()  # noqa: E712
    assert cs is not None
    return str(cs.id)


def test_availability_ws_connects(client: TestClient, db: Session) -> None:
    session_id = _get_seeded_session_id(db)
    with client.websocket_connect(f"/api/v1/ws/sessions/{session_id}/availability") as ws:
        data = ws.receive_json()
        assert data["type"] == "availability_snapshot"
        assert "data" in data
        assert data["data"]["session_id"] == session_id
        assert "spots_remaining" in data["data"]
        assert "capacity" in data["data"]


def test_availability_ws_invalid_session(client: TestClient) -> None:
    fake_id = uuid4()
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(
            f"/api/v1/ws/sessions/{fake_id}/availability"
        ):
            pass
    assert exc_info.value.code == 4004


def test_waitlist_ws_connects(client: TestClient, db: Session) -> None:
    session_id = _get_seeded_session_id(db)
    with client.websocket_connect(f"/api/v1/ws/sessions/{session_id}/waitlist") as ws:
        data = ws.receive_json()
        assert data["type"] == "waitlist_snapshot"
        assert "data" in data
        assert data["data"]["session_id"] == session_id
        assert "waitlist" in data["data"]
        assert "total_waiting" in data["data"]
