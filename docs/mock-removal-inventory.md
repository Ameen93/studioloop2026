# Mock/TODO Inventory (Phase 4)

## Completed in this pass

### `frontend/apps/gym-web`
- Replaced mock dashboard with API-backed data:
  - `analyticsGymOwnerDashboard`
  - `paymentsFailedPaymentActionItems`
- Replaced mock members list with API-backed data:
  - `staffMembershipsListGymMembers`
- Replaced mock check-in search/checkin flow with API-backed data:
  - `bookingsSearchMembersForCheckIn`
  - `bookingsManualCheckIn`
- Replaced mock payments/payouts with API-backed data:
  - `paymentsGymPaymentDashboard`
  - `paymentsFailedPaymentActionItems`
  - `paymentsMarketplacePayoutReport`
- Replaced hardcoded schedule grid with real role-gated data:
  - `staffMembershipsGetInstructorSchedule`
- Added shared auth/session helper for API headers/context:
  - `frontend/apps/gym-web/src/lib/apiAuth.ts`
- Replaced staff management mock data with API-backed flows:
  - `staffMembershipsListStaff`
  - `staffMembershipsAddStaffMember`
  - `staffMembershipsUpdateStaffRole`
  - `staffMembershipsDeactivateStaffMember`
- Replaced messaging mock send flow with API-backed messaging:
  - `notificationsSendGymMessageRoute`
  - Note: backend does not provide a message-history list endpoint; UI now transparently shows session-only sent history.

### `frontend/apps/consumer-web`
- Added shared auth header helper:
  - `frontend/apps/consumer-web/src/lib/apiAuth.ts`
- Replaced home placeholder bookings with API-backed consumer activity:
  - `analyticsConsumerStats`
  - `analyticsConsumerClassHistory`
  - `bookingsGetConsumerQr`
- Replaced discover placeholder catalog with API-backed marketplace browse:
  - `marketplaceBrowseMarketplaceClasses`
- Replaced class detail placeholder with API-backed detail + booking actions:
  - `marketplaceViewMarketplaceClassDetails`
  - `bookingsBookWithMembership`
  - `marketplaceBookMarketplaceClassWithSubscription`
  - `bookingsBookPayPerClass`
  - `bookingsJoinWaitlist`
- Replaced memberships placeholders with API-backed memberships/subscription:
  - `staffMembershipsListConsumerMemberships`
  - `marketplaceViewMarketplaceSubscriptionStatus`
- Replaced profile placeholders with API-backed profile/history/payments:
  - `consumerAuthGetCurrentConsumerProfile`
  - `consumerAuthUpdateConsumerProfile`
  - `consumerAuthDeleteConsumerAccount`
  - `analyticsConsumerClassHistory`
  - `paymentsConsumerPaymentHistory`
- Replaced QR placeholder data with API token payload:
  - `bookingsGetConsumerQr`
- Wired referral send action via backend referral endpoints:
  - `marketplaceGetReferralLink`
  - `marketplaceTrackReferralSignup`
- Fixed auth error-path handling for non-2xx login responses:
  - `consumerAuthLoginConsumer` calls now propagate API errors correctly instead of showing token-shape fallback errors.
  - Updated in `frontend/apps/consumer-web/src/routes/auth/Login.tsx`

### `frontend/apps/consumer-mobile`
- Added shared auth header helper:
  - `frontend/apps/consumer-mobile/lib/apiAuth.ts`
- Replaced home placeholder bookings with API-backed consumer activity:
  - `analyticsConsumerStats`
  - `analyticsConsumerClassHistory`
- Replaced discover placeholder catalog with API-backed marketplace browse:
  - `marketplaceBrowseMarketplaceClasses`
- Replaced class detail placeholder with API-backed detail + booking actions:
  - `marketplaceViewMarketplaceClassDetails`
  - `bookingsBookWithMembership`
  - `marketplaceBookMarketplaceClassWithSubscription`
  - `bookingsBookPayPerClass`
  - `bookingsJoinWaitlist`
- Replaced memberships placeholders with API-backed memberships/subscription:
  - `staffMembershipsListConsumerMemberships`
  - `marketplaceViewMarketplaceSubscriptionStatus`
- Replaced QR placeholder payload generation with API-backed signed token:
  - `bookingsGetConsumerQr`
- Fixed token-only login state by hydrating stored profile post-login:
  - `consumerAuthGetCurrentConsumerProfile`
- Fixed login API error propagation for 4xx responses:
  - Updated in `frontend/apps/consumer-mobile/app/(auth)/login.tsx`

### `frontend/apps/gym-mobile`
- Added shared auth header helper:
  - `frontend/apps/gym-mobile/lib/apiAuth.ts`
- Replaced dashboard placeholder metrics with API-backed dashboard:
  - `analyticsGymOwnerDashboard`
- Replaced members placeholder list with API-backed membership roster:
  - `staffMembershipsListGymMembers`
- Replaced check-in placeholders with API-backed scan/search/manual flows:
  - `bookingsScanQr`
  - `bookingsSearchMembersForCheckIn`
  - `bookingsManualCheckIn`
  - Preserved offline SQLite queue fallback
- Replaced reports placeholders with API-backed analytics reports:
  - `analyticsRevenueReport`
  - `analyticsAttendanceReport`
  - `analyticsMembershipHealthReport`
- Replaced schedule placeholder with API-backed class session view:
  - `marketplaceBrowseMarketplaceClasses` (filtered to current gym)
- Fixed token-only login state by hydrating stored staff profile post-login:
  - `gymsGetMyGymProfile`
- Fixed login API error propagation for 4xx responses:
  - Updated in `frontend/apps/gym-mobile/app/(auth)/login.tsx`

### `frontend/apps/web` and `frontend/apps/gym-web`
- Added local dev API proxy fallback (`/api` -> backend target) to avoid silent auth failures when `VITE_API_BASE_URL` is not set:
  - `frontend/apps/web/vite.config.ts`
  - `frontend/apps/gym-web/vite.config.ts`
  - `frontend/apps/consumer-web/vite.config.ts`
- Fixed login API error propagation for 4xx responses:
  - `frontend/apps/web/src/routes/auth/Login.tsx`
  - `frontend/apps/gym-web/src/routes/auth/Login.tsx`

## Remaining mock/TODO surfaces

### Medium priority
- Consumer-web has no dedicated "list my bookings" endpoint yet.
  - Current home experience is API-backed via analytics + QR booking IDs.
  - Add explicit bookings list endpoint if cancel/manage-from-home is required.

## Backend Follow-ups
- `backend/app/api/deps.py` tenant access checks are now enforced for `get_current_gym`:
  - Superusers: full access
  - Non-superusers: must have active staff membership in target gym
- Remaining future hardening: migrate legacy `User`-based gym access to unified staff/consumer identity dependencies where applicable.
