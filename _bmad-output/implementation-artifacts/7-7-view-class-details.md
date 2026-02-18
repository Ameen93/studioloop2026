# 7-7-view-class-details

## Status
done

## Implementation Notes
Expanded class detail endpoint with duration, booking action, instructor metadata, map link, and cancellation policy.

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)
- `uv run pytest tests/api/routes/test_bookings.py tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude review (`claude -p`) on changed marketplace/model/test files.
- Applied fixes for: duplicate subscription creation, duplicate bookings, referral-code attribution spoofing, predictable reset date handling, and cancelled-subscription management guard.
