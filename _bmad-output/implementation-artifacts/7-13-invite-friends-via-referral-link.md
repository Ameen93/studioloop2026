# 7-13-invite-friends-via-referral-link

## Status
done

## Implementation Notes
Added referral link generation + referral signup tracking with hashed email storage (POPIA-safe).

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)
- `uv run pytest tests/api/routes/test_bookings.py tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude review (`claude -p`) on changed marketplace/model/test files.
- Applied fixes for: duplicate subscription creation, duplicate bookings, referral-code attribution spoofing, predictable reset date handling, and cancelled-subscription management guard.
