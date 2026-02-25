"""Real-time WebSocket endpoints (Epic 11, Stories 11.7 & 11.8).

Implements:
- Story 11.7: Real-Time Class Availability (spots updates)
- Story 11.8: Real-Time Waitlist Updates (position changes)

Uses FastAPI's built-in WebSocket support with in-memory
broadcast for connected clients. Each session has its own
set of connected clients for availability and waitlist updates.
"""

import asyncio
import json
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, col, select

from app.core.db import engine
from app.models.booking import Booking, BookingStatus
from app.models.class_session import ClassSession
from app.models.waitlist_entry import WaitlistEntry, WaitlistStatus

router = APIRouter(tags=["realtime"])


# =============================================================================
# Connection Manager - In-Memory Broadcast
# =============================================================================


class ConnectionManager:
    """Manages WebSocket connections for real-time updates.

    Connections are organized by channel (session_id + type).
    When data changes, all connected clients on the relevant
    channel receive the update.
    """

    def __init__(self) -> None:
        # Key: "{session_id}:{channel_type}" -> set of WebSocket connections
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """Accept a WebSocket connection and add it to a channel."""
        await websocket.accept()
        self._connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """Remove a WebSocket connection from a channel."""
        self._connections[channel].discard(websocket)
        # Clean up empty channels
        if not self._connections[channel]:
            del self._connections[channel]

    async def broadcast(self, channel: str, data: dict[str, object]) -> None:
        """Broadcast a message to all connections on a channel."""
        dead_connections: list[WebSocket] = []
        for ws in self._connections.get(channel, set()):
            try:
                await ws.send_json(data)
            except Exception:
                dead_connections.append(ws)

        # Remove dead connections
        for ws in dead_connections:
            self._connections[channel].discard(ws)

    def connection_count(self, channel: str) -> int:
        """Get the number of active connections on a channel."""
        return len(self._connections.get(channel, set()))


# Singleton connection manager
manager = ConnectionManager()


# =============================================================================
# Helpers
# =============================================================================


def _get_session_availability(session_id: UUID) -> dict[str, object] | None:
    """Fetch current availability for a class session from the database."""
    with Session(engine) as db:
        class_session = db.get(ClassSession, session_id)
        if not class_session:
            return None

        # Count active bookings
        active_bookings = db.exec(
            select(Booking).where(
                Booking.session_id == session_id,
                Booking.status == BookingStatus.BOOKED,
            )
        ).all()

        spots_booked = len(active_bookings)
        spots_remaining = max(0, class_session.capacity - spots_booked)

        return {
            "session_id": str(session_id),
            "capacity": class_session.capacity,
            "spots_booked": spots_booked,
            "spots_remaining": spots_remaining,
            "is_full": spots_remaining == 0,
            "waitlist_enabled": class_session.waitlist_enabled,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def _get_waitlist_positions(session_id: UUID) -> dict[str, object] | None:
    """Fetch current waitlist for a class session from the database."""
    with Session(engine) as db:
        class_session = db.get(ClassSession, session_id)
        if not class_session:
            return None

        entries = db.exec(
            select(WaitlistEntry)
            .where(
                WaitlistEntry.session_id == session_id,
                col(WaitlistEntry.status).in_(
                    [WaitlistStatus.WAITLISTED, WaitlistStatus.OFFERED]
                ),
            )
            .order_by(col(WaitlistEntry.position).asc())
        ).all()

        return {
            "session_id": str(session_id),
            "waitlist": [
                {
                    "consumer_id": str(entry.consumer_id),
                    "position": entry.position,
                    "status": entry.status.value,
                    "offered_at": entry.offered_at.isoformat()
                    if entry.offered_at
                    else None,
                    "expires_at": entry.expires_at.isoformat()
                    if entry.expires_at
                    else None,
                }
                for entry in entries
            ],
            "total_waiting": len(entries),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# =============================================================================
# Story 11.7: Real-Time Class Availability
# =============================================================================


@router.websocket("/ws/sessions/{session_id}/availability")
async def session_availability_ws(
    websocket: WebSocket,
    session_id: UUID,
) -> None:
    """WebSocket endpoint for real-time class session availability.

    On connection, sends the current availability state.
    Then sends updates whenever availability changes.

    Clients can send a JSON message with {"action": "refresh"}
    to force a re-fetch of current availability.

    The server also polls for changes every 5 seconds as a
    fallback mechanism for changes made outside WebSocket context.
    """
    channel = f"{session_id}:availability"

    # Validate session exists
    initial_data = _get_session_availability(session_id)
    if initial_data is None:
        await websocket.close(code=4004, reason="Session not found")
        return

    await manager.connect(websocket, channel)

    try:
        # Send initial state
        await websocket.send_json(
            {
                "type": "availability_snapshot",
                "data": initial_data,
            }
        )

        while True:
            try:
                # Wait for client messages with a timeout for periodic refresh
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=5.0,
                )

                # Handle client commands
                try:
                    parsed = json.loads(message)
                    if parsed.get("action") == "refresh":
                        data = _get_session_availability(session_id)
                        if data:
                            await websocket.send_json(
                                {
                                    "type": "availability_snapshot",
                                    "data": data,
                                }
                            )
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Invalid JSON message",
                        }
                    )

            except asyncio.TimeoutError:
                # Periodic refresh - send current state
                data = _get_session_availability(session_id)
                if data:
                    await manager.broadcast(
                        channel,
                        {
                            "type": "availability_update",
                            "data": data,
                        },
                    )

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, channel)


# =============================================================================
# Story 11.8: Real-Time Waitlist Updates
# =============================================================================


@router.websocket("/ws/sessions/{session_id}/waitlist")
async def session_waitlist_ws(
    websocket: WebSocket,
    session_id: UUID,
) -> None:
    """WebSocket endpoint for real-time waitlist position updates.

    On connection, sends the current waitlist state.
    Then sends updates whenever waitlist positions change.

    Clients can send a JSON message with {"action": "refresh"}
    to force a re-fetch of current waitlist state.

    The server also polls for changes every 5 seconds.
    """
    channel = f"{session_id}:waitlist"

    # Validate session exists
    initial_data = _get_waitlist_positions(session_id)
    if initial_data is None:
        await websocket.close(code=4004, reason="Session not found")
        return

    await manager.connect(websocket, channel)

    try:
        # Send initial state
        await websocket.send_json(
            {
                "type": "waitlist_snapshot",
                "data": initial_data,
            }
        )

        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=5.0,
                )

                try:
                    parsed = json.loads(message)
                    if parsed.get("action") == "refresh":
                        data = _get_waitlist_positions(session_id)
                        if data:
                            await websocket.send_json(
                                {
                                    "type": "waitlist_snapshot",
                                    "data": data,
                                }
                            )
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Invalid JSON message",
                        }
                    )

            except asyncio.TimeoutError:
                # Periodic refresh
                data = _get_waitlist_positions(session_id)
                if data:
                    await manager.broadcast(
                        channel,
                        {
                            "type": "waitlist_update",
                            "data": data,
                        },
                    )

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, channel)


# =============================================================================
# Utility function for external use
# =============================================================================


async def notify_availability_change(session_id: UUID) -> None:
    """Notify all connected clients about an availability change.

    Call this from booking/cancellation endpoints to push
    real-time updates to connected WebSocket clients.
    """
    channel = f"{session_id}:availability"
    if manager.connection_count(channel) > 0:
        data = _get_session_availability(session_id)
        if data:
            await manager.broadcast(
                channel,
                {
                    "type": "availability_update",
                    "data": data,
                },
            )


async def notify_waitlist_change(session_id: UUID) -> None:
    """Notify all connected clients about a waitlist change.

    Call this from waitlist management endpoints to push
    real-time updates to connected WebSocket clients.
    """
    channel = f"{session_id}:waitlist"
    if manager.connection_count(channel) > 0:
        data = _get_waitlist_positions(session_id)
        if data:
            await manager.broadcast(
                channel,
                {
                    "type": "waitlist_update",
                    "data": data,
                },
            )
