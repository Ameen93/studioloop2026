# 7-8-subscribe-to-marketplace-plan

## Status
done

## Implementation Notes
Added marketplace subscription create flow with plan allocations and duplicate active-subscription guard.

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)
- `uv run pytest tests/api/routes/test_bookings.py tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude review (`claude -p`) on changed marketplace/model/test files.
- Applied fixes for: duplicate subscription creation, duplicate bookings, referral-code attribution spoofing, predictable reset date handling, and cancelled-subscription management guard.
