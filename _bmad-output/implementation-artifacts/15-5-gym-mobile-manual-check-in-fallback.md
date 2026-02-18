# 15-5-gym-mobile-manual-check-in-fallback

## Status
done

## Implementation Notes
Search by phone/name fallback for check-in in `frontend/apps/gym-mobile/src/screens/CheckIn/ManualCheckIn.tsx`. Debounced search with member list results and one-tap check-in confirmation.

## Validation
- Lint and type-check pass
- `pnpm --filter gym-mobile lint` (pass)
