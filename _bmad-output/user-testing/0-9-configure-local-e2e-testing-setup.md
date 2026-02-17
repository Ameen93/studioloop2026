# QA Checklist: Story 0.9 - Configure Local E2E Testing Setup

**Story:** Configure Local E2E Testing Setup
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] Local development environment is running (Docker containers for Postgres + Redis)
- [ ] Backend server is running on http://localhost:8000
- [ ] Frontend dev server is running on http://localhost:5173
- [ ] Node.js 18+ installed
- [ ] pnpm installed (project uses pnpm as package manager)
- [ ] Seed data has been populated (test@studioloop.com account exists)

---

## Environment Setup

### 1. Start Backend Services

```bash
# Navigate to backend directory
cd backend

# Start Docker services (Postgres + Redis)
docker compose up -d

# Run database migrations
uv run alembic upgrade head

# Seed the database with test data
uv run python scripts/seed.py --reset

# Start the backend server
uv run uvicorn app.main:app --reload
```

- [ ] Backend server is accessible at http://localhost:8000
- [ ] API docs available at http://localhost:8000/docs

### 2. Start Frontend Development Server

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
pnpm install

# Start development server
pnpm dev
```

- [ ] Frontend is accessible at http://localhost:5173

---

## Test Cases

### TC-1: Playwright Installation and Configuration

**Acceptance Criterion:** #1 - Playwright is configured for gym-web and consumer-web apps

**Steps:**
1. Check Playwright is installed in frontend
   ```bash
   cd frontend
   cat package.json | grep playwright
   ```

2. Verify Playwright config exists
   ```bash
   ls -la playwright.config.ts
   ```

3. Verify e2e directory structure
   ```bash
   ls -la e2e/
   ```

**Expected Results:**
- [ ] `@playwright/test` appears in devDependencies
- [ ] `playwright.config.ts` exists at frontend root
- [ ] `e2e/` directory exists with test files

**Actual Results:** _______________

---

### TC-2: E2E Test Execution via pnpm

**Acceptance Criterion:** #2 - `pnpm test:e2e` runs web E2E tests against local backend

**Steps:**
1. Ensure backend and frontend are running
2. Run E2E tests
   ```bash
   cd frontend
   pnpm test:e2e
   ```

3. Verify test output

**Expected Results:**
- [ ] Command executes without errors
- [ ] Tests connect to local backend (http://localhost:8000 or frontend proxy)
- [ ] Test results are displayed in terminal
- [ ] HTML report is generated (check `playwright-report/` directory)

**Actual Results:** _______________

---

### TC-3: Basic Smoke Tests Exist

**Acceptance Criterion:** #3 - Basic smoke tests exist: login, view dashboard, navigate pages

**Steps:**
1. Check smoke test file exists
   ```bash
   cat frontend/e2e/smoke.spec.ts
   ```

2. Check auth test file exists
   ```bash
   cat frontend/e2e/auth.spec.ts
   ```

3. Verify tests cover required scenarios
   - Home page loads
   - Navigation works
   - Login page renders
   - Login with test credentials

**Expected Results:**
- [ ] `smoke.spec.ts` contains navigation tests
- [ ] `auth.spec.ts` contains login flow tests
- [ ] Tests use test credentials (test@studioloop.com / testpassword123)
- [ ] All smoke tests pass when run

**Actual Results:** _______________

---

### TC-4: Headless Mode and --headed Option

**Acceptance Criterion:** #4 - Tests run in headless mode by default, with `--headed` option available

**Steps:**
1. Run tests in headless mode (default)
   ```bash
   cd frontend
   pnpm test:e2e
   ```

2. Run tests in headed mode
   ```bash
   cd frontend
   pnpm test:e2e:headed
   # OR
   pnpm test:e2e -- --headed
   ```

3. Verify browser window appears in headed mode

**Expected Results:**
- [ ] Default run shows no browser window (headless)
- [ ] `--headed` option shows browser window
- [ ] Tests pass in both modes

**Actual Results:** _______________

---

### TC-5: Detox Configuration (Optional)

**Acceptance Criterion:** #5 - Detox is configured for consumer-mobile and gym-mobile apps (optional, can be deferred)

**Steps:**
1. Check if Detox was configured
   ```bash
   ls -la frontend/.detoxrc.js 2>/dev/null || echo "Detox not configured (OK - optional)"
   ```

2. If configured, check mobile app directories
   ```bash
   ls frontend/apps/consumer-mobile/e2e/ 2>/dev/null || echo "No mobile e2e"
   ls frontend/apps/gym-mobile/e2e/ 2>/dev/null || echo "No mobile e2e"
   ```

**Expected Results:**
- [ ] Either Detox is configured with basic mobile tests
- [ ] OR Detox is explicitly deferred (documented in story completion notes)

**Actual Results:** _______________

---

### TC-6: Test Database Reset

**Acceptance Criterion:** #6 - Test database can be reset between test runs

**Steps:**
1. Reset and seed the database
   ```bash
   cd backend
   uv run python scripts/seed.py --reset
   ```

2. Verify seed data is fresh
   ```bash
   # Check test user exists by attempting login via API
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@studioloop.com", "password": "testpassword123"}'
   ```

3. Check if E2E pretest script exists
   ```bash
   cat frontend/package.json | grep pretest
   ```

**Expected Results:**
- [ ] `--reset` flag clears and re-seeds data
- [ ] Test user can log in after reset
- [ ] E2E tests can start with clean database state

**Actual Results:** _______________

---

### TC-7: E2E Tests Not in CI

**Acceptance Criterion:** #7 - E2E tests are NOT included in CI (run manually or in separate workflow)

**Steps:**
1. Check CI workflow
   ```bash
   cat .github/workflows/ci.yml | grep -E "(e2e|playwright)"
   ```

2. Verify `test` task in turbo.json doesn't include e2e
   ```bash
   cat frontend/turbo.json
   ```

3. Check for separate E2E workflow (optional)
   ```bash
   ls .github/workflows/ | grep -i e2e
   ```

**Expected Results:**
- [ ] CI workflow does NOT run `test:e2e`
- [ ] Normal `pnpm test` only runs unit tests
- [ ] Optional: Separate `e2e.yml` workflow exists for manual runs
- [ ] Comment in ci.yml explains E2E is manual

**Actual Results:** _______________

---

## Edge Cases & Error Scenarios

### EC-1: E2E Test Without Backend Running

**Scenario:** Run E2E tests when backend is not running

**Test:**
```bash
# Stop backend first, then run E2E
cd frontend
pnpm test:e2e
```

**Expected:** Tests fail gracefully with clear error message about backend connection

**Result:** _______________

---

### EC-2: E2E Test With Empty Database

**Scenario:** Run E2E tests without seeding the database

**Test:**
```bash
cd backend
uv run python scripts/seed.py --reset  # This seeds, but...
# Manually clear test user somehow, then run E2E login test
cd frontend
pnpm test:e2e -- auth.spec.ts
```

**Expected:** Login tests fail with appropriate error (invalid credentials)

**Result:** _______________

---

### EC-3: Playwright UI Mode

**Scenario:** Test Playwright's interactive UI mode

**Test:**
```bash
cd frontend
pnpm test:e2e:ui
# OR
npx playwright test --ui
```

**Expected:** Playwright UI opens in browser, allowing interactive test execution

**Result:** _______________

---

## Rollback Steps

If testing fails or you need to reset:

### Full Rollback
```bash
# Remove Playwright and E2E setup
cd frontend
rm -rf e2e/
rm playwright.config.ts
pnpm remove @playwright/test

# Revert package.json changes (if using git)
git checkout -- package.json turbo.json
pnpm install
```

### Partial Rollback
```bash
# Reset just the test database
cd backend
uv run python scripts/seed.py --reset

# Clear Playwright cache and reports
cd frontend
rm -rf playwright-report/
rm -rf test-results/
```

### Environment Cleanup
```bash
# Stop all running servers
# Terminal 1: Ctrl+C on backend
# Terminal 2: Ctrl+C on frontend

# Stop Docker services
cd backend
docker compose down
```

---

## Sign-Off

### Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-1: Playwright Installation | [ ] Pass / [ ] Fail | |
| TC-2: E2E Test Execution | [ ] Pass / [ ] Fail | |
| TC-3: Smoke Tests Exist | [ ] Pass / [ ] Fail | |
| TC-4: Headless/Headed Mode | [ ] Pass / [ ] Fail | |
| TC-5: Detox Config (Optional) | [ ] Pass / [ ] Fail / [ ] Deferred | |
| TC-6: Database Reset | [ ] Pass / [ ] Fail | |
| TC-7: Not in CI | [ ] Pass / [ ] Fail | |
| EC-1: No Backend Error | [ ] Pass / [ ] Fail | |
| EC-2: Empty Database | [ ] Pass / [ ] Fail | |
| EC-3: UI Mode | [ ] Pass / [ ] Fail | |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready to proceed
- [ ] **FAIL** - Issues found, requires dev attention

**Blocking Issues:** _______________

**Non-Blocking Notes:** _______________

**Tested By:** Ameen
**Date:** _______________
**Signature:** _______________

---

## Next Story

Once this story passes QA:
1. Update sprint-status.yaml: `0-9-configure-local-e2e-testing-setup: done`
2. Run `epic-0-retrospective` workflow (this is the last story in Epic 0!)
3. Proceed to Epic 1: Authentication & Identity Platform
