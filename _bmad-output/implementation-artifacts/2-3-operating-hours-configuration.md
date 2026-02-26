# Story 2.3: Operating Hours Configuration

Status: done

## Story

As a **gym owner**,
I want to set my gym's operating hours,
So that members know when we're open.

## Acceptance Criteria

1. Owner/manager can set open/close times per weekday.
2. Days can be marked as closed.
3. Different day schedules are supported.
4. Operating hours are stored in `gyms.business_hours` JSON.
5. Operating hours can be retrieved for management/public profile surfaces.

## Tasks / Subtasks

- [x] Added `business_hours` JSON field to `gyms` model.
- [x] Added Alembic migration for `business_hours` with safe default.
- [x] Implemented `GET /api/v1/gyms/me/operating_hours`.
- [x] Implemented `PATCH /api/v1/gyms/me/operating_hours`.
- [x] Added validation for weekday keys and required open/close values when day is open.
- [x] Added tests for successful update and invalid weekday validation.
- [x] Ran Claude Code review and confirmed no high/critical issues.

## Dev Agent Record

### Agent Model Used

OpenAI Codex (gpt-5.3-codex)

### Completion Notes

- Implemented gym operating-hours storage and API endpoints under owner/manager RBAC.
- Kept API naming snake_case and gym tenant scoping intact.
- Test execution remains blocked in this environment by missing shared `.env` and a DB revision-chain mismatch (`b39ef91be31a` not present).

### File List

- `backend/app/models/gym.py`
- `backend/app/api/routes/gyms.py`
- `backend/app/alembic/versions/72f6fd27cdad_add_gym_business_hours_field.py`
- `backend/tests/api/routes/test_gyms.py`
