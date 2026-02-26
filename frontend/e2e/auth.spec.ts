import { test, expect } from "@playwright/test";
import { TEST_USER } from "./fixtures/test-data";

/**
 * Authentication E2E tests for StudioLoop.
 *
 * NOTE: These tests require:
 * 1. Backend running on http://localhost:8000
 * 2. Database seeded with test user: uv run python scripts/seed.py --reset
 * 3. Frontend app running on http://localhost:5173 (auto-started by Playwright config)
 *
 * Run with: pnpm test:e2e e2e/auth.spec.ts
 */

test.describe("Authentication", () => {
  test("login page renders correctly", async ({ page }) => {
    await page.goto("/auth/login");
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(
      page.locator('button[type="submit"]', { hasText: /sign in/i })
    ).toBeVisible();
  });

  test("redirects unauthenticated home visits to login", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/\/auth\/login$/);
  });

  test("shows password validation error for short password", async ({ page }) => {
    await page.goto("/auth/login");
    await page.fill('input[name="email"]', "valid@example.com");
    await page.fill('input[name="password"]', "short");
    await page.locator('button[type="submit"]').click();

    await expect(page.getByText("Password must be at least 8 characters")).toBeVisible();
  });

  test("surfaces duplicate email error during registration", async ({ page }) => {
    await page.route("**/api/v1/auth/consumer/register", async (route) => {
      await route.fulfill({
        status: 400,
        contentType: "application/json",
        body: JSON.stringify({
          detail: {
            code: "EMAIL_ALREADY_EXISTS",
            message: "Email already registered",
          },
        }),
      });
    });

    await page.goto("/auth/register");
    await page.fill('input[name="first_name"]', "Jane");
    await page.fill('input[name="last_name"]', "Tester");
    await page.fill('input[name="email"]', "already@exists.com");
    await page.fill('input[name="password"]', "validpassword");
    await page.fill('input[name="confirmPassword"]', "validpassword");
    await page.locator('button[type="submit"]').click();

    await expect(page.getByText("An account with this email already exists")).toBeVisible();
  });

  test("surfaces invalid credentials from backend", async ({ page }) => {
    await page.route("**/api/v1/auth/consumer/login", async (route) => {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({
          detail: {
            code: "INVALID_CREDENTIALS",
            message: "Invalid email or password",
          },
        }),
      });
    });

    await page.goto("/auth/login");
    await page.fill('input[name="email"]', "unknown-user@example.com");
    await page.fill('input[name="password"]', "nottherightpassword");
    await page.locator('button[type="submit"]').click();

    await expect(page.getByText("Invalid email or password")).toBeVisible();
  });

  test("successful login navigates to authenticated home", async ({ page }) => {
    await page.route("**/api/v1/auth/consumer/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "fake-access-token",
          refresh_token: "fake-refresh-token",
          token_type: "bearer",
        }),
      });
    });

    await page.goto("/auth/login");
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.locator('button[type="submit"]').click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByText("You are signed in")).toBeVisible();
  });
});
