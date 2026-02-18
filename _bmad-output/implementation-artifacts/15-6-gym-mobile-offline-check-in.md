# 15-6-gym-mobile-offline-check-in

## Status
done

## Implementation Notes
SQLite offline queue with sync in `frontend/apps/gym-mobile/src/services/offlineQueue.ts`. Stores check-ins locally when offline and syncs to backend when connectivity is restored with conflict resolution.

## Validation
- Lint and type-check pass
- `pnpm --filter gym-mobile lint` (pass)
