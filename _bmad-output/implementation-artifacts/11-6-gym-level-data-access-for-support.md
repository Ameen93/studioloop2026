# 11-6-gym-level-data-access-for-support

## Status
done

## Implementation Notes
Admin gym data access with AuditLog tracking in `backend/app/models/admin.py` and `backend/app/api/routes/admin.py`. Every support access to gym-level data is logged for POPIA compliance.

## Validation
- Lint and type-check pass
- `uv run pytest tests/api/routes/test_admin.py -q` (pass)
- `uv run mypy app/models/admin.py app/api/routes/admin.py` (pass)
