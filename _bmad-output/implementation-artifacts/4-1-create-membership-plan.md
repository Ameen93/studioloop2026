# Story 4.1: create-membership-plan

Status: done

## Summary
- Implemented membership plan creation with gym scoping, billing cycle, and tier support.
- Added/updated automated backend API tests in `backend/tests/api/routes/test_staff_memberships.py`.
- Reviewed with Claude Code and applied critical fixes (password hardening, duplicate-membership guard, migration FK naming, explicit tier handling).

## Files
- `backend/app/api/routes/staff_memberships.py`
- `backend/app/models/membership_plan.py`
- `backend/app/models/digital_waiver.py`
- `backend/app/models/gym_membership.py`
- `backend/app/models/staff.py`
- `backend/app/models/class_session.py`
- `backend/app/models/__init__.py`
- `backend/app/api/main.py`
- `backend/app/alembic/versions/f3b4d6e8a901_add_epic_3_and_4_models.py`
- `backend/app/alembic/versions/a7c9d2e4b123_add_tier_to_membership_plans.py`
- `backend/tests/api/routes/test_staff_memberships.py`
