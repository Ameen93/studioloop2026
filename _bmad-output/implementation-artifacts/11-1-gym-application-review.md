# 11-1-gym-application-review

## Status
done

## Implementation Notes
Admin can approve/reject gym applications via `backend/app/api/routes/admin.py`. Uses CurrentUser superuser auth to gate access to application review endpoints.

## Validation
- Lint and type-check pass
- `uv run pytest tests/api/routes/test_admin.py -q` (pass)
- `uv run mypy app/api/routes/admin.py` (pass)
