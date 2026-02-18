# Story 2.5: Cancellation Policy Configuration

Status: done

## Story

As a **gym owner**,
I want to set my gym's cancellation policy,
So that members understand the rules for cancelling bookings.

## Acceptance Criteria

1. Owner/manager can set cancellation window (hours before class).
2. Owner/manager can set no-show penalty (`none`, `credit_lost`, `fee`).
3. Policy is stored in `gyms.settings` JSON field.
4. Policy is retrievable for booking surfaces.

## Tasks / Subtasks

- [x] Added `settings` JSON field to `gyms` table and model.
- [x] Added migration for `gyms.settings` with safe default.
- [x] Implemented `GET /api/v1/gyms/me/cancellation_policy`.
- [x] Implemented `PATCH /api/v1/gyms/me/cancellation_policy`.
- [x] Added validation for no-show penalty values.
- [x] Added normalization/guardrails for corrupted persisted values on read.
- [x] Added tests for success path, invalid penalty, and RBAC rejection.
- [x] Ran Claude Code review and applied fixes; no high/medium findings remain.

## Dev Agent Record

### Agent Model Used

OpenAI Codex (gpt-5.3-codex)

### Completion Notes

- Preserved tenant isolation by using authenticated staff `gym_id` for all reads/writes.
- Kept API surface snake_case and role-gated to owner/manager.
- Storage is in `gyms.settings` to align with Story 2.5 requirement and future policy expansion.

### File List

- `backend/app/models/gym.py`
- `backend/app/api/routes/gyms.py`
- `backend/app/alembic/versions/e19f4a57ab22_add_gym_settings_field.py`
- `backend/tests/api/routes/test_gyms.py`
