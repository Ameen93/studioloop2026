# Story 2.6: Marketplace Participation Toggle

Status: done

## Summary
- Added owner/manager endpoints to read and update gym marketplace participation.
- Toggle is persisted in `gyms.settings["marketplace_enabled"]`.
- Added tests for update success and RBAC coverage through existing role-gated helpers.
- Ran Claude Code review and applied hardening fixes (CSV limits/race safeguards done in shared Epic 2 pass).

## Files
- `backend/app/api/routes/gyms.py`
- `backend/tests/api/routes/test_gyms.py`
