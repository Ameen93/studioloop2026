# Story 2.10: Space Double-Booking Prevention

Status: done

## Summary
- Added `class_sessions` model/table and scheduling endpoints.
- Implemented overlap detection by `start_time`/`end_time` and excluded cancelled sessions.
- Added alternative available space suggestions on conflict.
- Added advisory lock for race-condition hardening.
- Added tests for conflict prevention and cancelled-session rebooking.
- Reviewed with Claude Code and applied fixes.

## Files
- `backend/app/models/class_session.py`
- `backend/app/api/routes/gyms.py`
- `backend/app/alembic/versions/aa2c9f03c120_add_epic_2_story_6_to_11_models.py`
- `backend/tests/api/routes/test_gyms.py`
