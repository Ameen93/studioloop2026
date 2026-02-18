# 14-4-consumer-mobile-qr-code-display-offline

## Status
done

## Implementation Notes
QR code display with offline MMKV cache in `frontend/apps/consumer-mobile/src/screens/QRCode/`. Pre-caches QR data for upcoming bookings so check-in works without network connectivity.

## Validation
- Lint and type-check pass
- `pnpm --filter consumer-mobile lint` (pass)
