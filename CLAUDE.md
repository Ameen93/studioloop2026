# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StudioLoop is a multi-tenant SaaS platform for fitness studio management in South Africa. It has a FastAPI backend, a React web dashboard, and two React Native mobile apps (consumer + gym staff), all in a monorepo.

## Commands

### Backend (from `backend/`)
```bash
uv sync --dev                              # Install dependencies
uv run uvicorn app.main:app --reload       # Run dev server
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
pnpm dev                  # Run all apps in dev mode
pnpm lint                 # Lint all packages (Turbo)
pnpm type-check           # Type check all packages
pnpm test                 # Unit tests
pnpm test:e2e             # Playwright E2E
pnpm generate:api         # Regenerate OpenAPI client from backend spec
```

### Local Services
```bash
docker compose -f docker-compose.local.yml up -d    # Postgres 17 + Redis 7 + Adminer
docker compose -f docker-compose.local.yml down
# Postgres: localhost:5432, Redis: localhost:6379, Adminer: localhost:8080
```

## Architecture

### Backend (`backend/app/`)

- **Framework:** FastAPI + SQLModel (Pydantic v2 + SQLAlchemy) + PostgreSQL 17
- **Package manager:** `uv` (not pip/poetry)
- **API prefix:** `/api/v1`

**Model hierarchy:**
```
BaseModel (UUID PK + created_at/updated_at)
├── GymScopedModel (+ gym_id FK)
│   └── GymScopedSoftDeleteModel (+ is_active, deleted_at)
```

**Repository pattern:** `BaseRepository[Model, Create, Update]` for platform-scoped entities, `GymScopedRepository[M, C, U]` for gym-scoped (auto-filters by `gym_id`).

**Schema pattern:** Each domain defines `XBase` → `X` (table model) → `XCreate` / `XUpdate` / `XPublic` in the same model file.

**Three independent auth flows** with separate FastAPI deps:
- `CurrentUser` — legacy admin/superuser
- `CurrentConsumer` — consumer JWT (mobile app)
- `CurrentStaff` — staff JWT (gym employees)

**RBAC:** `RoleChecker` with hierarchy `owner > manager > front_desk = instructor`. Convenience deps: `RequireOwner`, `RequireOwnerOrManager`, `RequireStaff`.

**Error format:** All errors return `{ "error": { "code": "ERROR_CODE", "message": "...", "details": {} } }` via custom exception classes in `core/exceptions.py`.

### Frontend (`frontend/`)

- **Monorepo:** pnpm + Turborepo
- **Apps:** `apps/web` (React 19 + Vite + React Router v7 + Tailwind v4), `apps/consumer-mobile` (Expo 54 + NativeWind v4), `apps/gym-mobile` (Expo 54 + NativeWind v4)
- **Shared packages:** `packages/api-client` (hey-api OpenAPI codegen + TanStack Query v5), `packages/ui`, `packages/utils`

### Multi-Tenancy (Critical)

`Gym` is the tenant root. All gym data is isolated by `gym_id`. Consumer profiles are platform-scoped (shared). Every gym-scoped query MUST filter by `gym_id` — use `GymScopedRepository` which enforces this automatically.

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
- Payments: Ozow (primary), PayFast (secondary)
- Phone validation: SA format (+27...)
- Currency: ZAR (R 1,234.56)
- Date display: `DD MMM YYYY, HH:mm`
- Notifications: WhatsApp Business API preferred

## Testing

- **Backend:** pytest with real database. Session-scoped fixtures seed data via `seed_all()`. Tests mirror app structure in `backend/tests/`.
- **Frontend unit:** Vitest + RTL (web), Jest + jest-expo + RNTL (mobile)
- **E2E:** Playwright in `frontend/e2e/`

## Commit Style

Conventional commits matching repo history:
```
feat(epic-2): implement story 2.5 cancellation policy configuration
fix(auth): validate Apple token sub claim
```

## Project Planning

BMAD artifacts live in `_bmad-output/`. Current implementation status is tracked in `_bmad-output/implementation-artifacts/sprint-status.yaml`. Story specs are in `_bmad-output/implementation-artifacts/{story-id}-{name}.md`.
