---
project: studioloop2026
type: decisions
status: parked
stack: FastAPI, SQLModel, PostgreSQL, React 19, Expo, Vite, Tailwind, Turborepo, Stitch, Railway, Vercel
domain: fitness, saas, marketplace
last_analyzed: 2026-03-14
tags: studioloop, decisions, fitness, saas
---

# Decision Log

> Architectural and product decisions inferred from the codebase.

## Tech Stack Choices

**FastAPI + SQLModel** — SQLModel combines Pydantic v2 models with SQLAlchemy ORM, reducing boilerplate for a model-heavy app (30+ models). FastAPI auto-generates OpenAPI spec used for frontend client codegen.

**React 19 + Vite + Turborepo + pnpm** — Modern frontend stack with fast builds. Turborepo caches builds across 5 apps. pnpm workspaces handle shared packages (ui, utils, api-client). Vite for HMR during development.

**Expo 54 for mobile** — Managed React Native with NativeWind (Tailwind for mobile). gym-mobile adds QR scanning (expo-camera). MMKV for token storage (faster than AsyncStorage).

**Stitch over PayFast** — SA-native payment provider with GraphQL API. Supports Pay By Bank and Variable Recurring Payments. PayFast planned as second provider. Svix handles webhook routing and signature verification.

**Railway (JNB region)** — Docker deployment in Johannesburg for POPIA data residency compliance. PostgreSQL co-located in same region.

**Astro 5 for marketing** — Static site generation for landing pages. Separate from the React app bundle. Lightweight, fast-loading.

## Notable Implementation Choices

**GymScopedRepository pattern** — Generic repository with automatic `gym_id` filtering on every query. Makes it impossible to accidentally leak data across tenants. GymScopedSoftDeleteModel adds soft-delete for data preservation.

**Three independent auth systems** — Consumer, Staff, and Admin each have separate JWT flows. Staff tokens include `gym_id` claim for tenant validation. Consumer tokens are platform-scoped. Prevents auth confusion across roles.

**OpenAPI client codegen** — `@hey-api/openapi-ts` generates TypeScript SDK + TanStack Query hooks from FastAPI's OpenAPI spec. Eliminates manual API client maintenance. Single source of truth for API contracts.

**TanStack Query for ALL server state** — Strict rule: never duplicate API data in Zustand. Zustand is only for UI preferences (theme, sidebar state). TanStack Query handles caching, refetching, optimistic updates.

**Waitlist with auto-promotion + expiry** — When a booking is cancelled, next waitlist entry auto-promoted with 24h expiry. If not confirmed, moves to next entry. Prevents phantom holds.

**CSS variable theming** — `data-theme` attribute on root element. Tailwind v4 CSS variable overrides enable dark/light toggle without JavaScript class manipulation.

**Consistent error responses** — `StudioLoopError` base class with typed subclasses (NotFound, Validation, Conflict, PermissionDenied, TenantAccess, BusinessRule). All produce standardized `{ error: { code, message, details } }` JSON.

## Open Questions

1. **Domain** — studioloop.co.za not yet registered. Who handles DNS setup?
2. **Stitch sandbox** — Credentials needed for payment testing. When available?
3. **Pricing tiers** — R499/R999/R1,999 drafted but needs stakeholder approval.
4. **PayFast integration** — When to add as second payment provider?
5. **E2E in CI** — Playwright tests exist but aren't running in GitHub Actions. Worth the CI time?
6. **WebSocket on Vercel** — Real-time updates disabled (no persistent connections). Alternative?
7. **Legacy models** — `models_legacy.py` still contains auth models. When to migrate?
8. **App store submissions** — Timeline for consumer-mobile and gym-mobile?
9. **Luke's role** — Business partner role clarity needed (mentioned in BACKLOG.md).
