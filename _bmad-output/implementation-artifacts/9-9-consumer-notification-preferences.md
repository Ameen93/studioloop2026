# 9-9-consumer-notification-preferences

## Status
done

## Implementation Notes
Consumer notification preferences are implemented via `GET/PATCH /api/v1/notifications/me/preferences` covering channel toggles (push/email/WhatsApp), type-level controls, and reminder timing configuration. Critical notifications remain enforced.

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -q` (pass)
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` (pass)
