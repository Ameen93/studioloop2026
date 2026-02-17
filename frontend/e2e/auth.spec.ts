import { test, expect } from "@playwright/test";
import { TEST_USER } from "./fixtures/test-data";

/**
 * Authentication E2E tests for StudioLoop.
 *
 * NOTE: These tests require:
 * 1. Backend running on http://localhost:8000
 * 2. Database seeded with test user: uv run python scripts/seed.py --reset
 * 3. Auth pages implemented in the web app (Epic 1)
 *
 * Tests are marked as skip until auth UI is implemented.
 * Remove .skip() when auth routes are available.
 *
 * Run with: pnpm test:e2e e2e/auth.spec.ts
 */

test.describe("Authentication", () => {
  // Skip all auth tests until auth UI is implemented
  // TODO: Remove .skip when Epic 1 (Authentication) is complete
  test.describe.skip("Login Flow", () => {
    test("login page renders correctly", async ({ page }) => {
      await page.goto("/login");

      // Verify login form elements
      await expect(page.locator('input[name="email"]')).toBeVisible();
      await expect(page.locator('input[name="password"]')).toBeVisible();
      await expect(
        page.locator('button[type="submit"]', { hasText: /log in|sign in/i })
      ).toBeVisible();
    });

    test("shows validation errors for empty form", async ({ page }) => {
      await page.goto("/login");

      // Submit empty form
      await page.locator('button[type="submit"]').click();

      // Expect validation errors
      await expect(page.locator("text=email is required")).toBeVisible();
      await expect(page.locator("text=password is required")).toBeVisible();
    });

    test("shows error for invalid credentials", async ({ page }) => {
      await page.goto("/login");

      // Fill in invalid credentials
      await page.fill('input[name="email"]', "wrong@example.com");
      await page.fill('input[name="password"]', "wrongpassword");

      // Submit form
      await page.locator('button[type="submit"]').click();

      // Expect error message
      await expect(
        page.locator("text=/invalid|incorrect|failed/i")
      ).toBeVisible();
    });

    test("successful login redirects to dashboard", async ({ page }) => {
      await page.goto("/login");

      // Fill in valid test credentials
      await page.fill('input[name="email"]', TEST_USER.email);
      await page.fill('input[name="password"]', TEST_USER.password);

      // Submit form
      await page.locator('button[type="submit"]').click();

      // Wait for navigation to dashboard
      await expect(page).toHaveURL(/dashboard|home/);

      // Verify user is logged in
      await expect(page.locator(`text=${TEST_USER.fullName}`)).toBeVisible();
    });

    test("logout returns user to home page", async ({ page }) => {
      // First, log in
      await page.goto("/login");
      await page.fill('input[name="email"]', TEST_USER.email);
      await page.fill('input[name="password"]', TEST_USER.password);
      await page.locator('button[type="submit"]').click();
      await expect(page).toHaveURL(/dashboard|home/);

      // Find and click logout button
      await page.locator('button:has-text("Logout")').click();

      // Verify redirected to home/login
      await expect(page).toHaveURL(/^\/$|login/);
    });
  });

  // Placeholder test that always passes - verifies test infrastructure works
  test("test infrastructure is configured correctly", async ({ page }) => {
    // This test verifies that:
    // 1. Playwright is installed correctly
    // 2. The web app can be accessed
    // 3. Test fixtures are loadable

    await page.goto("/");
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);

    // Verify test data imports work
    expect(TEST_USER.email).toBe("test@studioloop.com");
    expect(TEST_USER.password).toBe("testpassword123");
  });
});
