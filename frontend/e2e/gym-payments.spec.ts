import { expect, test, type Page } from "@playwright/test";

async function mockStaffLoginAndDashboard(page: Page): Promise<void> {
  await page.route("**/api/v1/auth/staff/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "staff-access-token",
        refresh_token: "staff-refresh-token",
        role: "manager",
        gym_id: "gym-123",
      }),
    });
  });

  await page.route("**/api/v1/analytics/gyms/gym-123/dashboard", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        today_summary: {
          today_check_ins: 6,
          today_bookings: 11,
        },
        quick_metrics: {
          total_revenue: 98000,
          active_memberships: 120,
        },
        action_items: {
          waitlist_alerts: 1,
          expiring_memberships: 2,
        },
      }),
    });
  });

  await page.route("**/api/v1/payments/gyms/gym-123/failed/action-items", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });
}

async function loginStaff(page: Page): Promise<void> {
  await page.goto("/login");
  await page.fill('input[name="email"]', "manager@studioloop.com");
  await page.fill('input[name="password"]', "testpassword123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test.describe("Gym Payments", () => {
  test("shows payment metrics, failed tab, and payout breakdown", async ({ page }) => {
    await mockStaffLoginAndDashboard(page);

    await page.route("**/api/v1/payments/gyms/gym-123", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          summary: {
            total_received_cents: 350000,
            total_pending_cents: 25000,
            total_failed_cents: 12000,
          },
          items: [
            {
              payment_id: "pay-1",
              member_name: "Jamie Lee",
              amount_cents: 12000,
              payment_type: "membership",
              status: "failed",
              created_at: "2026-02-19T07:00:00Z",
            },
            {
              payment_id: "pay-2",
              member_name: "Taylor Morgan",
              amount_cents: 9000,
              payment_type: "pay_per_class",
              status: "completed",
              created_at: "2026-02-19T09:00:00Z",
            },
          ],
        }),
      });
    });

    await page.route("**/api/v1/payments/gyms/gym-123/reports/marketplace-payout", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          net_payout_cents: 220000,
          payout_schedule: "Weekly",
          class_breakdown: [
            {
              class_name: "Power Yoga",
              bookings: 18,
              gross_revenue_cents: 216000,
            },
          ],
        }),
      });
    });

    await loginStaff(page);
    await page.getByRole("link", { name: "Payments" }).click();

    await expect(page).toHaveURL(/\/payments$/);
    await expect(page.getByRole("heading", { name: "Payments" })).toBeVisible();
    await expect(page.getByText("R 3500.00")).toBeVisible();
    await expect(page.getByText("R 250.00")).toBeVisible();
    await expect(page.locator("p", { hasText: "R 120.00" })).toBeVisible();
    await expect(page.getByText("R 2200.00")).toBeVisible();

    await page.getByRole("button", { name: /^Failed \(1\)$/ }).click();
    await expect(page.getByText("pay-1")).toBeVisible();
    await expect(page.getByText("pay-2")).not.toBeVisible();

    await page.getByRole("button", { name: "Marketplace Payouts" }).click();
    await expect(page.getByRole("heading", { name: "Payout Breakdown" })).toBeVisible();
    await expect(page.getByText("Power Yoga")).toBeVisible();
    await expect(page.getByText("18")).toBeVisible();
    await expect(page.getByText("R 2160.00")).toBeVisible();
  });

  test("shows payment error banner when backend fails", async ({ page }) => {
    await mockStaffLoginAndDashboard(page);

    await page.route("**/api/v1/payments/gyms/gym-123", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          detail: { code: "INTERNAL_ERROR", message: "Unexpected failure" },
        }),
      });
    });

    await page.route("**/api/v1/payments/gyms/gym-123/reports/marketplace-payout", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          detail: { code: "INTERNAL_ERROR", message: "Unexpected failure" },
        }),
      });
    });

    await loginStaff(page);
    await page.getByRole("link", { name: "Payments" }).click();

    await expect(page).toHaveURL(/\/payments$/);
    await expect(page.getByText("Could not load all payment data.")).toBeVisible();
  });
});
