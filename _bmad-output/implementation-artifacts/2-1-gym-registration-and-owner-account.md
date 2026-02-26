# Story 2.1: Gym Registration and Owner Account

Status: done

## Story

As a **gym owner**,
I want to register my gym on StudioLoop,
So that I can start using the platform to manage my business.

## Acceptance Criteria

1. New gym owner can register with owner credentials + gym details.
2. `gyms` record is created with UUID primary key.
3. Owner is linked to the gym via `staff` record with `role: owner`.
4. Verification email is sent when email delivery is configured.
5. Gym includes required contact fields (`name`, `slug`, contact email/phone, `is_active`).

## Tasks / Subtasks

- [x] Add gym onboarding API endpoint: `POST /api/v1/gyms/register`
- [x] Validate duplicate gym slug and duplicate owner email
- [x] Validate and normalize South African phone numbers
- [x] Create gym + owner staff atomically in one transaction
- [x] Hash owner password with Argon2-compatible backend helper
- [x] Send verification email when SMTP is enabled
- [x] Add tests for successful registration + validation failures

## Dev Agent Record

### Agent Model Used

OpenAI Codex (gpt-5.3-codex)

### Completion Notes

- Implemented `backend/app/api/routes/gyms.py` with story 2.1 registration flow.
- Wired route in `backend/app/api/main.py`.
- Added tests in `backend/tests/api/routes/test_gyms.py`.
- Local ruff checks pass for changed files.

### File List

- `backend/app/api/routes/gyms.py`
- `backend/app/api/main.py`
- `backend/tests/api/routes/test_gyms.py`
