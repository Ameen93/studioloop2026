# Changelog

## 2026-02-28 — Unified Design System + Live Deployment

### Added
- **Complete UX overhaul** — Outfit typeface, coral/gold accent palette, dark/light themes across all 5 frontend apps
- **9 new shared UI components**: MetricCard, ClassCard, FilterChips, PriceBadge, StickyBottomCTA, SearchInput, SkeletonLoader, ActionItemCard, StatusFlash
- **4 updated primitives** with semantic tokens: Button, Card, Input, Modal
- **CSS theme system** via `data-theme` attribute with Tailwind v4 CSS var overrides
- **OAuth staff login** — Google/Apple ID support with migration for `google_id`/`apple_id` on Staff model
- **GitHub Actions deploy workflow** — auto-deploys all frontend apps to Vercel on push to master
- **EAS config** for both mobile apps (consumer + gym)
- **Demo walkthrough doc** with live URLs and login credentials
- **Pitch one-pager** for gym owner outreach
- **UX design specification** (2,068 lines) — comprehensive design system reference
- `.railwayignore` for clean backend deploys

### Changed
- Consumer-web: dark theme with coral accents
- Gym-web: light theme with gold accents
- Both mobile apps: dark backgrounds, updated tab bars
- Accent replacement: indigo→coral (consumer), blue→gold (gym), emerald→gold (gym-mobile)
- OpenAPI client regenerated with full schema (2,763+ lines)
- Cleaned `.gitignore`, removed tracked `dist/` directories

### Live URLs

> Historical record. These deployments are retired: the Railway backend no longer
> exists (404), so any frontend still resolving has no working API behind it.

- Gym Web: https://sl-gym.vercel.app
- Consumer Web: https://sl-consumer.vercel.app
- Marketing (Gyms): https://sl-marketing-gyms.vercel.app
- Marketing (Consumers): https://sl-marketing-consumers.vercel.app
- Admin: https://sl-admin-eta.vercel.app
- Backend API: https://backend-production-e3cc8.up.railway.app
- API Docs: https://backend-production-e3cc8.up.railway.app/docs

## 2026-02-27 — Railway Deploy + Stitch Payments

### Added
- Stitch payments API routes and tests
- Stitch sandbox webhook callback verification
- Railway deployment config (Dockerfile, railway.toml, healthchecks)

### Fixed
- Docker build (python:3.12-slim, build deps, cache mounts)
- Healthcheck timeout increased to 300s
- Migration-on-start for Railway

## 2026-02-26 — Epic 5 Merge

### Added
- Epic 5: Class Scheduling — models, routes, tests, calendar UI (stories 5-1..5-11)

### Fixed
- Stabilized merge — resolved class scheduling and account deletion regressions
- Staff performance report test fix
- Unique email per test run to prevent duplicate key errors
