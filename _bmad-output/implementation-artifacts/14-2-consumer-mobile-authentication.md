# 14-2-consumer-mobile-authentication

## Status
done

## Implementation Notes
Consumer auth with MMKV token storage in `frontend/apps/consumer-mobile/`. Login, register, and forgot-password screens with secure JWT persistence and automatic token refresh.

## Validation
- Lint and type-check pass
- `pnpm --filter consumer-mobile lint` (pass)
