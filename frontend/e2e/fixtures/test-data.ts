/**
 * Test data constants for E2E tests.
 *
 * These values should match the seed data created by:
 *   cd backend && uv run python scripts/seed.py --reset
 */

export const TEST_USER = {
  email: "test@studioloop.com",
  password: "testpassword123",
  fullName: "Test User",
} as const;

export const TEST_GYMS = {
  fitzonesSandton: {
    name: "FitZone Sandton",
    slug: "fitzone-sandton",
    city: "Johannesburg",
  },
  oxygenCapeTown: {
    name: "Oxygen Fitness Cape Town",
    slug: "oxygen-cape-town",
    city: "Cape Town",
  },
} as const;

/**
 * API endpoints for E2E testing.
 * Backend runs on port 8000 by default.
 */
export const API = {
  baseUrl: process.env.API_BASE_URL || "http://localhost:8000",
  auth: {
    login: "/api/v1/auth/login",
    register: "/api/v1/auth/register",
    me: "/api/v1/auth/me",
  },
} as const;
