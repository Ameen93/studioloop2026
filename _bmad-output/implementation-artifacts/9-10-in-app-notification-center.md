# 9-10-in-app-notification-center

## Status
done

## Implementation Notes
In-app notification center is implemented via `GET /api/v1/notifications/me` (list + unread count, 30-day retention filter) and `POST /api/v1/notifications/me/mark-read` for read-state updates.

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -q` (pass)
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` (pass)
