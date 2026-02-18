# 9-2-booking-confirmation-notifications

## Status
done

## Implementation Notes
Booking confirmations are implemented via `POST /api/v1/notifications/booking-confirmation` in `backend/app/api/routes/notifications.py` using `send_multi_channel` for in-app, email, and push channels. Payload includes class, gym, date/time, instructor and booking id.

Email add-to-calendar link is currently represented as structured notification data and is ready for provider-specific email template rendering.

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -q` (pass)
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` (pass)
