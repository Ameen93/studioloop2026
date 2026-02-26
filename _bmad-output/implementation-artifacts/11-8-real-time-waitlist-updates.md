# 11-8-real-time-waitlist-updates

## Status
done

## Implementation Notes
WebSocket endpoint at `/ws/sessions/{session_id}/waitlist` in `backend/app/api/routes/realtime.py`. Pushes waitlist position changes and promotion notifications to connected clients.

## Validation
- Lint and type-check pass
- `uv run pytest tests/api/routes/test_realtime.py -q` (pass)
- `uv run mypy app/api/routes/realtime.py` (pass)
