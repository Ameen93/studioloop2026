import { expect, test, type Page } from "@playwright/test";

async function mockAuthAndBaseData(page: Page): Promise<void> {
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
        total_classes_this_month: 3,
        current_streak_weeks: 1,
      }),
    });
  });

  await page.route("**/api/v1/analytics/me/class-history", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [] }),
    });
  });

  await page.route("**/api/v1/gyms/consumer/qr_code", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        todays_booking_ids: [],
        qr_token: "qr-token",
        expires_at: "2026-02-19T23:59:59Z",
      }),
    });
  });

  await page.route("**/api/v1/payments/me/history", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [] }),
    });
  });
}

async function loginConsumer(page: Page): Promise<void> {
  await page.goto("/login");
  await page.fill('input[name="email"]', "test@studioloop.com");
  await page.fill('input[name="password"]', "testpassword123");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/$/);
}

test.describe("Consumer Profile", () => {
  test("updates profile successfully", async ({ page }) => {
    await mockAuthAndBaseData(page);

    let currentProfile = {
      id: "consumer-123",
      email: "test@studioloop.com",
      first_name: "Test",
      last_name: "User",
      phone: "+27110000000",
      avatar_url: null,
    };

    await page.route("**/api/v1/auth/consumer/me", async (route) => {
      const method = route.request().method();
      if (method === "GET") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(currentProfile),
        });
        return;
      }

      if (method === "PATCH") {
        const payload = route.request().postDataJSON() as {
          first_name: string;
          last_name: string;
          phone: string | null;
        };
        currentProfile = {
          ...currentProfile,
          first_name: payload.first_name,
          last_name: payload.last_name,
          phone: payload.phone,
        };
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(currentProfile),
        });
        return;
      }

      await route.fulfill({ status: 200, body: JSON.stringify({ message: "ok" }) });
    });

    await loginConsumer(page);
    await page.getByRole("link", { name: "Profile" }).click();
    await expect(page).toHaveURL(/\/profile$/);
    await expect(page.getByRole("heading", { name: "Profile & Settings" })).toBeVisible();

    await page.fill('input[name="firstName"]', "Updated");
    await page.fill('input[name="lastName"]', "Member");
    await page.fill('input[name="phone"]', "+27821112222");
    await page.getByRole("button", { name: "Save changes" }).click();

    await expect(page.getByRole("button", { name: "Saved!" })).toBeVisible();
  });

  test("deletes account successfully and redirects to login", async ({ page }) => {
    await mockAuthAndBaseData(page);

    await page.route("**/api/v1/auth/consumer/me", async (route) => {
      const method = route.request().method();
      if (method === "GET") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "consumer-123",
            email: "test@studioloop.com",
            first_name: "Test",
            last_name: "User",
            phone: "+27110000000",
            avatar_url: null,
          }),
        });
        return;
      }

      if (method === "DELETE") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ message: "deleted" }),
        });
        return;
      }

      await route.fulfill({ status: 200, body: JSON.stringify({ message: "ok" }) });
    });

    await loginConsumer(page);
    await page.getByRole("link", { name: "Profile" }).click();
    await page.getByRole("button", { name: "Account" }).click();
    await page.getByRole("button", { name: "Delete my account" }).click();
    await page.getByRole("button", { name: "Yes, delete my account" }).click();

    await expect(page).toHaveURL(/\/login$/);
  });

  test("shows error messages when update and delete fail", async ({ page }) => {
    await mockAuthAndBaseData(page);

    await page.route("**/api/v1/auth/consumer/me", async (route) => {
      const method = route.request().method();
      if (method === "GET") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "consumer-123",
            email: "test@studioloop.com",
            first_name: "Test",
            last_name: "User",
            phone: "+27110000000",
            avatar_url: null,
          }),
        });
        return;
      }

      if (method === "PATCH") {
        await route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({
            detail: { code: "INVALID_PHONE_FORMAT", message: "Bad phone format" },
          }),
        });
        return;
      }

      if (method === "DELETE") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            detail: { code: "INTERNAL_ERROR", message: "Unexpected failure" },
          }),
        });
        return;
      }

      await route.fulfill({ status: 200, body: JSON.stringify({ message: "ok" }) });
    });

    await loginConsumer(page);
    await page.getByRole("link", { name: "Profile" }).click();

    await page.getByRole("button", { name: "Save changes" }).click();
    await expect(page.getByText("Could not save profile changes. Please try again.")).toBeVisible();

    await page.getByRole("button", { name: "Account" }).click();
    await page.getByRole("button", { name: "Delete my account" }).click();
    await page.getByRole("button", { name: "Yes, delete my account" }).click();
    await expect(page.getByText("Could not delete your account. Please try again.")).toBeVisible();
    await expect(page).toHaveURL(/\/profile$/);
  });
});
