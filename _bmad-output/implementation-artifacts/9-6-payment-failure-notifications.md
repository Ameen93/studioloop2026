# 9-6-payment-failure-notifications

## Status
done

## Implementation Notes
Payment failure alerts are implemented via `POST /api/v1/notifications/payment-failure` and treated as critical type notifications (cannot be fully disabled). Notifications include failure description and suggested remediation path metadata.

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -q` (pass)
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` (pass)
