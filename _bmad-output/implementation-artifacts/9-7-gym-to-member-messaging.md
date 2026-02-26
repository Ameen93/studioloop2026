# 9-7-gym-to-member-messaging

## Status
done

## Implementation Notes
Gym messaging is implemented via `POST /api/v1/notifications/gym-messages` with recipient targeting (`all`, `plan:<uuid>`, `individual`), selectable channels, optional scheduling timestamp, and delivery tracking in `gym_messages`.

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -q` (pass)
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` (pass)
