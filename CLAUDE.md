# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StudioLoop is a multi-tenant SaaS platform for fitness studio management in South Africa. It has a FastAPI backend, three React web apps, two React Native mobile apps, and two Astro marketing sites — all in a pnpm + Turborepo monorepo.

## Commands

### Backend (from `backend/`)
```bash
uv sync --dev                              # Install dependencies
uv run uvicorn app.main:app --reload       # Run dev server (port 8000)
uv run pytest -v                           # Run all tests
uv run pytest tests/api/routes/test_gyms.py -v                # Single test file
uv run pytest tests/api/routes/test_gyms.py::test_name -v     # Single test
uv run ruff check app/ && uv run ruff format app/             # Lint + format
uv run mypy app/                           # Type check
uv run alembic upgrade head                # Run migrations
uv run alembic revision --autogenerate -m "description"        # Create migration
uv run python scripts/seed.py              # Seed dev data
```

### Frontend (from `frontend/`)
```bash
pnpm install              # Install deps
pnpm dev                  # Run all apps in dev mode (Turbo)
pnpm lint                 # Lint all packages (Turbo)
pnpm type-check           # Type check all packages
pnpm test                 # Unit tests (Vitest for web, Jest for mobile)
pnpm generate:api         # Regenerate OpenAPI client from backend spec
pnpm test:e2e             # Playwright E2E (headless)
pnpm test:e2e:headed      # Playwright E2E (visible browser)
pnpm test:e2e:ui          # Playwright interactive UI mode
```

### Local Services
```bash
docker compose -f docker-compose.local.yml up -d    # Postgres 17 + Redis 7 + Adminer
docker compose -f docker-compose.local.yml down
# Postgres: localhost:5432, Redis: localhost:6379, Adminer: localhost:8080
```

### First-Time Local Setup
```bash
docker compose -f docker-compose.local.yml up -d
cd backend && uv sync --dev && uv run alembic upgrade head && uv run python scripts/seed.py
```

## Architecture

### Backend (`backend/app/`)

- **Framework:** FastAPI + SQLModel (Pydantic v2 + SQLAlchemy) + PostgreSQL 17
- **Package manager:** `uv` (not pip/poetry). Python 3.12 (pinned via `mise.toml`).
- **API prefix:** `/api/v1`
- **Security:** Argon2 passwords (via `pwdlib`), bcrypt fallback for legacy hashes. JWT HS256 (access: 24h, refresh: 7d). OAuth2 via Google and Apple Sign-In.

**Key directories:**
- `core/` — config (Pydantic BaseSettings from `.env`), db engine, security, exceptions
- `models/` — SQLModel domain models, all re-exported from `models/__init__.py`
- `repositories/` — generic data access (`BaseRepository`, `GymScopedRepository`)
- `services/` — business logic (payments/Stitch, notifications)
- `api/routes/` — 17 route modules aggregated in `api/main.py`
- `seed/` — dev/test data seeding orchestrated by `seed/orchestrator.py`
- `alembic/` — database migrations (30+ versions)

**Model hierarchy:**
```
BaseModel (UUID PK + created_at/updated_at)
├── GymScopedModel (+ gym_id FK)
│   └── GymScopedSoftDeleteModel (+ is_active, deleted_at)
```

Table names auto-generated from class name: `ClassSession` → `class_sessions`.

**Repository pattern:** `BaseRepository[Model, Create, Update]` for platform-scoped entities, `GymScopedRepository[M, C, U]` for gym-scoped (auto-filters by `gym_id`). Soft-delete models exclude inactive records by default.

**Schema pattern:** Each domain defines `XBase` → `X` (table model) → `XCreate` / `XUpdate` / `XPublic` in the same model file.

**Three independent auth flows** with separate FastAPI deps:
- `CurrentUser` — legacy admin/superuser
- `CurrentConsumer` — consumer JWT (mobile app)
- `CurrentStaff` — staff JWT (gym employees, includes `gym_id` claim)

Additional deps: `GymDep` (validates gym_id path param + staff access), `StaffGymDep` (staff with gym_id check).

**RBAC:** `RoleChecker` with hierarchy `owner > manager > front_desk = instructor`. Convenience deps: `RequireOwner`, `RequireOwnerOrManager`, `RequireStaff`.

**Error format:** All errors return `{ "error": { "code": "ERROR_CODE", "message": "...", "details": {} } }` via custom exception classes in `core/exceptions.py`. Exception hierarchy: `StudioLoopError` → `NotFoundError` (404), `ValidationError` (422), `ConflictError` (409), `PermissionDeniedError`/`TenantAccessError` (403), `BusinessRuleError` (400).

### Frontend (`frontend/`)

- **Monorepo:** pnpm 10 + Turborepo
- **Web apps:**
  - `apps/web` — Admin dashboard (React 19 + Vite + React Router v7 + Tailwind v4, port 5173)
  - `apps/consumer-web` — Consumer portal (same stack, port 5175)
  - `apps/gym-web` — Gym staff portal (same stack, port 5174)
- **Mobile apps:**
  - `apps/consumer-mobile` — Consumer app (Expo 54 + Expo Router + NativeWind v4)
  - `apps/gym-mobile` — Gym staff app (same stack, adds expo-camera for QR scanning)
- **Marketing sites:** `apps/marketing-consumers`, `apps/marketing-gyms` (Astro 5)
- **Shared packages:** `packages/api-client` (hey-api OpenAPI codegen + TanStack Query v5), `packages/ui` (Button, Input, Card, Modal + Tailwind preset), `packages/utils`

**API client generation flow:**
1. `scripts/export-openapi.sh` exports FastAPI's OpenAPI spec to `packages/api-client/openapi.json`
2. `@hey-api/openapi-ts` generates typed SDK + TanStack Query hooks in `src/generated/`
3. Apps import from `@sl/api-client` — never write manual fetch calls

**Auth per platform:**
- Web apps: tokens in `localStorage`, 401 interceptor with automatic refresh
- Mobile apps: tokens in MMKV (`react-native-mmkv`), session expiry event emitter

**Vite proxy:** All web apps proxy `/api` to backend (configurable via `VITE_API_PROXY_TARGET`).

### Multi-Tenancy (Critical)

`Gym` is the tenant root. All gym data is isolated by `gym_id`. Consumer profiles are platform-scoped (shared). Every gym-scoped query MUST filter by `gym_id` — use `GymScopedRepository` which enforces this automatically. Staff JWT tokens include `gym_id`; mismatches raise 403.

## Naming Conventions (Strict)

- **API endpoints & JSON fields:** `snake_case` — `/class_sessions`, `{ "gym_id": "..." }`
- **Database tables:** `snake_case` plural — `class_sessions`, `membership_plans`
- **Database columns:** `snake_case` — `created_at`, `gym_id`
- **Primary keys:** UUIDs everywhere (never auto-increment)
- **TypeScript:** `camelCase` vars/functions, `PascalCase` components/types, `SCREAMING_SNAKE` constants
- **Python:** 4-space indent, type hints required, async-first routes

## State Management (Frontend)

- **TanStack Query v5:** ALL server/API state — never duplicate in Zustand
- **Zustand:** ONLY client-side state (UI preferences, local flags)
- **Mobile storage:** MMKV for key-value (not AsyncStorage), Expo SQLite for offline queues

## SA-Specific Rules

- POPIA compliance: all user data must be deletable, consent tracked
- Production hosting: Fly.io Johannesburg (`jnb`) for data residency
- Payments: Stitch (primary, via Svix webhooks), Ozow, PayFast
- Phone validation: SA format (+27...)
- Currency: ZAR (R 1,234.56)
- Date display: `DD MMM YYYY, HH:mm`
- Notifications: WhatsApp Business API preferred

## Testing

- **Backend:** pytest with real database. Session-scoped fixtures run `alembic upgrade head` then seed data via `seed_all()`. Tests mirror app structure in `backend/tests/`. 25+ integration test files in `tests/api/routes/`.
- **Frontend unit:** Vitest + RTL (web apps), Jest + jest-expo + RNTL (mobile apps)
- **E2E:** Playwright in `frontend/e2e/` with three projects: `web-chromium` (5173), `consumer-web-chromium` (5175), `gym-web-chromium` (5174). **Prerequisite:** backend must be running and seeded. Test data fixtures in `e2e/fixtures/test-data.ts`.

## Environment

The `.env` file lives at the repo root (parent of `backend/`). Key variables:
- `DATABASE_URL` or individual `POSTGRES_*` vars
- `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`
- `ENVIRONMENT` (`local`|`staging`|`production`) — gates dev-only routes and Sentry
- OAuth: `GOOGLE_CLIENT_ID`/`SECRET`, `APPLE_CLIENT_ID`/`TEAM_ID`/`KEY_ID`/`PRIVATE_KEY`
- Payments: `STITCH_CLIENT_ID`/`SECRET`/`WEBHOOK_SECRET`
- Frontend: `VITE_API_BASE_URL`, mobile: `EXPO_PUBLIC_API_BASE_URL`

## Commit Style

Conventional commits matching repo history:
```
feat(epic-2): implement story 2.5 cancellation policy configuration
fix(auth): validate Apple token sub claim
```

## Project Planning

BMAD artifacts live in `_bmad-output/`. Current implementation status is tracked in `_bmad-output/implementation-artifacts/sprint-status.yaml`. Story specs are in `_bmad-output/implementation-artifacts/{story-id}-{name}.md`.
