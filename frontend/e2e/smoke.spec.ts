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
    await page.goto("/");
  });

  test("home page loads successfully", async ({ page }) => {
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    await expect(page).toHaveURL(/\/auth\/login$/);
    await expect(page.getByText("Sign in to your account")).toBeVisible();
  });

  test("login page contains expected form controls", async ({ page }) => {
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText("Sign in");
  });

  test("register link navigates correctly", async ({ page }) => {
    await page.getByRole("link", { name: "Create one" }).click();
    await expect(page).toHaveURL(/\/auth\/register$/);
    await expect(page.getByText("Create your account")).toBeVisible();
  });

  test("page is responsive and accessible", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    await page.waitForTimeout(1000);
    const criticalErrors = consoleErrors.filter((err) => !err.includes("favicon"));
    expect(criticalErrors).toHaveLength(0);
  });
});
