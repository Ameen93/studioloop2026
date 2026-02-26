# 12-2-gym-web-authentication

## Status
done

## Implementation Notes
Staff login page with JWT token storage in `frontend/apps/gym-web/`. Uses shared api-client package for staff auth endpoints with token refresh and protected route guards.

## Validation
- Lint and type-check pass
- `pnpm --filter gym-web build` (pass)
