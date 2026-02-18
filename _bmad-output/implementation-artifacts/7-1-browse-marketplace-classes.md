# 7-1-browse-marketplace-classes

## Status
done

## Implementation Notes
Implemented consumer-authenticated marketplace browse endpoint.
- Added `GET /api/v1/marketplace/classes`
- Returns upcoming classes from marketplace-enabled gyms only
- Excludes cancelled sessions and inactive spaces
- Includes gym/location + class pricing/capacity metadata

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude Code review (`claude -p`) on working diff.
- Applied fixes: filtered cancelled sessions and inactive spaces; removed non-idiomatic unused-variable pattern.
