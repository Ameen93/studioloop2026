# 7-2-filter-classes-by-type

## Status
done

## Implementation Notes
Extended marketplace class browse with class-type filtering.
- Added `class_type` query parameter to `GET /api/v1/marketplace/classes`
- Applies case-insensitive title matching for class-type discovery use-case
- Escapes wildcard characters (`%`, `_`, `\\`) before `ILIKE` for safe/predictable matching

## Validation
- `uv run pytest tests/api/routes/test_marketplace.py -q` (pass)

## Claude Review
- Ran Claude Code review (`claude -p`) on Story 7-2 diff.
- Applied feedback to escape wildcard characters in `ILIKE` filter.
