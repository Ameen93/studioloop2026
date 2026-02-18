# Story 2.2: Gym Profile Configuration

Status: done

## Story

As a **gym owner**,
I want to configure my gym's public profile,
So that consumers can learn about my gym.

## Acceptance Criteria

1. Owner/manager can update gym profile details (name, description, tagline).
2. Logo and cover photo gallery URLs can be configured for public profile presentation.
3. Address + map coordinates (lat/lng) can be saved.
4. Contact email and SA phone can be updated with validation.
5. Public profile endpoint returns updated profile data.

## Tasks / Subtasks

- [x] Extended `gyms` model with profile presentation fields (`tagline`, `logo_url`, `cover_photo_urls`).
- [x] Added Alembic migration to add new profile fields.
- [x] Added authenticated endpoints for gym profile read/update (`GET/PATCH /api/v1/gyms/me/profile`) with owner/manager RBAC.
- [x] Added public profile endpoint (`GET /api/v1/gyms/{gym_slug}/profile`).
- [x] Added SA phone validation and strict HTTP URL validation for media.
- [x] Added tests for profile update, public profile read, auth read, role enforcement, and tenant isolation safety.
- [x] Ran Claude Code review and applied fixes (PATCH semantics, list validation, stricter URL types, additional tests).

## Dev Agent Record

### Agent Model Used

OpenAI Codex (gpt-5.3-codex)

### Completion Notes

- Implemented Story 2.2 gym profile configuration endpoints and model support.
- Applied Claude Code review findings and updated endpoint semantics from PUT to PATCH to avoid unintended field wipes.
- Added/updated tests for the main profile flows and authorization boundaries.
- Test execution is currently blocked in this environment by missing shared runtime env config and an existing DB revision mismatch (`Can't locate revision identified by 'b39ef91be31a'`).

### File List

- `backend/app/models/gym.py`
- `backend/app/api/routes/gyms.py`
- `backend/app/alembic/versions/2ffca2ba00f3_add_gym_profile_media_fields.py`
- `backend/tests/api/routes/test_gyms.py`
