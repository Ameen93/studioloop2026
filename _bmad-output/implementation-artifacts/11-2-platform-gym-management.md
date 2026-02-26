# 11-2-platform-gym-management

## Status
done

## Implementation Notes
Admin gym list with search, filter, suspend, and reactivate actions via admin routes in `backend/app/api/routes/admin.py`. Superuser-only access enforced through CurrentUser dependency.

## Validation
- Lint and type-check pass
- `uv run pytest tests/api/routes/test_admin.py -q` (pass)
- `uv run mypy app/api/routes/admin.py` (pass)
