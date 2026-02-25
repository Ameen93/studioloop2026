import { expect, test } from "@playwright/test";

test.describe("Gym Web Journey", () => {
  test("staff login, member search, manual check-in, and logout", async ({ page }) => {
    await page.route("**/api/v1/auth/staff/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "staff-access-token",
          refresh_token: "staff-refresh-token",
          role: "front_desk",
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
            today_check_ins: 3,
            today_bookings: 5,
          },
          quick_metrics: {
            total_revenue: 25000,
            active_memberships: 80,
          },
          action_items: {
            waitlist_alerts: 0,
            expiring_memberships: 1,
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

    await page.route("**/api/v1/gyms/me/check_ins/search?**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            consumer_id: "consumer-123",
            first_name: "Jamie",
            last_name: "Lee",
            phone: "+27 82 555 0101",
          },
        ]),
      });
    });

    await page.route("**/api/v1/gyms/me/check_ins/manual", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          check_in_id: "checkin-123",
          status: "checked_in",
        }),
      });
    });

    await page.goto("/login");

    await page.fill('input[name="email"]', "staff@studioloop.com");
    await page.fill('input[name="password"]', "testpassword123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole("heading", { name: "Dashboard", exact: true })).toBeVisible();

    await page.getByRole("link", { name: "Check-in" }).click();
    await expect(page).toHaveURL(/\/checkin$/);
    await expect(page.getByRole("heading", { name: "Member Check-in" })).toBeVisible();

    await page.fill('input[placeholder="Search by name or phone number..."]', "jamie");
    await page.getByRole("button", { name: "Search" }).click();

    await expect(page.getByText("Jamie Lee")).toBeVisible();
    await page.getByRole("button", { name: "Check In" }).click();
    await expect(page.getByText("Checked In")).toBeVisible();

    await page.getByRole("button", { name: "Sign Out" }).click();
    await expect(page).toHaveURL(/\/login$/);
  });

  test("expires staff session and returns to login when API and refresh both return 401", async ({
    page,
  }) => {
    await page.route("**/api/v1/**", async (route) => {
      const url = route.request().url();

      if (url.includes("/api/v1/auth/staff/login")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: "staff-access-token",
            refresh_token: "staff-refresh-token",
            role: "front_desk",
            gym_id: "gym-123",
          }),
        });
        return;
      }

      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({
          detail: {
            code: "TOKEN_INVALID",
            message: "Token invalid",
          },
        }),
      });
    });

    await page.goto("/login");
    await page.fill('input[name="email"]', "staff@studioloop.com");
    await page.fill('input[name="password"]', "testpassword123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByText("Sign in with your staff credentials")).toBeVisible();
  });
});
