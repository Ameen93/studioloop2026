# Stitch Payments Integration

## Overview

StudioLoop integrates with [Stitch](https://stitch.money) as a payment provider for South African bank payments. Stitch provides:

- **Pay By Bank** — One-time EFT payments via instant bank transfer
- **Variable Recurring Payments (VRP)** — Recurring subscription payments (used for gym memberships)
- **Refunds** — Refund previously completed payments

## Architecture

### Provider Pattern

The Stitch provider (`backend/app/services/payments/stitch.py`) implements the same `PaymentProvider` protocol as Ozow and PayFast. It's selected by setting `PAYMENT_PROVIDER=stitch` or passing `provider: "stitch"` in the initiate request.

### Authentication

Stitch uses **OAuth2 Client Credentials** flow:

- **Token endpoint:** `https://secure.stitch.money/connect/token`
- **Scopes:**
  - `client_paymentrequest` — for one-time Pay By Bank
  - `client_recurringpaymentconsentrequest` — for VRP/subscription payments
  - `client_refund` — for refunds
- Tokens are cached in-memory via `StitchTokenManager` and refreshed 30s before expiry

### API

Stitch uses a **GraphQL API** at `https://api.stitch.money/graphql`. Key mutations:

- `clientPaymentInitiationRequestCreate` — creates a one-time payment request, returns `{id, url}`
- `paymentConsentRequestCreate` — creates a recurring payment consent (VRP), returns `{id, url}`

The returned `url` is where the user is redirected to complete payment in Stitch's hosted UI.

### Payment Flow

1. Consumer initiates payment → backend calls Stitch GraphQL to create payment request
2. Backend returns `redirect_url` to frontend
3. Frontend redirects consumer to Stitch hosted UI
4. Consumer completes payment at their bank
5. Stitch sends webhook to our `/api/v1/payments/webhooks/stitch` endpoint
6. Webhook updates payment status, activates membership if applicable

### Webhook Verification

Stitch webhooks are delivered via **Svix**. Verification uses HMAC-SHA256:

1. Construct signed content: `{svix_id}.{svix_timestamp}.{body}`
2. HMAC-SHA256 with base64-decoded webhook secret (after `whsec_` prefix)
3. Compare with signature from `svix-signature` header
4. Reject if timestamp is >5 minutes old (replay protection)

The webhook secret is per-subscription and configured via `STITCH_WEBHOOK_SECRET`.

## Configuration

Environment variables (add to `.env`):

```env
PAYMENT_PROVIDER=stitch
STITCH_CLIENT_ID=your-client-id
STITCH_CLIENT_SECRET=your-client-secret
STITCH_WEBHOOK_SECRET=whsec_your-svix-secret
```

Optional (defaults shown):

```env
STITCH_API_URL=https://api.stitch.money/graphql
STITCH_TOKEN_URL=https://secure.stitch.money/connect/token
STITCH_REDIRECT_BASE_URL=https://secure.stitch.money/connect/payment-request
```

## Payment Type Routing

| PaymentType              | Stitch Product | Scope                                    |
|--------------------------|---------------|------------------------------------------|
| `class_booking`          | Pay By Bank   | `client_paymentrequest`                  |
| `marketplace_subscription` | Pay By Bank | `client_paymentrequest`                  |
| `membership`             | VRP (Consent) | `client_recurringpaymentconsentrequest`  |

## Testing

```bash
cd backend
uv run pytest tests/services/payments/test_stitch.py -v
```

All 14 tests mock external HTTP calls — no Stitch credentials needed.

## Future Work

- [ ] Full refund implementation via `clientRefundInitiate` mutation
- [ ] Webhook subscription auto-creation via GraphQL
- [ ] Payment status polling fallback (query `node(id:)` for status)
- [ ] DebiCheck mandate support for traditional debit orders
- [ ] PayFast provider implementation (same abstract interface)

## References

- [Stitch Pay By Bank docs](https://docs.stitch.money/payment-products/payins/paybybank/integration-process)
- [Stitch Client Tokens](https://docs.stitch.money/authentication/client-tokens)
- [Stitch Webhooks (Svix)](https://docs.stitch.money/webhooks/using_webhooks)
- [Svix manual verification](https://docs.svix.com/receiving/verifying-payloads/how-manual)
