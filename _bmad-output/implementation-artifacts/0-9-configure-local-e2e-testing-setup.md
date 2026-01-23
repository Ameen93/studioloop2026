# Story 0.9: Configure Local E2E Testing Setup

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want E2E testing configured for web and mobile apps,
So that I can verify complete user flows work correctly.

## Acceptance Criteria

1. **Given** the local development environment is running **When** I configure E2E testing **Then** Playwright is configured for gym-web and consumer-web apps
2. `pnpm test:e2e` runs web E2E tests against local backend
3. Basic smoke tests exist: login, view dashboard, navigate pages
4. Tests run in headless mode by default, with `--headed` option available
5. Detox is configured for consumer-mobile and gym-mobile apps (optional, can be deferred)
6. Test database can be reset between test runs
7. E2E tests are NOT included in CI (run manually or in separate workflow)

## Tasks / Subtasks

- [x] Task 1: Install and configure Playwright for web apps (AC: #1, #4)
  - [x] Add Playwright to `frontend/` root devDependencies
  - [x] Create `frontend/playwright.config.ts` with shared configuration
  - [x] Configure baseURL to point to local frontend (http://localhost:5173)
  - [x] Configure headless mode by default with `--headed` CLI option
  - [x] Configure screenshots on failure and video recording options
  - [x] Create `frontend/e2e/` directory for E2E test files

- [x] Task 2: Add E2E test scripts to package.json (AC: #2)
  - [x] Add `test:e2e` script to `frontend/package.json` (runs Playwright)
  - [x] Add `test:e2e:headed` script for visual debugging
  - [x] Add `test:e2e:ui` script for Playwright UI mode
  - [x] Configure Turborepo to include e2e task (NOT in default `test` pipeline)

- [x] Task 3: Create basic smoke tests for web app (AC: #3)
  - [x] Create `frontend/e2e/smoke.spec.ts` with basic navigation tests
  - [x] Test: Home page loads successfully
  - [x] Test: Page contains expected content (Vite + React heading)
  - [x] Test: Counter button interaction works
  - [x] Create `frontend/e2e/auth.spec.ts` for login flow tests
  - [x] Test: Infrastructure test verifies Playwright setup
  - [x] Test: Login flow tests (skipped until auth UI implemented in Epic 1)
  - [x] Test: Test fixtures are loadable with test credentials

- [x] Task 4: Implement test database reset mechanism (AC: #6)
  - [x] Create helper script `frontend/scripts/reset-test-db.sh` to reset test database
  - [x] Leverage existing `backend/scripts/seed.py --reset` from Story 0.8
  - [x] Add `test:e2e:reset-db` script to package.json
  - [x] Test user (test@studioloop.com) included in seed data

- [x] Task 5: Ensure E2E tests excluded from CI (AC: #7)
  - [x] Verified `.github/workflows/ci.yml` does NOT run `test:e2e`
  - [x] Added comment in ci.yml explaining E2E is manual/separate
  - [x] Created `.github/workflows/e2e.yml` as manual workflow dispatch

- [x] Task 6: Configure Detox for mobile apps (OPTIONAL - DEFERRED) (AC: #5)
  - [x] **DEFERRED:** Mobile apps don't have features to test yet
  - [x] Documented in README that Detox will be configured when mobile apps have features
  - [x] Story notes include planned Detox configuration for future reference

- [x] Task 7: Add E2E documentation and usage guide
  - [x] Create `frontend/e2e/README.md` with setup and usage instructions
  - [x] Document how to run tests in headless vs headed mode
  - [x] Document test database reset procedure
  - [x] Add troubleshooting section for common issues

## Dev Notes

### Current Frontend Structure

```
frontend/
├── apps/
│   ├── web/              # Shared web app (currently serves both gym and consumer)
│   ├── consumer-mobile/  # React Native app for consumers
│   └── gym-mobile/       # React Native app for gym staff
├── packages/
│   ├── api-client/       # Generated API client (@sl/api-client)
│   ├── ui/               # Shared UI components (@sl/ui)
│   └── utils/            # Shared utilities (@sl/utils)
├── package.json          # Root package.json
├── pnpm-workspace.yaml
└── turbo.json
```

**Note:** There is currently only ONE web app (`apps/web`) that will serve both gym staff and consumers. The AC mentions "gym-web and consumer-web" but these are the same app for now. Tests should be structured to handle both user roles.

### Playwright Configuration Strategy

```typescript
// frontend/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Test Database Reset Pattern

The seed script from Story 0.8 already supports `--reset` flag:
```bash
cd backend && uv run python scripts/seed.py --reset
```

This will:
1. Delete all existing seed data (Spaces → Consumers → Gyms)
2. Re-seed with fresh test data
3. Ensure `test@studioloop.com` user exists with password `testpassword123`

### E2E Test Structure

```
frontend/
├── e2e/
│   ├── README.md           # Documentation
│   ├── smoke.spec.ts       # Basic navigation tests
│   ├── auth.spec.ts        # Authentication tests
│   └── fixtures/
│       └── test-data.ts    # Test data constants
├── playwright.config.ts    # Playwright configuration
└── package.json            # Updated with e2e scripts
```

### turbo.json Configuration

E2E tests should NOT be included in the default CI pipeline:

```json
{
  "tasks": {
    "test": { ... },  // Unit tests only
    "test:e2e": {
      "cache": false,
      "dependsOn": []  // No dependencies - manual run only
    }
  }
}
```

### Package Manager Commands

Project uses `pnpm` as package manager:
- Install: `pnpm add -D @playwright/test`
- Run scripts: `pnpm test:e2e`
- Workspace filter: `pnpm --filter @sl/web test:e2e`

### Architecture Compliance

- **ARCH-24**: Test files use `*.spec.ts` naming convention (per architecture doc)
- **E2E Location**: `e2e/` at frontend root (per architecture doc - "E2E tests: e2e/ at app root")
- **Test Framework**: Playwright for web, Detox for mobile (per architecture doc)

### Previous Story Intelligence

From Story 0.8 (Seed Data Scripts):
- Test user credentials: `test@studioloop.com` / `testpassword123`
- Reset command: `uv run python scripts/seed.py --reset`
- Seed data includes 5 gyms, 16 consumers, 14 spaces
- Backend runs on port 8000 by default

From Story 0.5 (Local CI - in review):
- GitHub Actions CI runs `pnpm test` (unit tests)
- Linting and type-checking configured
- E2E should NOT be added to this workflow

### Web App Current State

The web app (`apps/web`) currently:
- Uses Vite + React 19
- Has Vitest configured for unit tests
- Uses TailwindCSS via @tailwindcss/vite
- Has no routing yet (just single page)
- Runs on port 5173 by default

### Testing Requirements

1. **Smoke test**: App loads, basic navigation works
2. **Auth test**: Login flow works with test credentials
3. **Database isolation**: Tests start with clean, seeded database
4. **Headless by default**: CI-friendly, with `--headed` for debugging
5. **Manual trigger**: NOT included in normal CI runs

### Detox Configuration (Optional/Deferred)

If implementing Detox for mobile:
```javascript
// .detoxrc.js
module.exports = {
  testRunner: {
    args: {
      $0: 'jest',
      config: 'e2e/jest.config.js'
    }
  },
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/...',
      build: 'xcodebuild ...'
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/...',
      build: 'cd android && ./gradlew assembleDebug'
    }
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } },
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_4_API_30' } }
  }
};
```

**Recommendation:** Defer Detox setup to when mobile apps have actual features to test.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 0.9]
- [Source: _bmad-output/planning-artifacts/architecture.md#Testing Framework]
- [Source: _bmad-output/planning-artifacts/architecture.md#Test Location]
- [Source: backend/scripts/seed.py - Database seed/reset script]
- [Source: frontend/apps/web/package.json - Web app configuration]
- [Source: frontend/package.json - Root package configuration]
- [Playwright Documentation: https://playwright.dev/docs/intro]
- [Detox Documentation: https://wix.github.io/Detox/]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None

### Completion Notes List

1. **Playwright Configuration**: Installed @playwright/test ^1.57.0 at frontend workspace root. Created `playwright.config.ts` with Chromium browser, headless mode by default, screenshot on failure, video on retry. Configured webServer to start web app dev server automatically.

2. **E2E Test Scripts**: Added four scripts to `frontend/package.json`:
   - `test:e2e` - Run tests headless
   - `test:e2e:headed` - Run with visible browser
   - `test:e2e:ui` - Playwright interactive UI mode
   - `test:e2e:reset-db` - Reset and seed test database

3. **Smoke Tests**: Created 5 passing smoke tests in `e2e/smoke.spec.ts`:
   - Home page loads successfully
   - Page contains expected content (Vite + React)
   - Counter button interaction works
   - Page is responsive and accessible (no console errors)

4. **Auth Tests**: Created `e2e/auth.spec.ts` with login flow tests marked as `.skip()` until auth UI is implemented in Epic 1. Infrastructure test verifies Playwright and test fixtures work correctly.

5. **Test Data Fixtures**: Created `e2e/fixtures/test-data.ts` with test user credentials (`test@studioloop.com`/`testpassword123`) and gym data constants matching seed data from Story 0.8.

6. **Database Reset**: Created `frontend/scripts/reset-test-db.sh` shell script that runs backend seed script with `--reset` flag. Leverages existing seed infrastructure from Story 0.8.

7. **CI Exclusion**: Verified CI workflow only runs unit tests (`pnpm test`), not E2E. Added explanatory comment to `ci.yml`. Created separate `e2e.yml` workflow for manual dispatch with full backend/database setup.

8. **Detox (DEFERRED)**: Task 6 deferred as per story recommendation. Mobile apps don't have features to test yet. Documented future Detox configuration in README.

9. **Documentation**: Created comprehensive `frontend/e2e/README.md` with prerequisites, running tests, test structure, troubleshooting, and best practices.

10. **Test Results**: 5 passed, 5 skipped (auth tests await Epic 1). All unit tests (6) and linting pass.

### File List

**Created:**
- `frontend/playwright.config.ts` - Playwright configuration
- `frontend/e2e/smoke.spec.ts` - Smoke tests (4 tests)
- `frontend/e2e/auth.spec.ts` - Auth tests (5 skipped + 1 passing)
- `frontend/e2e/fixtures/test-data.ts` - Test data constants
- `frontend/e2e/README.md` - E2E testing documentation
- `frontend/scripts/reset-test-db.sh` - Database reset script
- `.github/workflows/e2e.yml` - Manual E2E workflow

**Modified:**
- `frontend/package.json` - Added e2e scripts
- `frontend/turbo.json` - Added test:e2e task
- `.github/workflows/ci.yml` - Added comment about E2E exclusion
