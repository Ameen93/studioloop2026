# 11-7-real-time-class-availability

## Status
done

## Implementation Notes
WebSocket endpoint at `/ws/sessions/{session_id}/availability` in `backend/app/api/routes/realtime.py`. Broadcasts spot count changes to connected clients in real time.

## Validation
- Lint and type-check pass
- `uv run pytest tests/api/routes/test_realtime.py -q` (pass)
- `uv run mypy app/api/routes/realtime.py` (pass)
