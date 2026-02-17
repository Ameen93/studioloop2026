import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration for StudioLoop E2E tests.
 *
 * Run with:
 *   pnpm test:e2e          - Headless mode (default)
 *   pnpm test:e2e:headed   - Visual debugging
 *   pnpm test:e2e:ui       - Playwright UI mode
 *
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Test directory location
  testDir: "./e2e",

  // Run tests in files in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [["html", { open: "never" }], ["list"]],

  // Shared settings for all projects
  use: {
    // Base URL for navigation - Vite dev server
    baseURL: process.env.BASE_URL || "http://localhost:5173",

    // Collect trace when retrying the failed test
    trace: "on-first-retry",

    // Capture screenshot only on failure
    screenshot: "only-on-failure",

    // Record video only on retry
    video: "on-first-retry",

    // Timeout for each action (click, fill, etc.)
    actionTimeout: 10000,

    // Timeout for each navigation
    navigationTimeout: 30000,
  },

  // Timeout for each test
  timeout: 30000,

  // Configure projects for major browsers
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    // Uncomment to add more browsers
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // Web server configuration - starts the web app dev server before tests
  webServer: {
    command: "pnpm --filter @sl/web dev",
    url: "http://localhost:5173",
    // Reuse existing server when running locally
    reuseExistingServer: !process.env.CI,
    // Timeout for server to start
    timeout: 120000,
    // Don't show server output unless error
    stdout: "ignore",
    stderr: "pipe",
  },

  // Output directory for test artifacts
  outputDir: "test-results",

  // Expect timeout
  expect: {
    timeout: 5000,
  },
});
