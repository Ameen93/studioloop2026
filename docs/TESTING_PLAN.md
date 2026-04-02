---
project: studioloop2026
type: testing
status: plan
last_updated: 2026-03-18
---

# StudioLoop — Comprehensive Testing Plan

Automated end-to-end testing using Claude Code + Chrome DevTools against a running local stack.

---

## Architecture

```
Docker Compose (local stack)
  ├── backend (FastAPI on :8000)
  ├── PostgreSQL (:5432)
  └── Redis (:6379)

Frontend dev servers
  ├── consumer-web (:5173 or similar)
  ├── gym-web (:5174 or similar)
  └── marketing sites

Claude Code session
  └── Uses Playwright/Chrome DevTools to drive browsers
  └── Also hits API directly for setup/teardown/verification
```

## Approach

**Two-layer testing:**
1. **API-level:** Direct HTTP calls to backend for auth flows, data setup, payment hooks, admin ops
2. **Browser-level:** Chrome DevTools / Playwright for UI flows, visual verification, mobile-responsive checks

**Why both?** Some things are faster/more reliable at API level (user creation, payment webhook simulation). UI testing catches rendering bugs, broken forms, navigation issues, responsive layout problems.

---

## Pre-requisites

Before running tests:
1. `docker compose -f docker-compose.local.yml up -d` (backend + DB + Redis)
2. Frontend dev servers running (`pnpm dev` in relevant app dirs)
3. Seed data script (or API calls to create test gym + test consumer)
4. Clean DB state (reset between full runs)

### Test Data Setup (via API)
```
1. Create superuser/admin account
2. Create test gym ("TestFit Studio")
   - Add class schedule (Yoga Mon/Wed 9am, HIIT Tue/Thu 6pm)
   - Add membership plans (Basic R199/mo, Premium R399/mo)
   - Set gym profile, hours, policies
3. Create test consumer ("Test User", test@example.com)
4. Create test staff member for gym
```

---

## Test Suites

### Suite 1: Smoke Tests (5 min)
Quick sanity check — run this first, every time.

| # | Test | Surface | Method |
|---|------|---------|--------|
| 1.1 | Backend health check returns 200 | API | GET /health |
| 1.2 | Consumer-web loads, shows login | Browser | Navigate, check title |
| 1.3 | Gym-web loads, shows login | Browser | Navigate, check title |
| 1.4 | Marketing consumer site loads | Browser | Navigate, check hero |
| 1.5 | Marketing gym site loads | Browser | Navigate, check hero |
| 1.6 | API docs are disabled (404) | API | GET /docs, /redoc, /openapi.json |
| 1.7 | CORS headers present | API | OPTIONS request |
| 1.8 | Rate limiting responds (429 after burst) | API | Rapid login attempts |

### Suite 2: Auth Flows (10 min)
Test all auth paths for both consumer and gym staff.

| # | Test | Surface | Method |
|---|------|---------|--------|
| 2.1 | Consumer email registration | Browser | Fill form, submit, verify redirect |
| 2.2 | Consumer email login | Browser | Fill form, submit, verify dashboard |
| 2.3 | Consumer logout | Browser | Click logout, verify redirect to login |
| 2.4 | Consumer password reset flow | API+Browser | Request reset, verify email, reset |
| 2.5 | Password strength validation | Browser | Try weak passwords, verify rejection |
| 2.6 | Gym staff login | Browser | Fill form, submit, verify gym dashboard |
| 2.7 | Gym staff logout | Browser | Click logout, verify redirect |
| 2.8 | Token refresh works | API | Use refresh token after access expires |
| 2.9 | Invalid credentials rejected | Browser | Wrong password, verify error message |
| 2.10 | Rate limiting on login (10/min) | API | 11 rapid attempts, verify 429 |

### Suite 3: Consumer Journey (15 min)
The main consumer flow: discover → book → attend → review.

| # | Test | Surface | Method |
|---|------|---------|--------|
| 3.1 | Marketplace browse (list gyms/classes) | Browser | Navigate, verify listings |
| 3.2 | Search/filter classes by type | Browser | Use filters, verify results |
| 3.3 | View class details | Browser | Click class, verify info page |
| 3.4 | Book a class | Browser | Click book, verify confirmation |
| 3.5 | View upcoming bookings | Browser | Navigate to bookings, verify list |
| 3.6 | Cancel a booking | Browser | Click cancel, verify removal |
| 3.7 | View booking history | Browser | Navigate, verify past bookings |
| 3.8 | Consumer profile edit | Browser | Change name, verify save |
| 3.9 | Notification preferences | Browser | Toggle settings, verify persistence |
| 3.10 | Consumer stats/analytics | Browser | Check dashboard stats render |

### Suite 4: Gym Management Journey (15 min)
Gym owner/staff dashboard flows.

| # | Test | Surface | Method |
|---|------|---------|--------|
| 4.1 | Gym dashboard loads with stats | Browser | Verify KPI cards render |
| 4.2 | View member list | Browser | Navigate, verify member table |
| 4.3 | View member detail | Browser | Click member, verify detail page |
| 4.4 | Class schedule management | Browser | Add/edit/delete a class |
| 4.5 | Membership plan management | Browser | View/edit plans |
| 4.6 | Gym profile settings | Browser | Edit name/hours/policies, save |
| 4.7 | Reports page | Browser | Verify revenue/attendance/membership charts |
| 4.8 | Staff membership management | Browser | View/manage memberships |
| 4.9 | Marketplace settings | Browser | Toggle visibility, verify |
| 4.10 | Gym spaces management | Browser | Add/edit spaces |

### Suite 5: Payment Flows (10 min)
⚠️ These use simulated webhooks since Stitch sandbox may not be available.

| # | Test | Surface | Method |
|---|------|---------|--------|
| 5.1 | Payment initiation returns checkout URL | API | POST payment endpoint |
| 5.2 | Successful payment webhook activates membership | API | POST webhook with success payload |
| 5.3 | Failed payment webhook doesn't activate | API | POST webhook with failure payload |
| 5.4 | Webhook signature validation (reject invalid) | API | POST with bad signature |
| 5.5 | Payment state machine: pending → completed | API | Verify state transitions |
| 5.6 | Payment state machine: pending → failed | API | Verify state transitions |
| 5.7 | Duplicate webhook handling (idempotent) | API | Send same webhook twice |

### Suite 6: Admin Dashboard (10 min)

| # | Test | Surface | Method |
|---|------|---------|--------|
| 6.1 | Admin login | Browser | Login with superuser |
| 6.2 | Platform health dashboard | Browser | Verify stats render |
| 6.3 | Gym approval workflow | Browser | Approve a pending gym |
| 6.4 | Gym suspension | Browser | Suspend a gym, verify |
| 6.5 | Complaints management | Browser | View/action complaints |
| 6.6 | Audit log viewer | Browser | Verify log entries |
| 6.7 | Non-admin cannot access admin routes | API | 403 on admin endpoints |

### Suite 7: Responsive / Mobile Web (10 min)
Using viewport resizing to test mobile layouts.

| # | Test | Surface | Method |
|---|------|---------|--------|
| 7.1 | Consumer-web at 375px (iPhone) | Browser | Resize, check layout |
| 7.2 | Consumer-web at 768px (tablet) | Browser | Resize, check layout |
| 7.3 | Gym-web at 375px | Browser | Resize, check layout |
| 7.4 | Gym-web at 768px | Browser | Resize, check layout |
| 7.5 | Navigation menus collapse/expand | Browser | Verify hamburger menu |
| 7.6 | Forms usable on mobile | Browser | Fill forms at mobile width |
| 7.7 | Marketing site responsive | Browser | Check hero, CTAs, footer |

### Suite 8: Edge Cases & Security (10 min)

| # | Test | Surface | Method |
|---|------|---------|--------|
| 8.1 | XSS in form inputs rejected | Browser | Submit script tags |
| 8.2 | SQL injection in search rejected | API | Malicious query params |
| 8.3 | Unauthorized API access returns 401 | API | Requests without token |
| 8.4 | Cross-tenant data isolation | API | Gym A can't see Gym B data |
| 8.5 | POPIA: account deletion request | API | Delete account, verify data purge |
| 8.6 | Rate limits on payment endpoints | API | Burst requests, verify 429 |
| 8.7 | Large file upload handling | API | Oversized file, verify rejection |
| 8.8 | Expired token handling | Browser | Verify redirect to login |

---

## Execution Plan

### Phase 1: Setup (30 min)
1. Spin up local Docker stack
2. Write seed data script (API calls to create test gym + consumer + classes)
3. Verify all frontend dev servers accessible

### Phase 2: API Tests (30 min)
Run Suites 1, 5, 6 (API portions), 8 via direct HTTP calls.
These are fastest and catch backend issues without browser overhead.

### Phase 3: Browser Tests (1-2 hours)
Run Suites 2, 3, 4, 6 (browser portions), 7 via Chrome DevTools.
Each suite is independent — can run in parallel or sequentially.

### Phase 4: Report
Generate a test results summary:
- ✅ Passed / ❌ Failed / ⚠️ Skipped
- Screenshots of failures
- List of bugs found with severity

---

## How to Run with Claude Code

```bash
# In the Claude Code session:
# 1. Start the stack
cd ~/projects/studioloop2026
docker compose -f docker-compose.local.yml up -d

# 2. Start frontend dev servers (separate terminals)
cd frontend/apps/consumer-web && pnpm dev &
cd frontend/apps/gym-web && pnpm dev &

# 3. Claude Code uses Chrome DevTools MCP to:
#    - Navigate to URLs
#    - Fill forms
#    - Click buttons
#    - Assert page content
#    - Take screenshots
#    - Resize viewport for responsive tests

# 4. Claude Code uses curl/httpx for API tests
```

## Notes
- Existing e2e specs in `frontend/e2e/` use mocked API routes — useful for CI but don't test real backend
- This plan tests the REAL integrated stack
- Focus on catching real bugs, not hitting 100% coverage
- Payment tests will use webhook simulation since Stitch sandbox likely unavailable locally
