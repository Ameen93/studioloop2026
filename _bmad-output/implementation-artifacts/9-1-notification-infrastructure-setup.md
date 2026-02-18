# 9-1

## Status
done

## Implementation Notes
Notification infrastructure for multi-channel dispatch across in-app, email, push, and WhatsApp channels.

### Models (`backend/app/models/notification.py`)
- `Notification` — core notification record with status lifecycle (pending → sent → delivered/failed), read tracking, scheduling support
- `NotificationTemplate` — reusable templates with variable substitution
- `NotificationPreference` — per-consumer channel toggles (push/email per type, WhatsApp, reminder timing)
- `GymMessage` — gym-to-member broadcast messages with recipient filtering and delivery stats
- Enums: `NotificationChannel`, `NotificationType`, `NotificationStatus`

### Service Layer (`backend/app/services/notifications/service.py`)
- `create_notification()` — persist notification records
- `dispatch_notification()` — send via channel (in-app immediate, email via SMTP, push/WhatsApp stubbed for MVP)
- `send_multi_channel()` — dispatch across channels respecting consumer preferences
- `_is_channel_enabled()` — preference checking with critical notification bypass (payment failure, class cancelled, emergency closure always enabled)
- `render_template()` — Python Template safe_substitute for notification templates
- `send_gym_message()` — broadcast to consumer list with delivery tracking

### API Routes (`backend/app/api/routes/notifications.py`)
- `GET /api/v1/notifications/health` — infrastructure health check
- Router registered in `backend/app/api/main.py`
- All Epic 9 endpoint stubs in place (stories 9-2 through 9-10)

### Database Migration (`backend/app/alembic/versions/d1a2b3c4e5f6_epic_9_notifications.py`)
- Tables: `notifications`, `notification_templates`, `notification_preferences`, `gym_messages`
- Indices on consumer_id, gym_id, status, channel, notification_type, is_read, scheduled_for, related_entity_id, created_at

### Test Coverage (`backend/tests/api/routes/test_notifications.py`)
- 19 tests covering: health check, model lifecycle, service layer (create/dispatch all channels), preference checks, template rendering, preferences CRUD API, in-app notification center

## Validation
- `uv run pytest tests/api/routes/test_notifications.py -v` (19 passed)
