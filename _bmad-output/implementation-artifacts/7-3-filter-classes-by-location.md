# 7-3-filter-classes-by-location

## Status
done

## Implementation Notes
Added location-based filtering to marketplace browse endpoint.
- Added `city` and `province` query parameters on `GET /api/v1/marketplace/classes`
- Implemented case-insensitive exact matching using normalized lowercase comparisons
- Supports combined location filters with existing class-type filter

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude Code review (`claude -p`) for Story 7-3.
- Applied review fix: replaced wildcard-prone location `ilike` usage with normalized exact matching.
