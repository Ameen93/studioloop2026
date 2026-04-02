# StudioLoop — Per-App Production Readiness Audits

**Created:** 2026-03-16
**Companion to:** [PRODUCTION-READINESS.md](./PRODUCTION-READINESS.md)

---

## Table of Contents

1. [Backend API](#1-backend-api)
2. [Admin Web (apps/web)](#2-admin-web-appsweb)
3. [Gym Web (apps/gym-web)](#3-gym-web-appsgym-web)
4. [Consumer Web (apps/consumer-web)](#4-consumer-web-appsconsumer-web)
5. [Consumer Mobile (apps/consumer-mobile)](#5-consumer-mobile-appsconsumer-mobile)
6. [Gym Mobile (apps/gym-mobile)](#6-gym-mobile-appsgym-mobile)
7. [Marketing — Consumers (apps/marketing-consumers)](#7-marketing--consumers)
8. [Marketing — Gyms (apps/marketing-gyms)](#8-marketing--gyms)

---

## 1. Backend API

**Path:** `backend/`
**Stack:** FastAPI + SQLModel + PostgreSQL 17 + Alembic
**Deploy:** Railway (Docker), planned Fly.io JNB
**Readiness: 70% — strong foundations, critical payment logic flaws**

### What's Working Well

- **18 route modules, 100+ endpoints** — all fully implemented, no stubs or `NotImplementedError`
- **ORM safety** — no raw SQL anywhere, all queries through SQLModel/SQLAlchemy
- **Multi-tenancy isolation** — `GymScopedRepository` enforces `gym_id` filtering automatically; no cross-tenant data leaks found
- **Custom exception hierarchy** — consistent `{ error: { code, message, details } }` format across all error responses
- **26 clean Alembic migrations** — linear chain, no branching, all have upgrade + downgrade
- **24 test files / 9,489 lines** — real database integration tests, no mocking, no skipped tests
- **Config validation** — Pydantic Settings fails fast on missing required vars; rejects `"changethis"` secrets in production
- **Dockerfile** — production-grade with `python:3.12-slim`, multi-layer caching, `uv sync --frozen`, 4 workers
- **Webhook verification** — Svix HMAC-SHA256 with 5-minute timestamp window for payment webhooks
- **Password security** — Argon2 primary + bcrypt legacy fallback, token versioning for session invalidation

### Blockers

| # | Issue | Location | Fix |
|---|-------|----------|-----|
| P0 | **Memberships activate before payment** | `api/routes/staff_memberships.py:580-631` | Add `pending_payment` state; activate only from webhook |
| P0 | **Marketplace subscriptions activate before payment** | `api/routes/marketplace.py:433-466` | Create unpaid intent; activate after verified payment |
| P0 | **Pay-per-class trusts client-supplied amount** | `api/routes/bookings.py:216-247` | Derive price server-side, require payment before booking |
| P0 | **Payment initiation trusts client price + entity IDs** | `api/routes/payments.py:222-296` | Server-side amount derivation, validate entity ownership |
| P0 | **Public webhook signature oracle** | `api/routes/payments.py:765-769` | Remove or restrict to local env |
| P0 | **Public retry worker trigger** | `api/routes/payments.py:612-641` | Restrict to admin/internal |
| P0 | **Stub payment providers on default path** | `core/config.py:151-165`, `services/payments/providers.py:41-120` | Require `PAYMENT_PROVIDER=stitch` in production |
| CRIT | **Apple ID token decoded without signature verification** | `api/routes/staff_auth.py:652`, check consumer routes too | Verify with Apple's public keys |
| CRIT | **Unauthenticated `/private/users/` endpoint** | `api/routes/private.py:23-38` | Add runtime env guard, not just import-time exclusion |

### High Priority

| Issue | Location | Fix |
|-------|----------|-----|
| No rate limiting on any endpoint | Entire backend | Add `slowapi` — priority: login, registration, password reset, webhooks |
| Missing security headers | `main.py` | Add middleware: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Referrer-Policy` |
| API docs exposed in production | `main.py:21` | Set `docs_url=None`, `redoc_url=None`, `openapi_url=None` when `ENVIRONMENT == "production"` |
| Stitch webhook falls back to SECRET_KEY | `services/payments/stitch.py:302` | Require `STITCH_WEBHOOK_SECRET` in non-local envs |
| SECRET_KEY auto-generates on startup | `core/config.py:37` | Add validator requiring explicit key in staging/production |
| Admin routes use manual `_require_superuser()` | `api/routes/admin.py:51-61` | Convert to `Depends()` pattern |
| Payment URLs accept `str` not `HttpUrl` | `api/routes/payments.py:34-36` | Use Pydantic `HttpUrl` type |
| CORS allows all methods/headers | `main.py:28-33` | Restrict to specific methods |

### Gaps

| Area | Status | Notes |
|------|--------|-------|
| Test coverage — `admin.py` | Missing | Platform admin operations entirely untested |
| Test coverage — `realtime.py` | Missing | WebSocket endpoints not tested |
| Background job queue | Not implemented | Email is synchronous (blocking), payment retries need scheduler, POPIA 30-day account deletion has no cleanup job |
| Structured logging | Basic only | No JSON formatter, no request/response logging, no performance metrics |
| Health check | Shallow | Returns 200 always — doesn't verify DB connectivity at runtime |
| Dockerfile | Near-complete | Missing `USER nonroot` directive (runs as root), missing `HEALTHCHECK` instruction |
| OpenAPI error docs | Incomplete | Error responses (400/401/403/404) not documented in `responses={}` |

### Dependencies

All production deps are current and properly pinned. Dev deps isolated in separate `[dependency-groups]`. Lock file (`uv.lock`) committed for reproducibility.

---

## 2. Admin Web (`apps/web`)

**Stack:** React 19 + Vite + React Router v7 + Tailwind v4
**Deploy:** Vercel (`sl-admin-eta.vercel.app`)
**Port:** 5173 (dev)
**Readiness: 30% — auth works, no admin functionality**

### Current State

This app is **not an admin dashboard** — it's a consumer auth portal. It implements login/register/forgot-password and nothing else.

### All Routes

| Route | Status | Notes |
|-------|--------|-------|
| `/auth/login` | Production | Email/password login for consumers |
| `/auth/register` | Production | Consumer registration with validation |
| `/auth/forgot-password` | Production | Password reset request |
| `/auth/resend-verification` | Production | Resend email verification |
| `/auth/verify-email` | Production | Token-based email verification |
| `/auth/verify-email-sent` | Production | Confirmation screen |
| `/` (Home) | **Stub** | Shows "You are signed in" + logout button only |
| `/terms` | **Placeholder** | Hardcoded text: "Local development placeholder. Replace with final legal content before production." |
| `/privacy` | **Placeholder** | Same placeholder text |

### What's Working

- Clean auth flow with generated API client (`@sl/api-client`)
- Token refresh with 401 interceptor and deduplication
- Client-side form validation (email regex, 8-char password)
- Route guard (`AuthGuard`) redirects unauthenticated users
- Responsive design with Tailwind breakpoints
- All tests passing (6 unit tests for auth flow)
- Builds cleanly — 287KB JS (88KB gzipped), no TypeScript errors, no lint errors
- No console.log, no mock data, no hardcoded URLs

### Blockers

| Issue | Location | Fix |
|-------|----------|-----|
| **Home page is a stub** — no admin dashboard | `src/routes/Home.tsx` | Build actual admin dashboard (gym management, user management, analytics, platform health) |
| **Terms page is placeholder** | `src/routes/Terms.tsx:6-7` | Replace with reviewed legal content |
| **Privacy page is placeholder** | `src/routes/Privacy.tsx:6-8` | Replace with reviewed POPIA-compliant privacy policy |
| **No global error boundary** | `src/App.tsx` | Add React ErrorBoundary wrapper — unhandled errors crash the app |

### Gaps

| Area | Status |
|------|--------|
| Admin features (gym management, user mgmt, analytics) | Not built |
| Global error boundary | Missing |
| Accessibility (ARIA labels, focus management) | Missing |
| Token storage | localStorage (XSS risk — see main doc H2) |

### Missing Admin Features

This app should have (based on Epic 11 — Platform Administration):
- Gym application review and approval
- Consumer complaint handling
- Account credit issuance
- Platform health monitoring
- Gym-level data access for support
- Audit log viewer

None of these exist in the frontend yet — backend endpoints exist but have no UI.

---

## 3. Gym Web (`apps/gym-web`)

**Stack:** React 19 + Vite + React Router v7 + Tailwind v4
**Deploy:** Vercel (`sl-gym.vercel.app`)
**Port:** 5174 (dev)
**Readiness: 70% — most features work, 3 pages are stubs**

### All Routes

| Route | Status | Notes |
|-------|--------|-------|
| `/login` | Production | Email/password + Google/Apple OAuth |
| `/auth/oauth-callback` | Production | OAuth token parsing from hash fragment |
| `/dashboard` | Production | Real API data — today's check-ins, bookings, active members, failed payment items |
| `/members` | Production | Real API — search, filters, loading/error/empty states |
| `/members/:memberId` | **Mock data** | Hardcoded member "Thabo Mokoena" — comment says "will be replaced with TanStack Query" |
| `/schedule` | Production | Real data but **uses manual `fetch()` instead of generated client** |
| `/checkin` | Production | Manual search + check-in via API |
| `/reports` | **All mock data** | Revenue (R 87,450), attendance (47 today), membership, class performance, staff — all hardcoded |
| `/staff` | Production | Full CRUD — add, deactivate, change roles via API |
| `/settings` | **Stub** | All forms have hardcoded `defaultValue` ("FitZone Sandton"), buttons don't save |
| `/messaging` | Production | Send in-app, email, WhatsApp, push messages |
| `/payments` | Production | Failed payment dashboard, marketplace payouts |

### What's Working

- Auth: email/password + OAuth with proper token refresh and deduplication
- Token storage: `gym_staff_access_token`, `gym_staff_refresh_token`, `gym_staff_info` in localStorage
- API integration: 9/10 pages use generated `@sl/api-client` correctly
- Error handling: all production pages show loading, error, and empty states
- Staff management: full add/deactivate/role-change lifecycle
- Dashboard: real-time metrics from API
- No console.log statements, no debug code

### Blockers

| # | Issue | Location | Fix |
|---|-------|----------|-----|
| 1 | **Member detail page uses mock data** | `routes/members/MemberDetail.tsx:14-41` | Replace with API calls for member details, attendance, payments |
| 2 | **Reports page is all hardcoded numbers** | `routes/reports/Reports.tsx:20-226` | Wire up to analytics API endpoints |
| 3 | **Settings page is non-functional** | `routes/settings/Settings.tsx` | Connect forms to gym settings API endpoints, add save handlers |
| 4 | **Schedule uses manual `fetch()`** | `routes/schedule/Schedule.tsx:98` | Replace with generated API client — bypasses token refresh |
| 5 | **No global error boundary** | `App.tsx` | Add React ErrorBoundary wrapper |

### Gaps

| Area | Status |
|------|--------|
| Schedule calendar responsive on mobile | Hard `grid-cols-7` — overflows on phones |
| Settings form validation | No min/max on numeric inputs |
| Token storage | localStorage (XSS risk) |
| Accessibility | Limited ARIA support |

---

## 4. Consumer Web (`apps/consumer-web`)

**Stack:** React 19 + Vite + React Router v7 + Tailwind v4
**Deploy:** Vercel (`sl-consumer.vercel.app`)
**Port:** 5175 (dev)
**Readiness: 85% — most complete web app, minor gaps**

### All Routes

| Route | Status | Notes |
|-------|--------|-------|
| `/login` | Production | Email/password + Google/Apple OAuth |
| `/register` | Production | Full form with SA phone validation (+27) |
| `/forgot-password` | Production | Email submission + confirmation |
| `/auth/oauth-callback` | Production | OAuth token extraction from fragment |
| `/` (Home) | Production | Activity dashboard, class history, QR shortcut |
| `/discover` | Production | Marketplace class browsing with type/search filters |
| `/discover/:classId` | Production | Full class details + 3 booking methods + waitlist |
| `/discover/:classId/share` | Production | Copy link, native share, email referral, social (WhatsApp/Twitter/Facebook) |
| `/discover/studio/:gymId` | Production | Gym profile + membership plans + waiver + enroll |
| `/bookings` | Production | Tabbed: upcoming/past/cancelled + cancel functionality |
| `/wallet` | Production | Subscription status, memberships, quick actions |
| `/memberships` | Production | Gym + marketplace subscription tabs |
| `/profile` | Production | 5 sections: edit profile, notifications, class history, payments, delete account |
| `/qr-code` | Production | Custom SVG QR generator with token + expiry |

### What's Working

- **13 pages, all fully implemented** — no stubs or placeholder content
- 100% generated API client usage — zero manual `fetch()` calls
- Complete booking flow: membership, subscription, pay-per-class, waitlist join
- Membership enrollment with digital waiver acceptance
- Sharing: copy link, Web Share API, email referral, social links
- Custom QR code generation with real token from API
- Profile with POPIA-compliant account deletion
- Payment history (read-only, PCI-compliant — no card data in frontend)
- Mobile-first responsive design with bottom nav on small screens
- Token refresh with 401 interceptor and concurrent-request deduplication
- Cross-tab auth sync via `sl:consumer-auth-change` custom event

### Minor Gaps

| Issue | Location | Fix |
|-------|----------|-----|
| QR code uses custom hash format, not ISO 18004 | `routes/QRCode.tsx:6-43` | Verify gym staff app decoder matches this format |
| Notification preference toggles not persisted to backend | `routes/profile/Profile.tsx:259-288` | Add API mutation for notification preferences |
| No global error boundary | `App.tsx` | Add React ErrorBoundary |
| Token storage | localStorage | XSS risk (see main doc H2) |
| Accessibility | No ARIA labels | Add before public launch |

### Payment Flow Note

The consumer web app correctly delegates payment processing to the backend (Stitch redirect). However, the **backend payment logic has P0 issues** (client-trusted amounts, activation before payment) documented in the main readiness doc. These affect all frontends.

---

## 5. Consumer Mobile (`apps/consumer-mobile`)

**Stack:** Expo 54 + React Native 0.81 + Expo Router + NativeWind v4 + MMKV
**Bundle ID:** `com.studioloop.consumer`
**Scheme:** `studioloop-consumer://`
**Readiness: 85% — feature-complete, needs push + crash reporting**

### All Screens

| Screen | Status | Notes |
|--------|--------|-------|
| Auth router (`index.tsx`) | Production | MMKV token check, redirects to auth or tabs |
| Login | Production | Email/password + Google/Apple OAuth via expo-web-browser |
| Register | Production | Full form with validation |
| Forgot Password | Production | Password reset flow |
| Verify Email / Resend | Production | Post-registration flow |
| Home Tab | Production | Class history, stats (FlatList) |
| Discover Tab | Production | Browse marketplace classes (FlatList + search) |
| Wallet Tab | Production | Subscription status, memberships, quick actions |
| Memberships Tab | Production | Gym + marketplace subscription tabs |
| QR Code Tab | Production | **Offline QR display** — cached via MMKV, shows "Available offline" badge |
| Profile Tab | Production | Profile, notification preferences, logout |
| Class Detail | Production | Dynamic route `/class/[id]` |
| Studio Detail | Production | Dynamic route `/studio/[id]` |

### What's Working

- **All screens fully implemented** — no stubs
- Token storage in MMKV (encrypted at rest, correct for mobile)
- OAuth via expo-web-browser (system browser, not WebView — secure)
- **Offline QR code**: cached in MMKV, falls back gracefully when offline, shows last-updated timestamp
- TanStack Query v5 with 5-minute staleTime
- API client from `@sl/api-client` — no manual fetch
- Session expiry event emitter pattern for 401 handling
- New Architecture enabled (`newArchEnabled: true`)

### Blockers

| # | Issue | Location | Fix |
|---|-------|----------|-----|
| 1 | **Push notification token not registered with backend** | `lib/notifications.ts:55` | After `getExpoPushTokenAsync()`, call backend registration endpoint |
| 2 | **Notification preferences stored locally only** | `app/(tabs)/profile.tsx:23-25` | Add API mutation to sync toggles to backend |
| 3 | **No error boundary / crash reporting** | Root layout | Add React error boundary + Sentry integration |
| 4 | **App store metadata missing** | `app.json` | Add description, privacy policy URL, category |

### Gaps

| Area | Status | Notes |
|------|--------|-------|
| Push notifications | Framework ready, backend integration missing | Token obtained but not sent to server |
| Biometric auth | Not implemented | No PIN/Face ID for sensitive operations |
| Certificate pinning | Not implemented | MITM risk on compromised devices |
| QR cache expiration | No expiry logic | Cached QR could become stale |
| EAS production profile | Minimal | Missing signing config, distribution type |

### EAS Config (`eas.json`)

```
development  → APK (Android), simulator (iOS)
preview      → APK (Android), simulator (iOS)
production   → autoIncrement: true (minimal — needs signing config)
```

Missing for store submission: iOS signing certificate, Android keystore, distribution type ("store").

---

## 6. Gym Mobile (`apps/gym-mobile`)

**Stack:** Expo 54 + React Native 0.81 + Expo Router + NativeWind v4 + MMKV + expo-camera + expo-sqlite
**Bundle ID:** `com.studioloop.gym`
**Scheme:** `studioloop-gym://`
**Readiness: 80% — feature-complete, offline sync gap**

### All Screens

| Screen | Status | Notes |
|--------|--------|-------|
| Auth router (`index.tsx`) | Production | MMKV token check with gym context |
| Staff Login | Production | Email/password + Google/Apple OAuth, stores role + gym_id |
| Dashboard | Production | Check-ins today, active members, revenue, **offline pending count** |
| Check-in Tab | Production | **QR camera scanner + manual search**, offline queueing |
| Schedule Tab | Production | Today's classes (FlatList) |
| Members Tab | Production | Gym member roster with search |
| Reports | Production | Revenue, attendance, membership health from API |

### What's Working

- **All screens fully implemented** — no stubs
- **QR scanner**: expo-camera CameraView with barcode filter (`['qr']`), permission handling, fallback to manual search
- **Offline check-in queue**: expo-sqlite `pending_checkins` table, stores check-ins when offline, shows pending count on dashboard
- QR payload parsing: handles both signed token format and JSON `{ type: "studioloop_checkin", consumer_id: "..." }`
- Token storage: MMKV with extended staff profile (role, gym_id, gym_name)
- OAuth: handles `NO_STAFF_ACCOUNT` error with user-friendly message
- TanStack Query v5 with 2-minute staleTime (fresher for staff operations)

### Blockers

| # | Issue | Location | Fix |
|---|-------|----------|-----|
| 1 | **Offline sync never triggers** — `syncPendingCheckins()` defined but never called | `lib/offline-checkin.ts:133-158` | Add sync trigger: on successful online check-in, on app foreground, or manual "Sync" button |
| 2 | **Push notification token not registered with backend** | `lib/notifications.ts` | Same as consumer app |
| 3 | **No error boundary / crash reporting** | Root layout | Add error boundary + Sentry |
| 4 | **Camera permission has no "try again" option** | `app/(tabs)/checkin.tsx:146-158` | Add retry button after permission denial |

### Gaps

| Area | Status | Notes |
|------|--------|-------|
| Offline sync | Queue works, sync never fires | Critical gap for production reliability |
| Push notifications | Framework ready, no backend integration | Same issue as consumer |
| Biometric auth | Not implemented | |
| Certificate pinning | Not implemented | |
| EAS production profile | Minimal | Same as consumer — needs signing config |

### Camera Permissions

- iOS: `NSCameraUsageDescription` in `infoPlist` ("Camera access is needed to scan member QR codes for check-in")
- Android: declared in expo-camera plugin config
- Runtime: `useCameraPermissions()` hook with request prompt
- Fallback: manual search if camera denied

---

## 7. Marketing — Consumers

**Path:** `apps/marketing-consumers/`
**Stack:** Astro 5 (static output)
**Deploy:** Vercel (manual — NOT in CI/CD pipeline)
**Readiness: 25% — design is polished, infrastructure is missing**

### Pages

Single page: `src/pages/index.astro` (429 lines)

**Content quality: Good** — real marketing copy, not placeholder:
- Hero: "Train where you want, not where your membership is locked."
- How it works (3 steps)
- Browse by neighborhood (Cape Town: Sea Point, Woodstock, Green Point, Observatory)
- 8 workout categories with AI-generated images
- 2 testimonials with headshots
- Early access/waitlist section

### What's Working

- Polished visual design with AI-generated assets (Flux Schnell via ComfyUI)
- All images have `loading="lazy"` (except hero = `"eager"`), `decoding="async"`, proper dimensions
- Responsive: CSS Grid with `auto-fit`, mobile breakpoint at 720px, fluid typography with `clamp()`
- Static output — fast, CDN-friendly

### Blockers

| # | Issue | Fix |
|---|-------|-----|
| 1 | **All forms are non-functional** — buttons with `type="button"` and no handlers | Wire up form submissions to backend API or email service (Resend, SendGrid) |
| 2 | **No privacy policy page** | Create `/privacy` route with POPIA-compliant content |
| 3 | **No terms of service page** | Create `/terms` route |
| 4 | **Not in CI/CD pipeline** | Add to `.github/workflows/deploy.yml` |

### Gaps

| Area | Status |
|------|--------|
| SEO: Open Graph tags | Missing |
| SEO: sitemap.xml | Missing |
| SEO: robots.txt | Missing |
| SEO: JSON-LD structured data | Missing |
| SEO: canonical URL | Missing |
| Analytics (GA4/Plausible) | None |
| Contact info / footer | Missing |
| Pricing details | Generic copy only — no plans, no prices |
| Additional pages (blog, help, FAQ) | None |
| Components | Empty directory — everything inlined in single page |

### Assets

All images AI-generated and tracked in `public/assets/marketing/manifest.json`:
- 2 hero images (1536x768)
- 8 workout type images (1024x1024)
- 5 testimonial headshots (768x1024, FaceRealism LoRA)
- 2 lifestyle images
- 3 gym interior mockups (1536x768)

### Astro Config

```js
output: 'static'
site: process.env.SITE_URL || 'https://app.studioloop.co.za'
publicDir: '../../public'  // shared assets
```

No integrations (no sitemap plugin, no i18n, no image optimization).

---

## 8. Marketing — Gyms

**Path:** `apps/marketing-gyms/`
**Stack:** Astro 5 (static output)
**Deploy:** Vercel (manual — NOT in CI/CD pipeline)
**Readiness: 25% — same gaps as consumer marketing site**

### Pages

Single page: `src/pages/index.astro` (548 lines)

**Content quality: Good** — B2B copy for gym operators:
- Hero: "Replace spreadsheet chaos with one operating system for your gym."
- The Problem section (stressed owner imagery)
- 4 features: member management, class scheduling, payment visibility, marketplace controls
- ROI metrics: 15h→<5h admin, >95% payment collection, >40% off-peak fill
- 3 testimonials with specific results ("saved us R12,000")
- 3 gym types (boutique studios, crossfit boxes, traditional gyms)
- FAQ (3 questions)
- Demo booking form

### What's Working

- Strong B2B messaging with specific ROI claims
- AI-generated assets (shared with consumer site)
- Responsive design
- Static output

### Blockers

Same as consumer marketing site:
| # | Issue | Fix |
|---|-------|-----|
| 1 | **Demo request form is non-functional** | Wire up to backend or email service |
| 2 | **No privacy policy page** | Create route |
| 3 | **No terms of service page** | Create route |
| 4 | **Not in CI/CD pipeline** | Add to deploy workflow |

### Gaps

Same gaps as consumer marketing site (SEO, analytics, contact info, pricing details).

### Design Differences from Consumer Site

| Aspect | Consumer (B2C) | Gyms (B2B) |
|--------|---------------|------------|
| Typography | Outfit + Manrope | Space Grotesk + Manrope |
| Colors | Coral/orange (`#c2410c` — `#ea580c`) | Blue/teal (`#1d4ed8` — `#0f766e`) |
| CTA focus | "Get the App" / waitlist | "Book Demo" / pricing call |

### Astro Config

```js
output: 'static'
site: process.env.SITE_URL || 'https://manage.studioloop.co.za'
publicDir: '../../public'  // shared assets
```

---

## Cross-App Summary

### Readiness Scores

| App | Score | Blocking Issues |
|-----|-------|-----------------|
| Backend API | 70% | P0 payment logic (activate before pay), Apple token verification, rate limiting, security headers |
| Admin Web | 30% | No admin functionality — auth portal only, placeholder legal pages |
| Gym Web | 70% | 3 pages with mock/stub data (member detail, reports, settings) |
| Consumer Web | 85% | Minor: notification prefs not persisted, no error boundary |
| Consumer Mobile | 85% | Push token not registered, no crash reporting, EAS signing not configured |
| Gym Mobile | 80% | Offline sync never fires, push token not registered, no crash reporting |
| Marketing (Consumers) | 25% | Forms don't submit, no legal pages, no SEO, no analytics, not in CI/CD |
| Marketing (Gyms) | 25% | Same as consumer marketing |

### Issues That Affect ALL Apps

| Issue | Impact | Fix |
|-------|--------|-----|
| Payment activation before verification | All booking/enrollment flows create false paid state | Backend payment state machine rework |
| No privacy policy | Legal blocker for every app | Write POPIA-compliant policy, create pages in all apps |
| No terms of service | Legal blocker | Write terms, create pages |
| No error boundaries (frontend) | Unhandled JS errors crash apps with no recovery | Add ErrorBoundary wrappers in all React apps |
| localStorage token storage (web) | XSS can steal tokens from all 3 web apps | Migrate to httpOnly cookies or implement strict CSP |

### Shared Dependencies Health

| Package | Status |
|---------|--------|
| `@sl/api-client` | Healthy — generated from OpenAPI, used by all frontends |
| `@sl/ui` | Healthy — shared Button, Input, Card, Modal |
| `@sl/utils` | Healthy — shared utilities |
| TanStack Query v5 | Current (`5.90.19`) |
| React 19.1.0 | Current |
| React Router 7.12.0 | Current (7.13.1 available, minor) |
| Expo 54 | Current |
| React Native 0.81 | Current |

### Recommended Work Order

**Phase 1 — Security & Payment (Backend)**
1. Fix payment state machine (P0s: activate only after verified webhook)
2. Lock down exposed payment helper endpoints
3. Fix Apple token verification
4. Add rate limiting + security headers
5. Disable production API docs

**Phase 2 — Legal & Infrastructure**
6. Write privacy policy + terms of service
7. Create legal pages in all apps (web, mobile, marketing)
8. Set up official `@studioloop.co.za` accounts (see main doc)
9. Configure DNS + custom domains

**Phase 3 — Frontend Completion**
10. Build admin dashboard (admin web)
11. Replace mock data in gym-web (member detail, reports, settings)
12. Add error boundaries to all React apps
13. Wire up marketing site forms

**Phase 4 — Mobile Store Prep**
14. Implement push notification backend registration
15. Fix gym-mobile offline sync trigger
16. Add Sentry crash reporting to both mobile apps
17. Configure EAS signing + store metadata
18. App store submissions

---

*Companion to [PRODUCTION-READINESS.md](./PRODUCTION-READINESS.md) — refer to that doc for account migration, DNS setup, and secrets rotation checklists.*
