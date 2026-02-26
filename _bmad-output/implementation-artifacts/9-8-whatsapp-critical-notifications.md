# 9-8-whatsapp-critical-notifications

## Status
done

## Implementation Notes
Critical WhatsApp notifications are implemented via `POST /api/v1/notifications/whatsapp/critical` for emergency-only types (class cancelled / emergency closure). Service layer supports WhatsApp channel with email fallback behavior documented for provider integration.

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -q` (pass)
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` (pass)
