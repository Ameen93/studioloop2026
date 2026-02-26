# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service, DB models, API routes, migrations, and pytest suite.
  - App code: `backend/app/` (`api/routes`, `models`, `repositories`, `schemas`, `services`)
  - Tests: `backend/tests/`
- `frontend/`: pnpm + Turborepo workspace.
  - Apps: `frontend/apps/web`, `frontend/apps/consumer-mobile`, `frontend/apps/gym-mobile`
  - Shared packages: `frontend/packages/api-client`, `frontend/packages/ui`, `frontend/packages/utils`
  - E2E: `frontend/e2e/` (Playwright)
- Planning and delivery artifacts: `_bmad-output/` (PRD, architecture, story status).

## Build, Test, and Development Commands
- Backend setup: `cd backend && uv sync --dev`
- Run backend locally: `cd backend && uv run uvicorn app.main:app --reload`
- Backend tests: `cd backend && uv run pytest -v`
- Backend quality: `cd backend && uv run ruff check app/ && uv run mypy app/`
- Frontend setup: `cd frontend && pnpm install`
- Run all frontend apps/tasks: `cd frontend && pnpm dev`
- Frontend checks: `cd frontend && pnpm lint && pnpm type-check && pnpm test`
- E2E tests: `cd frontend && pnpm test:e2e` (see `frontend/e2e/README.md` for seed/setup)

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints required, async-first in FastAPI routes.
- TypeScript: strict mode; `camelCase` for vars/functions, `PascalCase` for components/types.
- API/database naming is strict `snake_case` (routes, JSON fields, table/column names).
- Use UUIDs for primary keys; enforce tenant scoping with `gym_id` on gym-scoped queries.
- Format/lint before PR: Ruff + MyPy (backend), workspace lint/type-check (frontend).

## Testing Guidelines
- Backend: `pytest` with tests in `backend/tests/**`, add/update tests with every behavior change.
- Frontend/unit: workspace `pnpm test`.
- E2E: Playwright in `frontend/e2e/*.spec.ts`; prefer stable selectors (`data-testid`).
- Minimum expectation: changed code paths covered by tests; no failing CI jobs.

## Commit & Pull Request Guidelines
- Follow Conventional Commit style seen in history:
  - `feat(epic-2): implement story 2.5 cancellation policy configuration`
  - `fix(auth): validate Apple token sub claim`
- Keep commits focused to one story/change.
- PRs should include: summary, linked story/issue, test evidence (commands run), and UI screenshots for visual changes.
- Ensure CI passes (`.github/workflows/ci.yml`) before requesting review.

## Security & Configuration Tips
- Do not commit secrets; use local `.env` files.
- Respect multi-tenancy boundaries and role-based access checks on every gym-scoped endpoint.
