# StudioLoop System Stabilization Plan

## Current Baseline

### Green
- Backend tests: `357 passed, 2 skipped`
- Backend ruff: passing
- Backend mypy: passing (`0 errors`)
- Frontend lint: passing
- Frontend type-check: passing
- Frontend tests: passing
- Auth E2E (`frontend/e2e/auth.spec.ts`): passing
- Gym web core operator pages are API-backed (dashboard, members, check-in, payments, instructor schedule)
- Consumer web core member pages are API-backed (home activity, discover, class detail booking, memberships, profile, QR)
- Gym web staff and messaging pages are API-backed (message history pending backend list endpoint)
- Consumer mobile core member pages are API-backed (home activity, discover, class detail booking, memberships, QR)
- Gym mobile core staff pages are API-backed (dashboard, members, check-in, reports, schedule)

### Red / Risky
- Legacy `User` and domain-specific auth identities still coexist; dependency migration to a single identity model remains a long-term cleanup item.

## Findings by Severity

### P0 (blocks real local usage)
- Gym mobile login endpoint was not wired (hard throw in mutation).
  - Fixed in `frontend/apps/gym-mobile/app/(auth)/login.tsx`
- CORS did not allow all local web app origins (`5174`, `5175`).
  - Fixed in `backend/app/core/config.py`
  - Guardrail test added in `backend/tests/api/test_cors.py`
- Web app post-login route loop (`/` redirected back to login).
  - Fixed by protected home route in `frontend/apps/web/src/App.tsx`
- Web app dev servers had no `/api` proxy fallback, so local login failed when `VITE_API_BASE_URL` was unset.
  - Fixed in:
  - `frontend/apps/web/vite.config.ts`
  - `frontend/apps/gym-web/vite.config.ts`
  - `frontend/apps/consumer-web/vite.config.ts`

### P1 (high probability user-facing breaks)
- Dead route links in web auth flow.
  - Added missing pages/routes:
  - `frontend/apps/web/src/routes/auth/ForgotPassword.tsx`
  - `frontend/apps/web/src/routes/auth/ResendVerification.tsx`
  - `frontend/apps/web/src/routes/Terms.tsx`
  - `frontend/apps/web/src/routes/Privacy.tsx`
- Consumer mobile linked to missing auth routes.
  - Added:
  - `frontend/apps/consumer-mobile/app/(auth)/forgot-password.tsx`
  - `frontend/apps/consumer-mobile/app/(auth)/resend-verification.tsx`
  - Updated stack in `frontend/apps/consumer-mobile/app/(auth)/_layout.tsx`
- Consumer-web registration error code mismatch.
  - Fixed `EMAIL_ALREADY_REGISTERED` -> `EMAIL_ALREADY_EXISTS` in `frontend/apps/consumer-web/src/routes/auth/Register.tsx`
- Mobile login stored only tokens and not profile context needed by tabs.
  - Fixed in:
  - `frontend/apps/consumer-mobile/app/(auth)/login.tsx`
  - `frontend/apps/gym-mobile/app/(auth)/login.tsx`
- Login flows depended on non-throwing generated client behavior and produced false "missing tokens" errors on 4xx responses.
  - Fixed by explicit error propagation (`throwOnError` + `response.error` guard) in:
  - `frontend/apps/web/src/routes/auth/Login.tsx`
  - `frontend/apps/consumer-web/src/routes/auth/Login.tsx`
  - `frontend/apps/gym-web/src/routes/auth/Login.tsx`
  - `frontend/apps/consumer-mobile/app/(auth)/login.tsx`
  - `frontend/apps/gym-mobile/app/(auth)/login.tsx`
  - Extended same hardening to registration and recovery flows:
  - `frontend/apps/web/src/routes/auth/Register.tsx`
  - `frontend/apps/consumer-web/src/routes/auth/Register.tsx`
  - `frontend/apps/consumer-mobile/app/(auth)/register.tsx`
  - `frontend/apps/web/src/routes/auth/ForgotPassword.tsx`
  - `frontend/apps/consumer-web/src/routes/auth/ForgotPassword.tsx`
  - `frontend/apps/consumer-mobile/app/(auth)/forgot-password.tsx`
  - `frontend/apps/web/src/routes/auth/ResendVerification.tsx`
  - `frontend/apps/consumer-mobile/app/(auth)/resend-verification.tsx`
  - Added auth E2E coverage for invalid credentials and duplicate-email registration in `frontend/e2e/auth.spec.ts`
- Consumer-web auth state was hook-instance local, allowing guard/layout desync on logout/login updates.
  - Fixed by moving `useAuth` to shared storage subscription semantics in:
  - `frontend/apps/consumer-web/src/hooks/useAuth.ts`
  - Added logout redirect/token-clear regression coverage:
  - `frontend/apps/consumer-web/src/App.test.tsx`
  - `frontend/apps/gym-web/src/App.test.tsx`
- Expired-session behavior was not centralized; apps could remain in a stale authenticated state after backend `401` responses.
  - Added API-client `401` interceptors to clear local auth state and redirect to login in:
  - `frontend/apps/web/src/lib/configureApiClient.ts`
  - `frontend/apps/consumer-web/src/lib/configureApiClient.ts`
  - `frontend/apps/gym-web/src/lib/configureApiClient.ts`
  - Extended same pattern to mobile apps with app-level session-expiry events:
  - `frontend/apps/consumer-mobile/lib/configureApiClient.ts`
  - `frontend/apps/gym-mobile/lib/configureApiClient.ts`
  - `frontend/apps/consumer-mobile/lib/authSession.ts`
  - `frontend/apps/gym-mobile/lib/authSession.ts`
  - `frontend/apps/consumer-mobile/app/_layout.tsx`
  - `frontend/apps/gym-mobile/app/_layout.tsx`
  - Added mobile unit coverage:
  - `frontend/apps/consumer-mobile/__tests__/authSession.test.ts`
  - `frontend/apps/gym-mobile/__tests__/authSession.test.ts`
- Added one-time refresh-token retry on `401` for web clients before forced logout:
  - `frontend/apps/web/src/lib/configureApiClient.ts`
  - `frontend/apps/consumer-web/src/lib/configureApiClient.ts`
  - `frontend/apps/gym-web/src/lib/configureApiClient.ts`
  - Added unit coverage for refresh/retry and refresh-failure logout:
  - `frontend/apps/consumer-web/src/lib/configureApiClient.test.ts`
  - `frontend/apps/gym-web/src/lib/configureApiClient.test.ts`
- Consumer discover route could white-screen due to filtering undefined query data during first render.
  - Fixed in `frontend/apps/consumer-web/src/routes/discover/Discover.tsx` (`classesQuery.data ?? []` safeguard).
- Additional first-render crash risks from direct `query.data` usage before hydration.
  - Fixed with null-safe defaults in:
  - `frontend/apps/gym-web/src/routes/members/MemberList.tsx`
  - `frontend/apps/gym-web/src/routes/staff/StaffManagement.tsx`
  - `frontend/apps/gym-web/src/routes/payments/Payments.tsx`
  - `frontend/apps/consumer-web/src/routes/profile/Profile.tsx`
  - `frontend/apps/consumer-web/src/routes/memberships/Memberships.tsx`
- Gym staff session parsing required `id`, but login payload persists only `role` + `gym_id`, causing missing tenant context and skipped dashboard/payment queries.
  - Fixed parser contract in `frontend/apps/gym-web/src/lib/apiAuth.ts`
  - Added regression test: `frontend/apps/gym-web/src/lib/apiAuth.test.ts`
- Consumer profile mutations lacked explicit error handling; update/delete failures were silent to users.
  - Added user-visible mutation error states and strict error propagation in:
  - `frontend/apps/consumer-web/src/routes/profile/Profile.tsx`
- Playwright app servers could auto-shift ports, causing cross-app E2E misrouting.
  - Enforced strict ports in `frontend/playwright.config.ts` webServer commands.

### P2 (stability and maintainability)
- API base URL hardcoding and per-app divergence.
  - Added client configuration hooks:
  - `frontend/apps/web/src/lib/configureApiClient.ts`
  - `frontend/apps/consumer-web/src/lib/configureApiClient.ts`
  - `frontend/apps/consumer-mobile/lib/configureApiClient.ts`
- Backend quality gate mismatch: tests pass while mypy fails heavily.
  - Hotspots:
  - `backend/app/api/routes/marketplace.py`
  - `backend/app/api/routes/staff_memberships.py`
  - `backend/app/api/routes/gyms.py`
  - `backend/app/api/routes/bookings.py`
  - `backend/app/api/routes/admin.py`
- Gym access validation in `get_current_gym` was permissive and user-model based.
  - Fixed in `backend/app/api/deps.py` by migrating to staff identity (`CurrentStaff`) and strict tenant checks.
  - Covered by dependency tests in `backend/tests/api/test_deps.py` and route-level cross-tenant tests:
  - `backend/tests/api/routes/test_analytics.py`
  - `backend/tests/api/routes/test_payments.py`
  - `backend/tests/api/routes/test_notifications.py`
- Remaining non-admin `CurrentUser` usages are legacy user-domain endpoints (`users`, `items`, `login`) and are intentionally not gym-tenant scoped.

## Execution Plan

### Phase 1: Auth and Local Testability (completed)
- [x] Fix login runtime blockers (web + gym-mobile + CORS)
- [x] Restore/enable auth E2E coverage for current routes
- [x] Remove dead auth links by adding missing routes/screens
- [x] Add route-level auth smoke tests for web, consumer-web, gym-web

### Phase 2: API Contract Convergence
- [x] Regenerate API client from current backend OpenAPI
- [x] Remove manual fetch fallbacks where SDK coverage exists
- [x] Add contract tests asserting expected auth endpoints in generated SDK
- [x] Enforce base URL injection pattern in all apps

### Phase 3: Backend Type-Safety Hardening (completed)
- [x] Tackle mypy errors module-by-module (`117 -> 0`)
- [x] Normalize SQLModel/SQLAlchemy typing patterns (`.is_()`, `.asc()`, `.desc()`, joins)
- [ ] Add CI gate for mypy with an explicit temporary allowlist and burn-down target

### Phase 4: Placeholder and Mock Removal
- [~] Replace mock dashboard/payments/schedule/member data with API-backed queries
- [x] `gym-web` dashboard -> `analyticsGymOwnerDashboard` + payment action items
- [x] `gym-web` members -> `staffMembershipsListGymMembers`
- [x] `gym-web` check-in -> `bookingsSearchMembersForCheckIn` + `bookingsManualCheckIn`
- [x] `gym-web` payments -> `paymentsGymPaymentDashboard` + failed items + payout report
- [x] `gym-web` schedule -> `staffMembershipsGetInstructorSchedule` (role-gated, no fallback mock)
- [x] `gym-web` staff -> list/add/update/deactivate staff APIs
- [x] `gym-web` messaging -> send gym message API (session-only history until backend list endpoint exists)
- [x] `consumer-web` home -> `analyticsConsumerStats` + `analyticsConsumerClassHistory` + `bookingsGetConsumerQr`
- [x] `consumer-web` discover/class detail -> marketplace browse/details + booking/waitlist APIs
- [x] `consumer-web` memberships -> consumer memberships + marketplace subscription status
- [x] `consumer-web` profile -> profile update/delete + class history + payment history
- [x] Replace TODO mobile data flows with real endpoints
- [x] Add end-to-end user journeys per app (login -> core action -> logout)
  - `frontend/e2e/consumer-journey.spec.ts` (login -> discover -> class detail -> booking -> logout)
  - `frontend/e2e/gym-journey.spec.ts` (staff login -> member search -> manual check-in -> logout)
  - Added auth-expiry failure-path assertions:
  - consumer: `401` + refresh failure redirects to `/login`
  - gym: `401` + refresh failure redirects to `/login`
  - Added gym payments E2E coverage:
  - `frontend/e2e/gym-payments.spec.ts` (payments dashboard metrics + failed tab + payout breakdown + backend error banner)
  - Added consumer profile E2E coverage:
  - `frontend/e2e/consumer-profile.spec.ts` (profile update success, account delete success, mutation failure messaging)

## Next Two Recommended Workstreams

1. Add focused E2E around consumer memberships/profile data consistency after token refresh and re-auth.
2. Add backend endpoints for consumer booking list/history-by-booking and gym message list to remove remaining UI fallback states.
