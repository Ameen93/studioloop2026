# StudioLoop E2E Testing

End-to-end tests for StudioLoop web application using [Playwright](https://playwright.dev/).

## Prerequisites

Before running E2E tests, ensure:

1. **Backend is running** with database:
   ```bash
   cd backend
   docker compose up -d          # Start Postgres + Redis
   uv run alembic upgrade head   # Run migrations
   uv run uvicorn app.main:app --reload  # Start backend
   ```

2. **Database is seeded** with test data:
   ```bash
   cd backend
   uv run python scripts/seed.py --reset
   ```

3. **Frontend dependencies** are installed:
   ```bash
   cd frontend
   pnpm install
   ```

## Running Tests

### Basic Commands

```bash
# Run all E2E tests (headless)
pnpm test:e2e

# Run tests with browser visible (for debugging)
pnpm test:e2e:headed

# Run tests in Playwright UI mode (interactive)
pnpm test:e2e:ui

# Reset test database before running
pnpm test:e2e:reset-db
```

### Running Specific Tests

```bash
# Run only smoke tests
pnpm test:e2e e2e/smoke.spec.ts

# Run only auth tests
pnpm test:e2e e2e/auth.spec.ts

# Run tests matching a pattern
pnpm test:e2e --grep "home page"
```

### Debug Mode

```bash
# Run with browser visible and slow motion
pnpm test:e2e:headed -- --slow-mo=500

# Run specific test in debug mode
pnpm test:e2e -- --debug e2e/smoke.spec.ts
```

## Test Structure

```
frontend/
├── e2e/
│   ├── README.md           # This file
│   ├── smoke.spec.ts       # Basic app loading/navigation tests
│   ├── auth.spec.ts        # Authentication flow tests
│   └── fixtures/
│       └── test-data.ts    # Test constants (users, gyms, etc.)
├── playwright.config.ts    # Playwright configuration
├── playwright-report/      # HTML test reports (generated)
└── test-results/          # Test artifacts (generated)
```

## Test User Credentials

The seed script creates a test user:

- **Email:** `test@studioloop.com`
- **Password:** `testpassword123`

These credentials are available in `e2e/fixtures/test-data.ts`.

## Configuration

The Playwright configuration is in `frontend/playwright.config.ts`:

- **Base URL:** `http://localhost:5173` (Vite dev server)
- **Browser:** Chromium by default
- **Screenshots:** Captured on failure
- **Videos:** Recorded on retry
- **Reports:** HTML report generated in `playwright-report/`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:5173` | Frontend dev server URL |
| `CI` | - | Set in CI to change behavior |

## CI/CD Integration

E2E tests are **NOT** included in the standard CI pipeline (`ci.yml`) because they require a running backend and database.

### Manual Workflow

A separate `e2e.yml` workflow is available for manual dispatch:

1. Go to Actions tab in GitHub
2. Select "E2E Tests" workflow
3. Click "Run workflow"
4. Choose browser (chromium/firefox/webkit/all)

### Running Locally Before PR

Before creating a PR, run E2E tests locally:

```bash
# Start backend (terminal 1)
cd backend
docker compose up -d
uv run alembic upgrade head
uv run python scripts/seed.py --reset
uv run uvicorn app.main:app --reload

# Run E2E tests (terminal 2)
cd frontend
pnpm test:e2e
```

## Troubleshooting

### Tests Fail to Connect

**Error:** `net::ERR_CONNECTION_REFUSED`

**Solution:** Ensure the web app dev server is running:
```bash
# Option 1: Let Playwright start it (automatic)
pnpm test:e2e

# Option 2: Start manually first
pnpm --filter @sl/web dev
pnpm test:e2e
```

### Database Not Seeded

**Error:** Login tests fail with invalid credentials

**Solution:** Reset and seed the database:
```bash
cd backend
uv run python scripts/seed.py --reset
```

### Browser Not Installed

**Error:** `Executable doesn't exist`

**Solution:** Install Playwright browsers:
```bash
npx playwright install chromium
# Or install all browsers:
npx playwright install
```

### Slow Tests on First Run

Playwright needs to download browsers on first run. This is normal and takes a few minutes.

### Permission Denied on Linux

If you see permission errors when running browsers on Linux:

```bash
# Install browser dependencies
npx playwright install-deps
```

## Writing New Tests

### Test Template

```typescript
import { test, expect } from "@playwright/test";
import { TEST_USER } from "./fixtures/test-data";

test.describe("Feature Name", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should do something", async ({ page }) => {
    // Arrange
    await page.goto("/some-page");

    // Act
    await page.click("button");

    // Assert
    await expect(page.locator("h1")).toContainText("Expected");
  });
});
```

### Best Practices

1. **Use data-testid** for selectors when possible
2. **Wait for elements** before interacting
3. **Keep tests independent** - each test should work alone
4. **Use fixtures** for shared test data
5. **Handle loading states** explicitly

## Mobile E2E Testing (Detox)

Mobile E2E testing with Detox is **deferred** until mobile apps have features to test.

When ready, Detox will be configured for:
- `apps/consumer-mobile` - Consumer iOS/Android app
- `apps/gym-mobile` - Gym staff iOS/Android app

See the story notes for planned Detox configuration.

## Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright VS Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright)
