# 15-10-gym-mobile-push-notifications

## Status
done

## Implementation Notes
Expo Notifications client-side registration in `frontend/apps/gym-mobile/src/services/notifications.ts`. Registers staff push token on login, handles foreground/background notifications for new bookings and schedule changes.

## Validation
- Lint and type-check pass
- `pnpm --filter gym-mobile lint` (pass)
