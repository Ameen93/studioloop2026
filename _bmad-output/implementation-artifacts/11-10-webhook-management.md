# 11-10-webhook-management

## Status
done

## Implementation Notes
WebhookEndpoint CRUD at `/gyms/{gym_id}/webhooks` in `backend/app/api/routes/webhooks.py`. Gym-scoped endpoint management with event type filtering and secret rotation support.

## Validation
- Lint and type-check pass
- `uv run pytest tests/api/routes/test_webhooks.py -q` (pass)
- `uv run mypy app/api/routes/webhooks.py` (pass)
