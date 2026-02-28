# StudioLoop

Affordable gym management + marketplace platform for South African fitness studios.

## Live Demo

| App | URL | Audience |
|-----|-----|----------|
| **Gym Dashboard** | [sl-gym.vercel.app](https://sl-gym.vercel.app) | Studio owners & staff |
| **Consumer App** | [sl-consumer.vercel.app](https://sl-consumer.vercel.app) | Gym members |
| **Marketing (Gyms)** | [sl-marketing-gyms.vercel.app](https://sl-marketing-gyms.vercel.app) | Gym owner acquisition |
| **Marketing (Consumers)** | [sl-marketing-consumers.vercel.app](https://sl-marketing-consumers.vercel.app) | Member acquisition |
| **Admin** | [sl-admin-eta.vercel.app](https://sl-admin-eta.vercel.app) | Internal |
| **API** | [backend-production-e3cc8.up.railway.app/docs](https://backend-production-e3cc8.up.railway.app/docs) | Developers |

See [docs/demo-walkthrough.md](docs/demo-walkthrough.md) for login credentials and demo script.

## Architecture

```
frontend/
├── apps/
│   ├── consumer-web/          # Member-facing web app (dark/coral theme)
│   ├── consumer-mobile/       # React Native + Expo (member mobile)
│   ├── gym-web/               # Studio dashboard (light/gold theme)
│   ├── gym-mobile/            # React Native + Expo (staff mobile)
│   ├── web/                   # Legacy web app
│   ├── marketing-consumers/   # Astro landing page
│   └── marketing-gyms/        # Astro landing page
├── packages/
│   ├── ui/                    # Shared design system (@sl/ui)
│   └── api-client/            # Generated OpenAPI client
backend/
├── app/
│   ├── api/routes/            # FastAPI endpoints
│   ├── models/                # SQLAlchemy models
│   ├── core/                  # Config, security, OAuth
│   └── seed/                  # Demo data
```

**Stack:** FastAPI · PostgreSQL · SQLAlchemy · Alembic · React · React Native · Expo · Astro · Tailwind v4 · pnpm · Turborepo

## Quick Start

See [CLAUDE.md](CLAUDE.md) for all commands. Key ones:

```bash
# Backend
cd backend && uv sync --dev && uv run uvicorn app.main:app --reload

# Frontend
cd frontend && pnpm install && pnpm dev

# Local services (Postgres + Redis)
docker compose -f docker-compose.local.yml up -d

# Tests
cd backend && uv run pytest -v
cd frontend && pnpm test
```

## Design System

Outfit typeface · Coral (consumer) / Gold (gym) accent scales · Dark & light themes via CSS `data-theme` attribute · Tailwind v4 CSS variable overrides.

See [UX Design Specification](_bmad-output/planning-artifacts/ux-design-specification.md) for full reference.

## Deployment

- **Frontend:** Vercel (auto-deploy via GitHub Actions on push to master)
- **Backend:** Railway (Docker, auto-deploy via GitHub integration)
- **CI:** `.github/workflows/deploy.yml`

## License

Proprietary. All rights reserved.
