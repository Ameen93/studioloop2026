import { test, expect } from "@playwright/test";

/**
 * Smoke tests for the StudioLoop web application.
 *
 * These tests verify basic functionality works:
 * - App loads successfully
 * - Basic UI elements are visible
 * - User interactions work (click, etc.)
 *
 * Run with: pnpm test:e2e e2e/smoke.spec.ts
 */

test.describe("Smoke Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page before each test
    await page.goto("/");
  });

  test("home page loads successfully", async ({ page }) => {
    // Verify the page has a title (actual title may vary based on app config)
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);

    // Verify the main heading is visible
    await expect(page.locator("h1")).toBeVisible();
  });

  test("page contains expected content", async ({ page }) => {
    // Check for the Vite + React heading
    await expect(page.locator("h1")).toContainText("Vite + React");

    // Check for the Vite logo link
    const viteLink = page.locator('a[href="https://vite.dev"]');
    await expect(viteLink).toBeVisible();

    // Check for the React logo link
    const reactLink = page.locator('a[href="https://react.dev"]');
    await expect(reactLink).toBeVisible();
  });

  test("counter button works", async ({ page }) => {
    // Find the counter button
    const counterButton = page.locator("button");
    await expect(counterButton).toBeVisible();

    // Verify initial count
    await expect(counterButton).toContainText("count is 0");

    // Click the button and verify count increases
    await counterButton.click();
    await expect(counterButton).toContainText("count is 1");

    // Click again
    await counterButton.click();
    await expect(counterButton).toContainText("count is 2");
  });

  test("page is responsive and accessible", async ({ page }) => {
    // Check that logos have alt text (accessibility)
    const viteLogo = page.locator('img[alt="Vite logo"]');
    await expect(viteLogo).toBeVisible();

    const reactLogo = page.locator('img[alt="React logo"]');
    await expect(reactLogo).toBeVisible();

    // Check that the page has no console errors
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    // Wait a bit for any async errors
    await page.waitForTimeout(1000);

    // Filter out known acceptable errors (e.g., favicon 404)
    const criticalErrors = consoleErrors.filter(
      (err) => !err.includes("favicon")
    );
    expect(criticalErrors).toHaveLength(0);
  });
});
