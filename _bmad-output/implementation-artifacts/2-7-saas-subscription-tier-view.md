# Story 2.7: SaaS Subscription Tier View

Status: done

## Summary
- Added `subscription_tier` enum field on gyms with migration.
- Implemented subscription details endpoint with tier limits, current staff count, member count, renewal date and upgrade link.
- Added tests validating subscription response payload.
- Reviewed with Claude Code and applied fixes.

## Files
- `backend/app/models/gym.py`
- `backend/app/api/routes/gyms.py`
- `backend/app/alembic/versions/aa2c9f03c120_add_epic_2_story_6_to_11_models.py`
- `backend/tests/api/routes/test_gyms.py`
