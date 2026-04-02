# StudioLoop — Production Readiness Plan

**Created:** 2026-03-16
**Last Updated:** 2026-03-17
**Domain:** studioloop.co.za
**Status:** Pre-production (all 15 feature epics done, Epic 16 deployment is backlog)

### Remediation Progress (2026-03-17)

The following items from this audit have been **completed**:

| ID | Item | What Was Done |
|----|------|---------------|
| C1 | Unauthenticated user creation | Already had runtime guard (`ENVIRONMENT != "local"`) + router exclusion |
| C2 | Apple ID token signature verification | Added `app/core/apple_token.py` — JWKS verification via Apple's public keys (RS256). Updated both `staff_auth.py` and `consumers.py`. |
| C3 | Prospect CSV in git | Removed from tracking + added to `.gitignore`. Full history scrub pending. |
| C7 | Webhook signature test endpoint | Already had environment guard (`ENVIRONMENT != "local"`) |
| H1 | No rate limiting | Added `slowapi` — login: 10/min, password reset: 5/min, payment: 20/min, webhooks: 60/min |
| H3 | Missing security headers | Already had `SecurityHeadersMiddleware` (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, HSTS) |
| H4 | API docs in production | Already disabled (`docs_url=None`, `redoc_url=None`, `openapi_url=None` when production) |
| H5 | Demo passwords in git | Removed from tracking + added to `.gitignore`. Full history scrub pending. |
| H8 | Payment retry worker exposed | Already had environment guard |
| H9 | Stub payment providers on default path | Already enforced: `PAYMENT_PROVIDER` must be `stitch` in production (config validator) |
| M1 | CORS over-permissive | Already restricted to specific methods and headers |
| M2 | Payment URLs accept `str` | Already using `HttpUrl` type |
| M3 | Stitch webhook fallback to SECRET_KEY | Already required in non-local envs. Also fixed logic bug in fallback expression. |
| M4 | Admin auth manual function | Converted to `CurrentSuperUser` dependency injection (13 endpoints) |
| M5 | SECRET_KEY auto-generates | Already required in non-local envs (config validator) |
| M9 | Email logging sensitive data | Reduced SMTP response logging from `info` to `debug` |
| M11 | Mobile notification prefs UI-only | Wired 3 toggles to backend `GET/PATCH /notifications/me/preferences` API |
| M13 | Mobile support/legal URL defaults | Confirmed defaults are correct (`https://studioloop.co.za`) |
| M21 | Health check liveness-only | `/health` now verifies DB connectivity (`SELECT 1`), returns 503 if unreachable. Use `/health` for liveness, `/ready` (future) for readiness. |
| M22 | Container not hardened | Added non-root `appuser` and `HEALTHCHECK` to Dockerfile |
| H1 | Rate limiting | Proxy-aware: uses `X-Forwarded-For` header for client IP detection behind reverse proxies |
| M11 | Mobile notification prefs | Added `prefsFetched` guard to prevent saving default values before backend data loads |
| H6 | Vercel IDs in secrets | Replaced hardcoded Vercel project IDs in deploy.yml with `${{ secrets.VERCEL_*_PROJECT_ID }}` |
| M10 | Password policy | Added `validate_password_strength()`: min 8 chars, 1 uppercase, 1 lowercase, 1 digit. Applied to all create/reset schemas. |
| L2 | Plaintext password in email | `generate_new_account_email()` now sends a password-reset link instead of plaintext password |
| M14 | E2E workflow | Fixed Playwright `--project` names to match `playwright.config.ts` (web-chromium, consumer-web-chromium, gym-web-chromium) |
| M24 | POPIA deletion worker | Added `scripts/cleanup_deleted_accounts.py` — purges consumer data past 30-day grace period with `--dry-run` support |
| H11 | Admin dashboard | Built real admin UI: platform health dashboard, gym management (approve/reject/suspend), complaints, audit logs |
| M15 | Member detail mock | Wired gym-web MemberDetail page to real `staffMembershipsGetMemberDetail` API |
| M16 | Reports mock | Wired gym-web Reports page to 5 analytics endpoints (revenue, attendance, membership, class, staff) |
| M17 | Settings mock | Wired gym-web Settings page to real gym profile/hours/policies/plans/spaces/marketplace APIs |

**Remaining P0 blockers:** ~~C4-C6 (payment state machine)~~, H10 (legal pages), plus all account/infrastructure setup.

---

## Table of Contents

1. [Account & Email Migration](#1-account--email-migration)
2. [Security Audit Findings](#2-security-audit-findings)
3. [Infrastructure Setup](#3-infrastructure-setup)
4. [Code Cleanup](#4-code-cleanup)
5. [Development Work Remaining](#5-development-work-remaining)
6. [Pre-Launch Checklist](#6-pre-launch-checklist)

---

## 1. Account & Email Migration

You're currently using personal accounts for all services. Create official `@studioloop.co.za` email addresses and migrate every service.

### 1.1 Email Addresses to Create

Set up a business email provider (Google Workspace, Zoho Mail, or Fastmail) on the `studioloop.co.za` domain first.

| Email | Purpose |
|-------|---------|
| `admin@studioloop.co.za` | Platform superuser, admin dashboard login |
| `dev@studioloop.co.za` | Developer/CI service accounts (GitHub, Vercel, Railway) |
| `noreply@studioloop.co.za` | Transactional email sender (SMTP FROM address) |
| `support@studioloop.co.za` | Customer support, POPIA data requests |
| `billing@studioloop.co.za` | Stitch payment account, financial notifications |
| `security@studioloop.co.za` | Sentry alerts, security notifications |
| `apps@studioloop.co.za` | Apple Developer & Google Play Console accounts |

### 1.2 Service Accounts to Migrate

Each service below needs to be re-registered or transferred to official accounts.

| # | Service | Current State | Action Required | Account Email |
|---|---------|--------------|-----------------|---------------|
| 1 | **Google Workspace / Email** | No business email | Set up email hosting on `studioloop.co.za` | — |
| 2 | **GitHub** | Personal account (`ameen-solomons-projects`) | Create org or transfer repo to business account | `dev@studioloop.co.za` |
| 3 | **Vercel** | Personal team (`team_N2U5Xc9b9cQAwqh3Y823TPY8`) | Create new Vercel team or transfer projects | `dev@studioloop.co.za` |
| 4 | **Railway** | Personal account | Create org/team, transfer project | `dev@studioloop.co.za` |
| 5 | **Google OAuth** (Cloud Console) | Personal GCP project | New GCP project under business account, new OAuth client ID/secret | `dev@studioloop.co.za` |
| 6 | **Apple Developer** | Not set up / personal | Enroll as organization ($99/yr), create App ID, Sign-In keys | `apps@studioloop.co.za` |
| 7 | **Google Play Console** | Not set up / personal | Register as organization ($25 one-time), create app listing | `apps@studioloop.co.za` |
| 8 | **Stitch Payments** | Client ID/Secret exist | Register business account, get production credentials | `billing@studioloop.co.za` |
| 9 | **Sentry** | DSN placeholder only | Create organization, set up FastAPI project | `security@studioloop.co.za` |
| 10 | **SMTP Provider** | Placeholder config | Choose provider (Resend, Postmark, or SES), configure SPF/DKIM/DMARC on domain | `noreply@studioloop.co.za` |
| 11 | **Expo / EAS** | Personal account | Create org account, transfer project ownership | `dev@studioloop.co.za` |
| 12 | **Domain Registrar** | Domain acquired | Ensure auto-renew is on, WHOIS privacy enabled | `admin@studioloop.co.za` |
| 13 | **Fly.io** (if migrating) | Not set up | Create org for JNB region deployment | `dev@studioloop.co.za` |

### 1.3 DNS Records Needed

Once email + hosting are set up, configure these DNS records on `studioloop.co.za`:

| Record | Type | Value | Purpose |
|--------|------|-------|---------|
| `@` / `www` | A/CNAME | Vercel or marketing site | Main website |
| `app` | CNAME | `cname.vercel-dns.com` | Consumer web app |
| `manage` | CNAME | `cname.vercel-dns.com` | Gym staff web app |
| `dashboard` | CNAME | `cname.vercel-dns.com` | Admin dashboard |
| `api` | A/CNAME | Railway/Fly.io | Backend API |
| MX records | MX | Email provider | Business email |
| `_dmarc` | TXT | DMARC policy | Email auth |
| SPF | TXT | `v=spf1 include:...` | Email auth |
| DKIM | CNAME/TXT | Provider-specific | Email auth |

### 1.4 Secrets to Rotate After Migration

After creating official accounts, generate new credentials and update everywhere:

| Secret | Where It's Used | Update Locations |
|--------|----------------|-----------------|
| `SECRET_KEY` | JWT signing | `.env`, Railway env vars |
| `FIRST_SUPERUSER_PASSWORD` | Admin login | `.env`, Railway env vars |
| `GOOGLE_CLIENT_ID` / `SECRET` | OAuth | `.env`, Railway, GCP Console |
| `APPLE_CLIENT_ID` / `TEAM_ID` / `KEY_ID` / `PRIVATE_KEY` | OAuth | `.env`, Railway, Apple Developer |
| `STITCH_CLIENT_ID` / `SECRET` / `WEBHOOK_SECRET` | Payments | `.env`, Railway, Stitch dashboard |
| `SMTP_USER` / `SMTP_PASSWORD` | Email sending | `.env`, Railway |
| `SENTRY_DSN` | Error tracking | `.env`, Railway |
| `VERCEL_TOKEN` | CI deploy | GitHub repo secrets |
| `RAILWAY_TOKEN` | CI deploy | GitHub repo secrets |
| `TURBO_TOKEN` / `TURBO_TEAM` | Build cache | GitHub repo secrets |
| Vercel project IDs | CI deploy | `.github/workflows/deploy.yml` (hardcoded — move to secrets) |

---

## 2. Security Audit Findings

### CRITICAL

| # | Issue | Location | Risk | Fix |
|---|-------|----------|------|-----|
| C1 | ~~**Unauthenticated user creation endpoint**~~ | `backend/app/api/routes/private.py:23-38` | Anyone can create admin accounts if route is exposed | ✅ Has runtime guard (`ENVIRONMENT != "local"`) + router exclusion in `api/main.py:51-52` |
| C2 | ~~**Apple ID token decoded without signature verification**~~ | `backend/app/api/routes/staff_auth.py`, `consumers.py` | Token forgery — attacker can craft a fake Apple ID token | ✅ Fixed 2026-03-17: Added `app/core/apple_token.py` with JWKS verification (RS256, audience, issuer checks). Both routes updated. |
| C3 | **Prospect contact data committed to git** | `docs/cape-town-prospects.csv` | Real names, emails, phone numbers of gym owners in public repo | Remove from git history (`git filter-repo`), add to `.gitignore`. Store in private CRM instead. |
| C4 | ~~**Paid memberships activate before any verified payment succeeds**~~ | `backend/app/api/routes/staff_memberships.py` | Consumers can obtain gym membership access without paying | ✅ Fixed 2026-03-17: Memberships now created in `PENDING_PAYMENT` state. Payment initiated via provider. Webhook activates on completion, cancels on failure. |
| C5 | ~~**Marketplace subscriptions activate before any verified payment succeeds**~~ | `backend/app/api/routes/marketplace.py` | Consumers can obtain marketplace credits for free | ✅ Fixed 2026-03-17: Subscriptions now created in `PENDING_PAYMENT` state with platform-level Payment record (nullable gym_id). Webhook activates on completion. Plan pricing: R799/8, R999/12, R1499/unlimited. |
| C6 | ~~**Pay-per-class bookings are finalized before payment confirmation**~~ | `backend/app/api/routes/bookings.py` | Revenue leakage and booking/payment state drift | ✅ Fixed 2026-03-17: Bookings now created in `PENDING_PAYMENT` state with spot held. Webhook confirms booking on completion, cancels and releases spot on failure. |
| C7 | ~~**Public payment webhook signature helper exposes signing capability**~~ | `backend/app/api/routes/payments.py:765-769` | Makes forged payment webhook events feasible | ✅ Already has environment guard (`ENVIRONMENT != "local"`) |

### HIGH

| # | Issue | Location | Risk | Fix |
|---|-------|----------|------|-----|
| H1 | ~~**No rate limiting** on any endpoint~~ | Entire backend | Brute-force login, spam registrations, webhook abuse | ✅ Fixed 2026-03-17: Added `slowapi`. Login: 10/min, password reset: 5/min, payment: 20/min, webhooks: 60/min. |
| H2 | **Frontend tokens in localStorage** | `apps/web/src/lib/configureApiClient.ts`, `apps/gym-web/src/hooks/useAuth.ts`, `apps/consumer-web/src/lib/apiAuth.ts` | XSS can steal tokens (access + refresh) | Migrate to httpOnly cookie auth for web apps. Mobile apps using MMKV are fine. |
| H3 | ~~**Missing security headers**~~ | Backend `main.py` | Clickjacking, MIME sniffing, no HSTS | ✅ Already has `SecurityHeadersMiddleware` (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, HSTS in production) |
| H4 | ~~**API docs exposed in production**~~ | `backend/app/main.py` | Full endpoint/schema enumeration | ✅ Already disabled: `docs_url=None`, `redoc_url=None`, `openapi_url=None` when production |
| H5 | **Demo walkthrough with real passwords tracked in git** | `docs/demo-walkthrough.md` | Seed passwords (`staffpass123`, `password123`) visible in repo | ⚠️ Removed from tracking + .gitignore 2026-03-17. Full history scrub still needed. |
| H6 | **Vercel project IDs hardcoded in deploy workflow** | `.github/workflows/deploy.yml:30-35` | Minor exposure risk, makes rotation harder | Move to GitHub secrets (`VERCEL_PROJECT_ID_GYM`, etc.) |
| H7 | **Payment initiation trusts client-supplied amounts and related entity IDs** | `backend/app/api/routes/payments.py:222-296` | Price tampering and binding payments to arbitrary records | Derive prices and allowable target entity IDs server-side from plans/classes/subscriptions |
| H8 | ~~**Payment retry worker can be triggered directly**~~ | `backend/app/api/routes/payments.py:612-641` | Anyone could trigger global retry processing and mutate payment state | ✅ Already has environment guard (`ENVIRONMENT != "local"`) |
| H9 | ~~**Stub payment providers still exist on the default production path**~~ | `backend/app/core/config.py` | Production checkout can accidentally use non-production providers | ✅ Already enforced: `PAYMENT_PROVIDER` must be `stitch` in production (config validator) |
| H10 | **Legal pages are still placeholders** | `frontend/apps/web/src/routes/Terms.tsx`, `frontend/apps/web/src/routes/Privacy.tsx` | Public launch and app store compliance blocker | Replace with reviewed final legal content before launch |
| H11 | **Admin web app is not actually an admin dashboard yet** | `frontend/apps/web/src/routes/Home.tsx:1-29` | Platform admin workflows have backend support but no production UI | Build Epic 11 admin UI or keep this surface private until complete |

### MEDIUM

| # | Issue | Location | Risk | Fix |
|---|-------|----------|------|-----|
| M1 | ~~**CORS allows all methods/headers**~~ | `backend/app/main.py:28-33` | Slightly over-permissive | ✅ Already restricted to specific methods and headers |
| M2 | ~~**Payment URLs accept `str` not `HttpUrl`**~~ | `backend/app/api/routes/payments.py:34-36` | `javascript:` or malicious URLs could be stored | ✅ Already using `HttpUrl` |
| M3 | ~~**Stitch webhook falls back to SECRET_KEY**~~ | `backend/app/services/payments/stitch.py:302` | Wrong signing key if env var missing | ✅ Required in non-local envs. Fallback logic bug also fixed 2026-03-17. |
| M4 | ~~**Admin routes use manual `_require_superuser()` call**~~ | `backend/app/api/routes/admin.py` | Easy to forget, not enforced by framework | ✅ Fixed 2026-03-17: Converted to `CurrentSuperUser` dependency |
| M5 | ~~**SECRET_KEY auto-generates random value if not set**~~ | `backend/app/core/config.py:37` | All tokens invalidated on restart, breaks multi-instance | ✅ Already required in non-local envs |
| M6 | **No Content-Security-Policy** | Web apps (Vercel) | XSS mitigation gap | Configure CSP headers in `vercel.json` for each app |
| M7 | **No certificate pinning in mobile apps** | Both mobile apps | MITM on compromised devices | Consider adding cert pinning for production API domain |
| M8 | **GitHub Actions not hash-pinned** | `.github/workflows/*.yml` | Supply chain risk (tag substitution) | Pin actions to commit SHAs (e.g., `actions/checkout@abcdef123`) |
| M9 | ~~**Email logging may expose sensitive data**~~ | `backend/app/utils.py:56` | SMTP response logged at INFO level | ✅ Fixed 2026-03-17: Reduced to DEBUG |
| M10 | **Password policy is minimal** (8 chars, no complexity) | `models/consumer.py:182`, `models/staff.py:97` | Weak passwords allowed | Consider adding complexity rules or use zxcvbn-style strength check |
| M11 | ~~**Consumer mobile notification preferences are UI-only**~~ | `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx` | Users think preferences changed when nothing persisted | ✅ Fixed 2026-03-17: Wired 3 toggles to `GET/PATCH /notifications/me/preferences` |
| M12 | **Push and WhatsApp notifications are still stubbed** | `backend/app/services/notifications/service.py:124-160` | Product promises exceed actual delivery capability | Implement real providers or narrow release promises/product copy |
| M13 | ~~**Mobile support/legal defaults were inconsistent with launch domain**~~ | `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx` | Broken trust and support links in production builds if env vars are missing | ✅ Verified 2026-03-17: Defaults already use `studioloop.co.za` |
| M14 | **E2E workflow does not match configured Playwright projects** | `.github/workflows/e2e.yml`, `frontend/playwright.config.ts` | CI can provide misleading release-safety signals | Align workflow project names or remove placeholder E2E claims from readiness |
| M15 | **Gym web member detail page is still hardcoded mock data** | `frontend/apps/gym-web/src/routes/members/MemberDetail.tsx:13-41` | Staff could see fake member/payment/attendance data in production | Replace with real API-backed member detail queries |
| M16 | **Gym web reports page is entirely hardcoded** | `frontend/apps/gym-web/src/routes/reports/Reports.tsx:20-226` | Operators may make business decisions from fake metrics | Wire to reporting/analytics API before launch |
| M17 | **Gym web settings page is non-functional and non-persisted** | `frontend/apps/gym-web/src/routes/settings/Settings.tsx:22-257` | Operators can believe settings changed when nothing was saved | Connect all tabs to actual settings APIs or hide incomplete sections |
| M18 | **Critical backend route modules have little or no dedicated route-level test coverage** | `backend/tests/` vs `backend/app/api/routes/*.py` | Payment/admin/realtime regressions can ship without meaningful CI protection | Add focused tests for `admin.py`, `analytics.py`, `bookings.py`, `marketplace.py`, `payments.py`, `realtime.py`, `staff_memberships.py`, and `webhooks.py` |
| M19 | **Marketing sites are outside the deploy pipeline and have non-functional forms** | `.github/workflows/deploy.yml:27-35`, `frontend/apps/marketing-consumers/src/pages/index.astro:69-75,166-169`, `frontend/apps/marketing-gyms/src/pages/index.astro:242-249` | Public acquisition flows can silently fail or drift from production deploys | Add both Astro apps to CI/CD and wire forms to real handlers |
| M20 | **Mobile production build config is still minimal** | `frontend/apps/consumer-mobile/eas.json`, `frontend/apps/gym-mobile/eas.json`, both `app.json` files | Store submission and signing readiness are overstated | Finalize production signing, distribution, metadata, and privacy-policy configuration for both apps |
| M21 | ~~**Health checks are liveness-only and do not verify DB or critical dependencies**~~ | `backend/app/main.py:70-73` | Platform can report healthy while database is broken | ✅ Fixed 2026-03-17: `/health` now runs `SELECT 1` and returns 503 if DB unreachable |
| M22 | ~~**Container runtime is not hardened for production**~~ | `backend/Dockerfile` | Runs as root and has no Docker-level `HEALTHCHECK` | ✅ Fixed 2026-03-17: Added non-root `appuser` and `HEALTHCHECK` |
| M23 | **Frontend/mobile crash reporting is not actually wired despite Sentry plans** | `backend/app/main.py:35-36`, no corresponding frontend/mobile Sentry initialization found | Client-side crashes can go unseen in production | Add Sentry or equivalent crash reporting to web and mobile apps before launch |
| M24 | **POPIA account deletion promises scheduled cleanup, but no cleanup worker exists** | `backend/app/api/routes/consumers.py:603-607,633-643` | Data may remain beyond the promised 30-day deletion window | Implement and operate a real cleanup job, and document its runbook |
| M25 | **No backup/restore or incident-response runbook is present in repo docs** | `docs/`, `backend/README.md` | Operational recovery depends on tribal knowledge during an outage | Add documented restore, rollback, migration-failure, and incident-response procedures |
| M26 | **Deployment target configuration is split across Railway and Vercel serverless paths** | `backend/railway.toml`, `vercel.json`, `api/index.py` | Team can drift between unsupported deployment models | Decide and document the single supported production deployment path for the backend |

### LOW

| # | Issue | Location | Notes |
|---|-------|----------|-------|
| L1 | Seed data uses weak default password `staffpass123` | `backend/app/seed/staff.py` | Fine for local dev, never use in staging/prod |
| L2 | `generate_new_account_email()` accepts plaintext password | `backend/app/utils.py:86-100` | Not called in auth routes currently, but risky pattern |
| L3 | OAuth redirect URIs hardcoded to localhost defaults | `backend/app/core/config.py:122-133` | Overridden by env vars, just ensure they're set |
| L4 | Legacy models not yet migrated | `backend/app/models/__init__.py:115` | Tech debt, not security |

---

## 3. Infrastructure Setup

### 3.1 Production Hosting Decision

**Current state:** Backend on Railway, frontend on Vercel.
**Planned state (per Epic 16):** Backend on Fly.io (JNB region for POPIA data residency).

**Decision needed:** Stick with Railway or migrate to Fly.io?

| Factor | Railway | Fly.io |
|--------|---------|--------|
| JNB region | No (closest: EU) | Yes (`jnb` region) |
| POPIA compliance | Risk — data leaves SA | Compliant — data stays in SA |
| Managed Postgres | Yes (or use Neon) | Yes (Fly Postgres) |
| Pricing | Usage-based | Usage-based |
| Docker deploy | Native | Native |
| Complexity | Lower | Slightly higher |

**Recommendation:** Migrate to Fly.io for production if POPIA data residency is a hard requirement. Keep Railway for staging.

### 3.2 Database

- [ ] Provision production Postgres (Fly.io Postgres or Supabase/Neon with JNB-proximal region)
- [ ] Enable SSL connections (`?sslmode=require`)
- [ ] Set up automated backups (daily, 30-day retention)
- [ ] Run `alembic upgrade head` on production DB
- [ ] Create production superuser with strong password
- [ ] Do NOT run seed scripts on production

### 3.3 Redis

Redis is in docker-compose but not used by application code yet. Decide:
- [ ] If needed for production (session store, caching, rate limiting, background jobs) → provision managed Redis
- [ ] If not needed yet → remove from production requirements, add later

### 3.4 CDN & Static Assets

- [ ] Vercel handles CDN for web apps automatically
- [ ] Configure custom domains on Vercel projects (see DNS section above)
- [ ] Set up proper cache headers for static assets

---

## 4. Code Cleanup

### 4.1 Remove Sensitive Files from Git

| File | Issue | Action |
|------|-------|--------|
| `docs/cape-town-prospects.csv` | Real contact data (70+ gym owners with emails/phones) | Remove from repo, add to `.gitignore`, store in CRM |
| `docs/demo-walkthrough.md` | Contains all seed passwords in plaintext | Remove passwords from doc, or untrack file |

### 4.2 Harden Private/Dev Routes

| Task | File | Details |
|------|------|---------|
| Guard private routes at endpoint level | `backend/app/api/routes/private.py` | Add `@app.on_event` or middleware check, not just router exclusion |
| Disable API docs in production | `backend/app/main.py` | Set `docs_url=None, redoc_url=None, openapi_url=None` for production |

### 4.3 Move Hardcoded Values to Config

| Value | Current Location | Move To |
|-------|-----------------|---------|
| Vercel project IDs | `.github/workflows/deploy.yml:30-35` | GitHub repo secrets |
| Vercel org ID | `.github/workflows/deploy.yml:17,78,84` | GitHub repo secrets |
| Localhost CORS origins | `backend/app/core/config.py:49-55` | Keep for local dev but ensure production only uses env var origins |

### 4.4 Frontend Token Storage Migration

Migrate web app auth from localStorage to httpOnly cookies:

| App | Current Auth File | Change |
|-----|-------------------|--------|
| `apps/web` | `src/lib/configureApiClient.ts` | Backend sets httpOnly cookie, frontend reads user state from `/me` endpoint |
| `apps/gym-web` | `src/hooks/useAuth.ts` | Same pattern |
| `apps/consumer-web` | `src/lib/apiAuth.ts` | Same pattern |

This is a significant change that requires backend cookie-setting endpoints and frontend refactoring. Consider scope vs. risk trade-off — an alternative is strict CSP + Subresource Integrity to mitigate XSS.

### 4.5 Stub Services That Need Real Implementation

| Service | Current State | What's Needed |
|---------|---------------|---------------|
| Push notifications (FCM/APNs) | Logs only | Integrate Firebase Cloud Messaging, configure with Expo |
| WhatsApp notifications | Logs only | Integrate WhatsApp Business API provider (e.g., Twilio, MessageBird) |
| Email templates | Basic HTML | Review/polish transactional email templates |
| Ozow / PayFast | Stub implementations | Either implement or remove from codebase |

### 4.6 Frontend Surfaces Still Using Mock or Placeholder Functionality

| Surface | Current State | What's Needed |
|---------|---------------|---------------|
| Admin web home/dashboard | Auth shell only (`"You are signed in"`) | Build real platform admin UI or keep app non-public until it exists |
| Admin web legal pages | Placeholder copy only | Replace with reviewed final legal content |
| Gym web member detail | Hardcoded member, attendance, and payment data | Replace with real member detail, payment history, and attendance queries |
| Gym web reports | All revenue, attendance, membership, and staff metrics are hardcoded | Connect to analytics/reporting endpoints with loading and error states |
| Gym web settings | Forms and toggles use `defaultValue` only; save buttons do not persist | Wire profile/hours/policies/plans/spaces/marketplace/webhook settings to APIs |

### 4.7 Marketing and Acquisition Surfaces

| Surface | Current State | What's Needed |
|---------|---------------|---------------|
| Consumer marketing site | Static landing page with search/waitlist forms using `type="button"` and no handlers | Connect forms to backend/email capture and add legal pages |
| Gym marketing site | Demo request form is present but non-functional | Wire to CRM/email capture and add legal pages |
| Marketing site deployment | Not included in deploy workflow matrix | Add both Astro sites to CI/CD so public marketing content is versioned and deployed consistently |

### 4.8 Operational Readiness Gaps

| Area | Current State | What's Needed |
|------|---------------|---------------|
| Health checks | ~~`/health` returns success without checking DB~~ | ✅ Fixed 2026-03-17: `/health` now verifies DB connectivity and returns 503 if unreachable |
| Container hardening | ~~Backend image runs as root~~ | ✅ Fixed 2026-03-17: Added non-root `appuser` and `HEALTHCHECK` instruction |
| Crash reporting | Backend initializes Sentry, but web/mobile apps do not | Add client-side crash/error reporting and alert routing |
| POPIA deletion operations | API sets `deletion_requested_at` but no cleanup worker/runbook is present | Implement scheduled deletion processing and document operations |
| Recovery runbooks | No repo-level backup/restore/rollback/incident procedures found | Add operational runbooks for database restore, rollback, and incident handling |
| Deployment path | Backend has both Railway and Vercel entrypoint configs in repo | Document the canonical production path and retire unsupported alternatives |

### 4.9 Documentation Drift and Stale Internal Claims

| Document | Stale / Misleading Claim | Why It Needs Updating |
|----------|--------------------------|------------------------|
| `docs/PROJECT_OVERVIEW.md` | Describes the platform as "production-ready", "85-90% ready", and links to public `/docs` | Current readiness audit identifies multiple P0 launch blockers and production docs should not remain publicly exposed |
| `docs/ARCHITECTURE.md` | Treats Railway JNB, Sentry, and production payment/monitoring posture as fully active/stable | Current repo shows hosting direction still in flux, backend-only Sentry wiring, and payment integrity gaps |
| `docs/FEATURES.md` | Lists WhatsApp alerts, consumer notification preferences, CI/CD, and deployment posture as implemented/current | Current codebase still has stubbed delivery, UI-only notification preferences, incomplete deploy scope, and placeholder E2E |
| `docs/AI_CONTEXT.md` and `docs/KNOWLEDGE_BASE_ENTRY.md` | Present the project as near-launch and production-deployed without the launch blockers now documented | These files can mislead future contributors or AI tooling about current readiness |
| `docs/demo-walkthrough.md` | Uses production URLs, public API docs, and demo language that overstates reports/member-detail/offline flows | Several demo surfaces are incomplete or placeholder, and the public-docs assumption conflicts with hardening requirements |
| `docs/launch-pricing-ops-march-2026.md` | Treats current backend/health URLs and stable production ops as established | Production topology and runtime posture are still being finalized |
| `docs/DECISIONS.md` | Treats Railway JNB and other deployment choices as settled decisions | Current readiness work still shows unresolved production hosting direction |

---

## 5. Development Work Remaining

### 5.0 Additional Launch Blockers From Full Audit

These items were confirmed during the repository-wide audit and should be treated as go-live blockers, not backlog cleanup:

| Priority | Task | Why It Blocks Launch |
|----------|------|----------------------|
| P0 | Rework membership, marketplace subscription, and pay-per-class flows so access is granted only after verified payment completion | Current monetization flow can grant paid access without a successful charge |
| P0 | Remove or lock down `/payments/webhook-signature-test` and `/payments/retries/run` in all non-local environments | Both endpoints materially weaken payment integrity |
| P0 | Server-side derive all billable amounts and validate related entity ownership on payment initiation | Client-controlled amounts are not production-safe |
| P0 | Replace placeholder legal/privacy content | Public launch and app store submission require final legal pages |
| P0 | Decide whether admin web and incomplete gym web pages can be public at launch | Several surfaces still present fake or non-persisted functionality |
| P1 | Add real route-level coverage for payment, booking, admin, and realtime backend modules | Current CI passes do not imply strong coverage over the highest-risk flows |
| P1 | Bring both marketing sites into CI/CD and replace inert forms with real lead capture | Public acquisition surfaces should not rely on manual deploys or dead buttons |
| P1 | Add real readiness probes, recovery runbooks, and deletion operations | Current ops posture is under-documented and partly aspirational |
| P1 | Decide and document the single supported production deployment path for the backend | Repo currently preserves multiple hosting directions |
| P1 | Reconcile stale overview/architecture/demo docs with the audited readiness picture | Internal docs currently overstate production posture |
| P1 | Make E2E CI truthful by aligning Playwright project names and running real release flows | Current workflow should not be treated as a dependable release gate |

### 5.1 Epic 16 Stories (Production Deployment)

All 7 stories are in `backlog` status:

| Story | Description | Key Tasks |
|-------|-------------|-----------|
| **16-1** | Deploy database infrastructure | Provision prod Postgres (Fly.io or managed), backups, SSL, connection pooling |
| **16-2** | Configure CI/CD pipelines | Update deploy workflow for production, add staging environment, branch protection |
| **16-3** | Setup monitoring & error tracking | Configure Sentry (backend + frontend), uptime monitoring, alerting |
| **16-4** | Configure production domains & SSL | DNS records, custom domains on Vercel/Fly, SSL certificates, email DNS (SPF/DKIM/DMARC) |
| **16-5** | Deploy backend to Fly.io | Dockerfile, `fly.toml`, health checks, env vars, scaling config |
| **16-6** | Deploy web apps to Vercel | Custom domains, env vars, build config, CSP headers |
| **16-7** | Configure EAS Build for mobile | Production build profiles, app store metadata, signing keys |

### 5.2 Security Fixes (Pre-Launch Blockers)

| Priority | Task | Effort | Status |
|----------|------|--------|--------|
| P0 | Fix Apple ID token verification (C2) | Small — add key verification | ✅ Done 2026-03-17 |
| P0 | Ensure private routes cannot be exposed in production (C1) | Small — add runtime guard | ✅ Already done |
| P0 | Remove prospect CSV from git history (C3) | Small — `git filter-repo` | ⚠️ Removed from tracking, history scrub pending |
| P0 | ~~Rework monetization state machine so memberships, subscriptions, and pay-per-class bookings only become active after verified payment completion (C4-C6, H7)~~ | Large — backend payment flow redesign | ✅ Done 2026-03-17 |
| P0 | Remove or hard-restrict payment helper endpoints (`/payments/webhook-signature-test`, `/payments/retries/run`) (C7, H8) | Small | ✅ Already done |
| P0 | Require real production payment provider path and remove accidental stub usage (H9) | Small | ✅ Already done |
| P0 | Replace placeholder legal/privacy pages and hide incomplete public surfaces (H10-H11, M15-M17) | Medium | ❌ Not started |
| P1 | Add rate limiting middleware (H1) | Medium — `slowapi` integration | ✅ Done 2026-03-17 |
| P1 | Add security headers middleware (H3) | Small — one middleware addition | ✅ Already done |
| P1 | Disable API docs in production (H4) | Small — conditional config | ✅ Already done |
| P1 | Require SECRET_KEY in production (M5) | Small — add validator | ✅ Already done |
| P1 | Require STITCH_WEBHOOK_SECRET in production (M3) | Small — add validator | ✅ Already done |
| P1 | Add route-level tests for payment, booking, admin, analytics, realtime, and webhook modules (M18) | Medium to Large | ❌ Not started |
| P1 | Add readiness checks, container hardening, and documented recovery procedures (M21, M22, M25, M26) | Medium | ⚠️ M21+M22 done 2026-03-17, M25+M26 not started |
| P1 | Add client-side crash reporting for web/mobile and operationalize deletion cleanup (M23, M24) | Medium | ❌ Not started |
| P1 | Update overview/architecture/demo docs so they no longer overstate readiness or expose production-only URLs/processes | Small to Medium | ❌ Not started |
| P2 | Migrate web auth to httpOnly cookies (H2) | Large — backend + frontend changes | ❌ Not started |
| P2 | Add CSP headers to Vercel config (M6) | Medium — policy definition | ❌ Not started |
| P2 | Convert admin auth to dependency injection (M4) | Small — refactor pattern | ✅ Done 2026-03-17 |
| P2 | Validate payment URLs as HttpUrl (M2) | Small — type change | ✅ Already done |

### 5.3 POPIA Compliance Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| Right to deletion | ✅ Done | Story 1-7 (account deletion) |
| Consent tracking | ✅ Done | Digital waivers (story 4-9) |
| Data residency (SA) | ⚠️ Blocked | Requires Fly.io JNB or SA-hosted DB |
| Privacy policy page | ❌ Not done | Need legal review + page on marketing site |
| Cookie consent banner | ❌ Not done | Required if using cookies for auth (especially after localStorage migration) |
| Data processing agreement | ❌ Not done | Needed for gym owners (data processors) |
| `support@studioloop.co.za` for data requests | ❌ Not done | Create email, document process |

### 5.4 App Store Readiness (Mobile)

| Task | Status | Details |
|------|--------|---------|
| Apple Developer enrollment | ❌ | Need business entity, $99/yr, D-U-N-S number |
| Google Play Console | ❌ | Need business entity, $25 one-time |
| App icons & splash screens | ⚠️ Check | Verify production-quality assets exist |
| App Store metadata (screenshots, description) | ❌ | Need for both consumer + gym apps |
| Privacy policy URL | ❌ | Required by both stores |
| EAS production build profiles | ⚠️ In progress | `eas.json` exists, needs final config |
| Push notification certificates | ❌ | APNs key (Apple), FCM setup (Google) |
| Deep link verification (`.well-known/`) | ❌ | Required for OAuth redirect + universal links |
| Persist notification preferences | ❌ | Current profile toggles are UI-only and do not affect backend behavior |
| Production signing/distribution config | ❌ | `eas.json` production profiles only set `autoIncrement`; store-signing setup is still incomplete |

### 5.5 Release Process and Test Coverage Gaps

| Area | Current State | Risk | Needed Before Launch |
|------|---------------|------|----------------------|
| Backend route coverage | `backend/tests/` has very limited route-module coverage relative to 18 backend route files | Critical flows can regress while CI stays green | Add focused tests for payments, bookings, memberships, admin, analytics, realtime, and webhooks |
| Frontend app coverage | Web/mobile tests are mostly auth/bootstrap tests with minimal workflow depth | UI regressions on booking, wallet, reports, and check-in flows can slip through | Add tests for primary user journeys and staff operational flows |
| Deploy pipeline scope | `deploy.yml` only deploys `gym-web`, `consumer-web`, and `web` | Marketing sites are outside release automation | Add `marketing-consumers` and `marketing-gyms` to deployment automation |
| E2E workflow fidelity | Workflow is marked placeholder and does not align with Playwright project names | Team can overestimate actual release confidence | Align workflow inputs and projects with `web-chromium`, `consumer-web-chromium`, and `gym-web-chromium` |

### 5.6 Operations and Recovery Gaps

| Area | Current State | Risk | Needed Before Launch |
|------|---------------|------|----------------------|
| Runtime health | Health endpoints return static success and do not verify DB readiness | Broken instances can pass platform health checks | Add readiness checks for DB and critical dependencies |
| Docker runtime | Backend container runs as root with no image-level health check | Weaker runtime posture and slower fault detection | Add non-root user and Docker `HEALTHCHECK` |
| Crash observability | Only backend Sentry initialization is present | Frontend/mobile failures may be invisible | Add Sentry or equivalent to web/mobile clients |
| POPIA deletion operations | 30-day deletion is promised but no cleanup job is documented or present | Compliance promise can be missed operationally | Add scheduled cleanup job and operator visibility |
| Recovery runbooks | No restore/rollback/incident docs found in repo | Slower recovery during outages or bad deploys | Add backup restore, rollback, and incident-response runbooks |
| Backend hosting direction | Railway and Vercel serverless configs both exist alongside Fly.io planning | Confusion over supported production topology | Choose and document one canonical production backend deployment path |
| Internal documentation drift | Several overview/architecture/demo docs still describe the repo as near-launch or production-ready | Team and tooling can make bad decisions from stale assumptions | Update high-level docs to point back to this readiness audit until blockers are cleared |

---

## 6. Pre-Launch Checklist

### Phase 1: Accounts & Infrastructure (Do First)
- [ ] Set up business email hosting on `studioloop.co.za`
- [ ] Create all `@studioloop.co.za` email addresses (see 1.1)
- [ ] Register/transfer all service accounts (see 1.2)
- [ ] Configure DNS records (see 1.3)
- [ ] Provision production database with backups
- [ ] Set up Sentry organization + projects
- [ ] Set up SMTP provider with SPF/DKIM/DMARC
- [ ] Register with Stitch for production payment credentials
- [ ] Enroll in Apple Developer Program (needs D-U-N-S)
- [ ] Register Google Play Developer account

### Phase 2: Security Fixes (Do Before Any Public Access)
- [x] Fix Apple ID token signature verification (C2) — ✅ 2026-03-17: Added `app/core/apple_token.py` with JWKS verification, updated both staff_auth.py and consumers.py
- [x] Add runtime guard on private/dev routes (C1) — ✅ Already had runtime guard + router exclusion
- [ ] Remove `cape-town-prospects.csv` from git history (C3) — ⚠️ Removed from tracking + .gitignore, full history scrub still needed (`git filter-repo`)
- [x] Rework monetization state machine so memberships, marketplace subscriptions, and pay-per-class bookings cannot become active/booked before verified payment completion (C4-C6, H7)
- [x] Remove or lock down `/payments/webhook-signature-test` and `/payments/retries/run` outside local/test environments (C7, H8) — ✅ Already had environment guards
- [x] Force production onto the real payment provider path and remove accidental stub-provider usage (H9) — ✅ Already enforced via config validator
- [x] Add rate limiting (`slowapi`) on auth + payment endpoints (H1) — ✅ 2026-03-17: Added slowapi with limits on login (10/min), password reset (5/min), payment (20/min), webhooks (60/min). Disabled in local env for tests.
- [x] Add security response headers middleware (H3) — ✅ Already had SecurityHeadersMiddleware
- [x] Disable API docs/redoc/openapi.json in production (H4) — ✅ Already disabled conditionally
- [ ] Remove demo passwords from tracked docs (H5) — ⚠️ Removed from tracking + .gitignore, full history scrub still needed
- [ ] Move Vercel project IDs to GitHub secrets (H6)
- [x] Add validator requiring SECRET_KEY in non-local envs (M5) — ✅ Already enforced via config validator
- [x] Add validator requiring STITCH_WEBHOOK_SECRET in non-local envs (M3) — ✅ Already enforced via config validator
- [x] Validate payment URLs with `HttpUrl` type (M2) — ✅ Already using HttpUrl
- [x] Restrict CORS methods/headers (M1) — ✅ Already restricted to specific methods/headers

### Phase 3: Production Deployment (Epic 16)
- [ ] Deploy backend to Fly.io JNB (or finalize Railway)
- [ ] Configure custom domains with SSL on Vercel (app, manage, dashboard)
- [ ] Configure custom domain for API (api.studioloop.co.za)
- [ ] Add both marketing Astro sites to automated deployment
- [ ] Decide and document the canonical production backend hosting target (Railway, Fly.io, or another single path)
- [ ] Update all OAuth redirect URIs to production domains
- [ ] Update CORS origins for production domains
- [ ] Update frontend `VITE_API_BASE_URL` env vars on Vercel
- [ ] Update mobile `EXPO_PUBLIC_API_BASE_URL`
- [ ] Run `alembic upgrade head` on production DB
- [ ] Create production superuser (strong password, official email)
- [ ] Set up uptime monitoring (e.g., Better Uptime, UptimeRobot)
- [ ] Configure Sentry alerts (email to `security@studioloop.co.za`)
- [x] Add a real readiness health check that validates DB connectivity — ✅ 2026-03-17: `/health` now runs `SELECT 1` and returns 503 if DB unreachable
- [ ] Verify webhook endpoints are reachable + signed correctly

### Phase 4: Polish & Legal
- [ ] Privacy policy page (legal review required)
- [ ] Terms of service page
- [ ] Replace placeholder legal content in admin web before exposing that surface publicly
- [ ] Replace inert marketing-site forms with real lead capture or remove them before launch
- [ ] Cookie consent (if using cookies)
- [ ] POPIA data processing agreements template for gym owners
- [ ] Configure `support@studioloop.co.za` email routing
- [ ] Document POPIA deletion operations, backup/restore, and incident-response runbooks
- [ ] Update overview/architecture/demo/launch docs so they stop overstating current production readiness
- [ ] Polish transactional email templates
- [ ] App Store metadata + screenshots
- [ ] Production EAS builds + store submissions

### Phase 5: Post-Launch Hardening
- [ ] Migrate web auth to httpOnly cookies (H2) — or implement strict CSP as alternative
- [ ] Add CSP headers on Vercel (`vercel.json`)
- [ ] Pin GitHub Actions to commit SHAs (M8)
- [ ] Add certificate pinning in mobile apps (M7)
- [ ] Implement push notifications (FCM/APNs)
- [ ] Implement WhatsApp Business API integration
- [x] Persist mobile notification preferences to backend settings — ✅ 2026-03-17: Wired 3 toggles in consumer-mobile profile to GET/PATCH `/notifications/me/preferences`
- [ ] Replace or remove incomplete admin/gym web pages that still use mock or non-persisted data
- [ ] Expand route-level backend coverage for payments, bookings, memberships, admin, analytics, realtime, and webhooks
- [ ] Expand frontend/mobile coverage beyond auth/bootstrap smoke tests
- [ ] Add web/mobile crash reporting and alert routing
- [x] Harden backend container runtime with non-root execution and Docker `HEALTHCHECK` — ✅ 2026-03-17: Added `appuser` non-root user and HEALTHCHECK to Dockerfile
- [ ] Implement automated POPIA deletion cleanup worker
- [ ] Make E2E CI match actual Playwright projects and release flows
- [ ] Decide on Ozow/PayFast: implement or remove stubs entirely
- [ ] Add Redis for rate limiting / caching / background jobs
- [ ] Load testing (k6 or similar)
- [ ] Penetration test (external)

---

## Appendix: Current Service Map

```
┌─────────────────────────────────────────────────────────┐
│                    studioloop.co.za                      │
├─────────────┬─────────────┬─────────────┬───────────────┤
│ app.*       │ manage.*    │ dashboard.* │ api.*         │
│ Consumer Web│ Gym Web     │ Admin Web   │ Backend API   │
│ (Vercel)    │ (Vercel)    │ (Vercel)    │ (Railway/Fly) │
├─────────────┴─────────────┴─────────────┴───────────────┤
│                     Backend API                          │
│  ┌──────┐ ┌────────┐ ┌───────┐ ┌──────┐ ┌────────────┐ │
│  │Sentry│ │  SMTP  │ │Stitch │ │Google│ │   Apple    │ │
│  │      │ │Provider│ │Payments│ │OAuth │ │  Sign-In   │ │
│  └──────┘ └────────┘ └───────┘ └──────┘ └────────────┘ │
├─────────────────────────────────────────────────────────┤
│               PostgreSQL (Fly.io JNB)                    │
├─────────────────────────────────────────────────────────┤
│          Mobile Apps (EAS Build → App Stores)            │
│  ┌───────────────────┐  ┌──────────────────────┐        │
│  │ Consumer (iOS/And)│  │ Gym Staff (iOS/And)  │        │
│  │ com.studioloop.   │  │ com.studioloop.gym   │        │
│  │    consumer       │  │                      │        │
│  └───────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

*This document should be treated as a living checklist. Update status as items are completed.*

---

## Appendix: Additional Audit Findings (2026-03-16)

This appendix captures issues found during a repository-wide production-readiness audit that are not fully covered above.

### Newly Identified P0 Launch Blockers

| # | Issue | Location | Risk | Fix |
|---|-------|----------|------|-----|
| P0-1 | ~~**Memberships become active before payment succeeds**~~ | `backend/app/api/routes/staff_memberships.py` | Users can gain paid membership access without a successful charge | ✅ Fixed: `PENDING_PAYMENT` state introduced; activate only from verified payment webhook |
| P0-2 | **Marketplace subscriptions become active before payment succeeds** | `backend/app/api/routes/marketplace.py:433-466` | Consumers can obtain marketplace credits for free | Create unpaid subscription intent first, then activate only after verified payment completion |
| P0-3 | **Pay-per-class booking trusts client amount and books immediately** | `backend/app/api/routes/bookings.py:216-247` | Users can underpay or get booked without paying | Derive class price server-side and require verified payment before final booking confirmation |
| P0-4 | **Payment initiation trusts client-supplied price and related entity IDs** | `backend/app/api/routes/payments.py:222-296` | Price tampering; a user can bind a payment to arbitrary membership/entity records | Derive all billable amounts and allowed target entity IDs on the server |
| P0-5 | **Public webhook signature oracle** | `backend/app/api/routes/payments.py:765-769` | Attackers can generate valid webhook signatures for forged payment events | Remove endpoint or restrict to local/test only |
| P0-6 | **Public retry worker trigger** | `backend/app/api/routes/payments.py:612-641` | Anyone can trigger global payment retry processing | Restrict to internal job runner or authenticated admin/local-only use |
| P0-7 | **Stub payment providers still sit on the default path** | `backend/app/core/config.py:151-165`, `backend/app/services/payments/providers.py:41-120` | Production can accidentally use fake providers | Require `PAYMENT_PROVIDER=stitch` in production or remove Ozow/PayFast until implemented |

### Newly Identified P1 Launch Gaps

| # | Issue | Location | Risk | Fix |
|---|-------|----------|------|-----|
| P1-1 | **Privacy policy page is still placeholder content** | `frontend/apps/web/src/routes/Privacy.tsx:1-15` | Legal/compliance blocker for public launch | Replace with final reviewed privacy policy |
| P1-2 | **Terms of service page is still placeholder content** | `frontend/apps/web/src/routes/Terms.tsx:1-14` | Legal/compliance blocker for public launch | Replace with final reviewed terms |
| P1-3 | **Mobile apps point to wrong production support/legal defaults** | `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx:20`, `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx:179-195` | Broken support and legal links in production builds | Switch defaults to `studioloop.co.za` and ensure env overrides are set |
| P1-4 | **E2E workflow is still effectively placeholder and mismatched to Playwright projects** | `.github/workflows/e2e.yml:33-35`, `frontend/playwright.config.ts:57-118` | False confidence in release test automation | Either make E2E CI real and aligned, or remove it from readiness claims |

### Additional High / Medium Findings From Full Audit

| # | Issue | Location | Risk | Fix |
|---|-------|----------|------|-----|
| A1 | ~~**Pay-per-class bookings only check that the submitted amount matches the session price; they still finalize a booking before any payment confirmation**~~ | `backend/app/api/routes/bookings.py` | Revenue leakage; charge and booking state can drift | ✅ Fixed: Booking created in `PENDING_PAYMENT` state with spot held; confirmed only after verified payment webhook |
| A2 | **Marketplace class booking consumes subscription credits immediately, with no payment trail for the subscription itself** | `backend/app/api/routes/marketplace.py:469-523` | Hard to reconcile revenue, refunds, and abuse cases | Record a paid subscription lifecycle and separate credit consumption from subscription purchase |
| A3 | **Notification promises exceed actual implementation** | `backend/app/services/notifications/service.py:124-160` | Users and gyms may expect push/WhatsApp delivery that does not happen | Scope product copy down or implement real delivery before launch |
| A4 | **Mobile notification preference toggles are UI-only and do not persist** | `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx:22-25`, `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx:160-165` | Users think they changed preferences, but backend behavior remains unchanged | Wire mobile settings to the notification preferences API or hide the controls until connected |
| A5 | **Production support/legal defaults in mobile were inconsistent with launch domain plan** | `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx:20`, `frontend/apps/consumer-mobile/app/(tabs)/profile.tsx:179-195` | Broken trust and support flow in production builds | Keep `.co.za` defaults and set explicit `EXPO_PUBLIC_LEGAL_BASE_URL` per environment |
| A6 | **E2E workflow browser names do not match Playwright project names** | `.github/workflows/e2e.yml:107-126`, `frontend/playwright.config.ts:57-118` | Manual CI runs can give misleading coverage or fail unexpectedly | Align workflow `--project` values with `web-chromium`, `consumer-web-chromium`, `gym-web-chromium` or simplify config |
| A7 | **`docs/PROJECT_OVERVIEW.md` and `docs/demo-walkthrough.md` still reference public docs and production URLs that assume insecure current state** | `docs/PROJECT_OVERVIEW.md`, `docs/demo-walkthrough.md` | Team may treat non-production-safe URLs/processes as launch-ready | Update docs after security fixes land so internal runbooks match actual production posture |

### Full Audit Notes

The full repository audit concluded:

1. The most serious remaining launch risk is not infrastructure, but monetization integrity.
   Memberships, subscriptions, and class bookings still do not cleanly enforce "paid before active/booked".
2. The existing readiness document correctly identified many security issues, but it understated how much of the payment system is still MVP-grade.
3. Legal and customer-facing production defaults were still incomplete in more than one surface.
4. Test automation exists, but the E2E workflow should not yet be treated as a trustworthy release gate.

### Operational Notes

- Notification delivery remains partial for go-live:
  - Push and WhatsApp are still stubbed and only logged in `backend/app/services/notifications/service.py:124-160`
- Mobile apps register for push tokens, but server-side push delivery is still not implemented end-to-end
- Several consumer/gym flows are production-looking in UI but still rely on MVP backend behavior that needs tightening before launch
- The existing document correctly captures:
  - Apple token verification gap
  - web token storage in `localStorage`
  - exposed API docs
  - missing security headers
  - hardcoded deploy metadata
  - sensitive tracked docs/data

### Recommended Immediate Remediation Order

1. Remove or lock down exposed payment helper endpoints (`webhook-signature-test`, retry worker)
2. Disable production docs/openapi exposure and add security headers
3. Require safe production payment configuration (`stitch`, explicit secrets)
4. Replace placeholder legal pages and fix mobile production support/legal URLs
5. ~~Rework payment state machine so memberships/subscriptions/bookings only activate after verified payment completion~~ ✅ Done
6. Make E2E CI truthful: either fully wire it up or stop presenting it as launch-ready automation
