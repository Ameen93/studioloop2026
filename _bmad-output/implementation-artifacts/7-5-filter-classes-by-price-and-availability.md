# 7-5-filter-classes-by-price-and-availability

## Status
done

## Implementation Notes
Extended marketplace browse with pricing and availability filters.
- Added `min_price_cents`, `max_price_cents`, and `only_available` query params
- Added validation for invalid price ranges (`min_price_cents > max_price_cents`)
- Filters now support combined use with prior type/location/date/time criteria

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude Code review (`claude -p`) for Story 7-5.
- Added missing negative test for invalid min/max price range.
