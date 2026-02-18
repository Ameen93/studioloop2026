# 14-8-consumer-mobile-push-notifications

## Status
done

## Implementation Notes
Expo Notifications client-side registration in `frontend/apps/consumer-mobile/src/services/notifications.ts`. Registers push token on login, handles foreground/background notification display, and deep-links to relevant screens.

## Validation
- Lint and type-check pass
- `pnpm --filter consumer-mobile lint` (pass)
