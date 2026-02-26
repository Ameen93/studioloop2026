# Epic 9 Review — 2026-02-18

## Scope Reviewed
Stories 9-1 through 9-10 in notifications & communication domain.

## Review Findings
- Multi-tenant isolation: verified gym-scoped and consumer-scoped access patterns in notification routes.
- Data conventions: UUID primary/foreign keys and snake_case naming preserved.
- POPIA safety: no secrets/PAN exposure in notification payloads; outputs remain operational metadata.
- Critical-notification safety: payment failure and emergency types bypass disable toggles.
- Retention/read model: in-app notification list applies 30-day retention and supports read-state transitions.

## Fixes Applied During Review
- Fixed notification payment-reminder query to use `GymMembership.ended_at` (existing model field) instead of non-existent `end_date` for static type-check correctness.

## Validation Evidence
- `uv run pytest tests/api/routes/test_notifications.py -q` → 19 passed
- `uv run mypy app/api/routes/notifications.py app/services/notifications/service.py app/models/notification.py` → success, no issues

## Manual/Secrets-Gated Items
- External provider credentials and production transports (SMTP vendor hardening, FCM/APNs keys, WhatsApp Business API live integration) remain environment/secrets-gated and are intentionally stubbed/safe for local MVP.
