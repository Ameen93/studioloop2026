# Story 2.4: Holiday Closures Management

Status: done

## Story

As a **gym owner**,
I want to set holiday closures,
So that members know when we're closed for special dates.

## Acceptance Criteria

1. Owner/manager can add a holiday closure date with optional reason.
2. Owner/manager can add multiple closures and list existing closures.
3. Owner/manager can remove existing closures.
4. Closures are persisted in `gym_closures` table.
5. Closures are displayed on public gym profile.
6. Class scheduling can consume closure dates (future-facing validation support prepared in API/domain model).

## Tasks / Subtasks

- [x] Added new `gym_closures` table migration with UUID PK, gym FK, and unique `(gym_id, closure_date)` constraint.
- [x] Added `GymClosure` model + gym relationship wiring.
- [x] Implemented `GET /api/v1/gyms/me/closures`.
- [x] Implemented `POST /api/v1/gyms/me/closures` with duplicate protection and DB-level race-safe handling.
- [x] Implemented `DELETE /api/v1/gyms/me/closures/{closure_id}` with tenant scoping.
- [x] Extended gym profile responses to include `holiday_closures`.
- [x] Limited public profile closure list to today+future dates.
- [x] Added endpoint tests covering create/list/delete/duplicate and public profile visibility.
- [x] Ran Claude Code review and applied findings.

## Dev Agent Record

### Agent Model Used

OpenAI Codex (gpt-5.3-codex)

### Completion Notes

- Preserved multi-tenant isolation by scoping closure operations to `current_staff.gym_id`.
- Kept snake_case for endpoint paths and payload fields.
- Added DB uniqueness and API conflict responses for deterministic behavior under concurrent writes.
- Existing project does not yet include class scheduling story models; closure data is now available for story 5 scheduling enforcement.

### File List

- `backend/app/models/gym.py`
- `backend/app/models/gym_closure.py`
- `backend/app/models/__init__.py`
- `backend/app/api/routes/gyms.py`
- `backend/app/alembic/versions/c3d9b0ad1f1e_add_gym_closures_table.py`
- `backend/tests/api/routes/test_gyms.py`
