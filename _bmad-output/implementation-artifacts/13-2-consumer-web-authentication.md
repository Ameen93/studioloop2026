# 13-2-consumer-web-authentication

## Status
done

## Implementation Notes
Consumer login, register, and forgot-password flows in `frontend/apps/consumer-web/src/pages/Auth/`. Uses shared api-client for consumer auth endpoints with JWT storage and protected route guards.

## Validation
- Lint and type-check pass
- `pnpm --filter consumer-web build` (pass)
