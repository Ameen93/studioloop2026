# 15-2-gym-mobile-authentication

## Status
done

## Implementation Notes
Staff login with MMKV token storage in `frontend/apps/gym-mobile/`. Login screen with gym selection, secure JWT persistence, and automatic token refresh via shared api-client.

## Validation
- Lint and type-check pass
- `pnpm --filter gym-mobile lint` (pass)
