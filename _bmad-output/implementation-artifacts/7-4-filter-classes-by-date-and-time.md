# 7-4-filter-classes-by-date-and-time

## Status
done

## Implementation Notes
Added date/time filtering to marketplace class discovery.
- Added `start_date`, `end_date`, `start_time_from`, `start_time_to` query params
- Supports date-window SQL filtering and time-of-day filtering on class start times
- Added range validation for date/time boundaries (400 on invalid ranges)
- Ensures `limit` is applied after all filters

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude Code review (`claude -p`) for Story 7-4.
- Applied findings: fixed limit-after-filter behavior and added invalid-range validation.
