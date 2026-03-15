---
project: studioloop2026
type: kb-entry
status: active
stack: FastAPI, SQLModel, PostgreSQL, React 19, Expo, Vite, Tailwind, Turborepo, Stitch, Railway, Vercel
domain: fitness, saas, marketplace
last_analyzed: 2026-03-14
tags: studioloop, fitness, saas, marketplace, south-africa
---

# Knowledge Base Entry — StudioLoop 2026

> Canonical single-file reference for cross-project knowledge base.

## Tags
fitness, saas, marketplace, multi-tenant, south-africa, fastapi, react, expo, payments, active

## Summary
StudioLoop is a production-deployed multi-tenant fitness studio SaaS for independent SA gyms. 15 epics complete covering auth, gym onboarding, staff RBAC, memberships, class scheduling, bookings with waitlists, marketplace for cross-gym discovery, Stitch payments, notifications, analytics, and admin. FastAPI backend (30+ models, 80+ endpoints) + Turborepo frontend (5 React/Expo apps). Live on Railway (JNB) + Vercel. 124 commits. March 2026 launch targeting Cape Town pilot studios. Pricing R499–R1,999/mo.

## Relationships to Other Projects

| Project | Relationship |
|---------|-------------|
| `mcp-servers-za` | Stitch payment server could complement StudioLoop's Stitch integration |
| `dealerOS` | Both are multi-tenant SaaS with similar architectural patterns |
| `carsearch` | Same DealersOnline ecosystem (work projects) |

## Reusable Patterns

1. **GymScopedRepository** — Generic CRUD with automatic tenant_id filtering. Reusable for any multi-tenant FastAPI app.
2. **Three-system auth** — Separate JWT flows for different user types (consumer, staff, admin). Each with role-specific claims.
3. **OpenAPI client codegen** — @hey-api generates TypeScript SDK + TanStack Query hooks from FastAPI spec. Zero-maintenance API client.
4. **Consistent error hierarchy** — Typed exception classes → standardized JSON response. Reusable error handling pattern.
5. **Waitlist auto-promotion** — Queue with expiry timer. When slot opens, auto-promote next entry with configurable timeout.
6. **CSS variable theming** — `data-theme` attribute + Tailwind v4 CSS vars for dark/light toggle. No JS class manipulation.
7. **Turborepo + pnpm workspace** — Multiple apps sharing UI components, utils, and API client. Cached builds.
8. **BMAD epic tracking** — Sprint status YAML with story-level progress. Good for complex multi-epic projects.

## Lessons & Insights

- **GymScopedRepository prevents tenant leaks** — Automatic `gym_id` filtering at the ORM level is more reliable than manual filtering in every route handler.
- **OpenAPI codegen is a force multiplier** — Auto-generating typed API clients from the backend spec eliminates a whole class of frontend/backend contract bugs.
- **TanStack Query > Zustand for server state** — Strict separation prevents data duplication and stale state. Server data in TanStack Query, UI state in Zustand.
- **Railway JNB for POPIA** — Hosting in Johannesburg satisfies SA data residency requirements with minimal latency for SA users.
- **Soft-delete + audit logging** — Required for POPIA compliance. Worth building in from the start rather than retrofitting.
- **15 epics is a lot** — Comprehensive feature set but also means more surface area to test and maintain. Pilot early to validate which features matter most.
