# 13-9-consumer-web-share-and-invite

## Status
done

## Implementation Notes
Share class via link and referral invite in `frontend/apps/consumer-web/src/pages/Share/`. Generates shareable deep links for classes and referral codes with Web Share API fallback to clipboard copy.

## Validation
- Lint and type-check pass
- `pnpm --filter consumer-web build` (pass)
