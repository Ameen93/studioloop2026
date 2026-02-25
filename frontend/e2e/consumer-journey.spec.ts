import { expect, test } from "@playwright/test";

test.describe("Consumer Web Journey", () => {
  test("login, discover class, book class, and logout", async ({ page }) => {
    await page.route("**/api/v1/auth/consumer/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "consumer-access-token",
          refresh_token: "consumer-refresh-token",
          token_type: "bearer",
        }),
      });
    });

    await page.route("**/api/v1/analytics/me/stats", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_classes_this_month: 4,
          current_streak_weeks: 2,
        }),
      });
    });

    await page.route("**/api/v1/analytics/me/class-history", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          items: [
            {
              session_id: "sess-history-1",
              class_name: "Power Yoga",
              gym_id: "gym-123",
              attended_at: "2026-02-18T08:00:00Z",
            },
          ],
        }),
      });
    });

    await page.route("**/api/v1/gyms/consumer/qr_code", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          todays_booking_ids: ["booking-1"],
          qr_token: "qr-token",
          expires_at: "2026-02-19T23:59:59Z",
        }),
      });
    });

    await page.route("**/api/v1/marketplace/classes?**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            session_id: "session-123",
            title: "Sunrise Flow",
            gym_name: "FitZone Sandton",
            city: "Johannesburg",
            province: "Gauteng",
            start_time: "2026-02-20T06:30:00Z",
            end_time: "2026-02-20T07:30:00Z",
            capacity: 20,
            spots_booked: 8,
            price_cents: 12000,
          },
        ]),
      });
    });

    await page.route("**/api/v1/marketplace/classes/session-123", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          session_id: "session-123",
          gym_id: "gym-123",
          gym_name: "FitZone Sandton",
          class_type: "yoga",
          title: "Sunrise Flow",
          description: "A guided morning flow session.",
          instructor_name: "Alex Kim",
          instructor_bio: "Certified yoga coach.",
          start_time: "2026-02-20T06:30:00Z",
          end_time: "2026-02-20T07:30:00Z",
          space_name: "Main Studio",
          address_line1: "100 Main Road",
          city: "Johannesburg",
          province: "Gauteng",
          price_cents: 12000,
          capacity: 20,
          spots_remaining: 12,
        }),
      });
    });

    await page.route("**/api/v1/gyms/consumer/bookings/pay_per_class", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          booking_id: "booking-123",
          status: "confirmed",
        }),
      });
    });

    await page.goto("/login");

    await page.fill('input[name="email"]', "test@studioloop.com");
    await page.fill('input[name="password"]', "testpassword123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole("heading", { name: "My Activity" })).toBeVisible();

    await page.getByRole("link", { name: "Find a class" }).click();
    await expect(page).toHaveURL(/\/discover$/);
    await expect(page.getByRole("heading", { name: "Discover Classes" })).toBeVisible();

    await page.getByRole("link", { name: /Sunrise Flow/i }).click();
    await expect(page).toHaveURL(/\/discover\/session-123$/);
    await expect(page.getByRole("heading", { name: "Sunrise Flow" })).toBeVisible();

    await page.getByRole("button", { name: /Book for R 120\.00/i }).click();
    await expect(page.getByText("Booking confirmed!")).toBeVisible();

    await page.getByRole("button", { name: "Sign out" }).click();
    await expect(page).toHaveURL(/\/login$/);
  });

  test("expires session and returns to login when API and refresh both return 401", async ({
    page,
  }) => {
    await page.route("**/api/v1/**", async (route) => {
      const url = route.request().url();

      if (url.includes("/api/v1/auth/consumer/login")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: "consumer-access-token",
            refresh_token: "consumer-refresh-token",
            token_type: "bearer",
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
    await page.fill('input[name="email"]', "test@studioloop.com");
    await page.fill('input[name="password"]', "testpassword123");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "Sign in to your account" })).toBeVisible();
  });
});
