# Feature Plan: Wallet Tab

**Status:** Planned  
**Priority:** P0 — blocks token model launch  
**Author:** Nick Fury  
**Date:** 2026-03-10  

---

## Overview

Add a **Wallet** tab to the consumer mobile app and consumer web app. This is the unified hub where users manage their StudioLoop token subscription, view token balance, purchase tokens/packs, track bookings across all studios, and manage guest passes.

This closes the gap between the existing marketplace subscription backend and the user-facing experience.

---

## User Stories

1. As a consumer, I can see my current token balance (BT and PT) at a glance
2. As a consumer, I can see my active StudioLoop subscription plan and renewal date
3. As a consumer, I can purchase token packs or upgrade/downgrade my subscription
4. As a consumer, I can see all upcoming bookings across every studio in one view
5. As a consumer, I can view my token transaction history (purchases, usage, rollovers)
6. As a consumer, I can manage my guest passes (view remaining, send to a friend)
7. As a consumer, I can pause or cancel my subscription

---

## Screens

### 1. Wallet Home (main tab screen)
**Sections:**
- **Token Balance card** — BT balance, PT balance, rollover tokens expiring soon (warning if < 7 days)
- **Active Plan card** — plan name (e.g. "Medium — 12 BT"), next renewal date, pause/cancel CTA
- **Upcoming Bookings** — next 3 bookings across all studios (tap to see full list)
- **Quick Actions** — "Buy Tokens", "Upgrade Plan", "Send Guest Pass"
- **Recent Activity** — last 5 token transactions (purchase / class used / rollover)

### 2. Token Purchase Sheet (bottom sheet / modal)
**Options displayed:**
- Single BT (R149)
- BT 3-Pack (R399)
- BT 5-Pack (R600)
- Single PT (R240)
- PT 3-Pack (R705)
- PT 5-Pack (R1,150)
- "Or choose a subscription plan →" (navigates to Plan Picker)

**Flow:**  
Select product → Payment (Stitch/card) → Confirmation → Balance updated

### 3. Plan Picker Screen
**Displays all subscription tiers with:**
- Token count, price, perks
- Current plan highlighted
- Upgrade/downgrade/cancel options
- Annual toggle (save ~15%)

**Flow:**  
Select plan → Confirm change → Takes effect next billing cycle (or immediately for upgrade)

### 4. Booking History Screen
- All bookings across all studios (upcoming + past)
- Filterable by: All / Upcoming / Past / Cancelled
- Shows: studio name, class name, date/time, token type used, check-in status

### 5. Guest Pass Screen
- Current guest pass balance
- Pass rules (Medium: 1/quarter, Heavy: 1/month)
- "Send a Guest Pass" → share link (creates ReferralInvite record)
- History of sent passes and whether they were redeemed

---

## API Endpoints (all exist — frontend only)

| Endpoint | Purpose |
|---|---|
| `GET /marketplace/subscription` | Current plan, token balance, status |
| `POST /marketplace/subscribe` | Subscribe / change plan |
| `GET /marketplace/subscriptions/history` | Token transaction history |
| `GET /marketplace/bookings` | All cross-studio bookings |
| `POST /marketplace/tokens/purchase` | Buy token pack |
| `GET /consumers/me/referral-invites` | Guest pass history |
| `POST /consumers/me/referral-invites` | Create/send guest pass |

> Note: Confirm exact endpoint paths against the OpenAPI spec before implementation.

---

## Data Model (already in DB)

- `marketplace_subscriptions` — plan tier, classes_remaining, classes_total, reset_at, status
- `credit_logs` — token transaction ledger (purchases, usage, rollovers)
- `bookings` — all bookings linked to consumer_id, filterable by source
- `referral_invites` — guest pass records

---

## Token Model Migration Required

Current backend uses `MarketplacePlanTier`: `EIGHT | TWELVE | UNLIMITED`  
New model needs: `BASIC_TOKEN | PREMIUM_TOKEN` with rollover logic and 2BT→1PT conversion

**Migration scope (backend task, tracked separately):**
- Update `MarketplacePlanTier` enum
- Add `basic_token_balance`, `premium_token_balance`, `rollover_balance` fields
- Add payout tier logic to booking flow (40-55% of retail, capped)
- Add 2BT→1PT conversion endpoint
- Update `credit_logs` to track BT vs PT separately

---

## Implementation Scope

### Consumer Mobile (React Native / Expo)
- New tab: `frontend/apps/consumer-mobile/app/(tabs)/wallet.tsx`
- Update `_layout.tsx`: replace `qr-code` tab OR add Wallet as 5th tab (move QR into Profile)
- Subscreens:
  - `app/wallet/purchase.tsx`
  - `app/wallet/plan-picker.tsx`
  - `app/wallet/booking-history.tsx`
  - `app/wallet/guest-pass.tsx`

### Consumer Web (React / Vite)
- New route: `frontend/apps/consumer-web/src/routes/wallet/Wallet.tsx`
- Add to nav

### Shared
- New API client types generated from updated OpenAPI spec (via hey-api)
- Shared UI components in `packages/ui`: `TokenBalanceCard`, `PlanCard`, `BookingRow`

---

## Tab Navigation Change

Current tabs: Home | Discover | QR Code | Memberships | Profile  
Proposed tabs: Home | Discover | Wallet | Memberships | Profile  

QR Code moves into Profile (or a floating button on Home — QR is a single-action screen, doesn't need a persistent tab slot).

---

## Acceptance Criteria

- [ ] User can view BT and PT token balance on Wallet home
- [ ] User can see active plan name, tokens remaining, renewal date
- [ ] User can purchase a token pack end-to-end (select → pay → balance updates)
- [ ] User can subscribe/upgrade/downgrade a plan
- [ ] User can view all upcoming and past bookings across studios
- [ ] User can view token transaction history (used, purchased, rolled over)
- [ ] User can send a guest pass via share link
- [ ] Annual plan toggle works on Plan Picker
- [ ] Wallet tab is visible in bottom nav on mobile
- [ ] Equivalent Wallet page exists on consumer-web

---

## Dependencies

- Backend token model migration (BT/PT enum + balance fields)
- Payment integration (Stitch) connected to token purchase flow
- Breakage/rollover job (cron to reset balances monthly and carry over rollover tokens)

---

## Estimated Effort

| Area | Estimate |
|---|---|
| Consumer mobile (Wallet tab + subscreens) | 3-4 days |
| Consumer web (Wallet page) | 1-2 days |
| Backend token model migration | 2-3 days |
| Shared UI components | 1 day |
| **Total** | **~7-10 days** |
