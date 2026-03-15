---
project: studioloop2026
type: ai-context
status: active
stack: FastAPI, SQLModel, PostgreSQL, React 19, Expo, Vite, Tailwind, Turborepo, Stitch, Railway, Vercel
domain: fitness, saas, marketplace
last_analyzed: 2026-03-14
tags: studioloop, fitness, saas, marketplace, south-africa
---

# AI Context File — StudioLoop 2026

> This file is optimized for loading into an AI assistant to provide full project context.

## Project Identity
- **Name**: StudioLoop 2026
- **Domain**: Fitness studio management SaaS + marketplace
- **Status**: Active (near launch, 85-90% ready)
- **Stack**: FastAPI, SQLModel, PostgreSQL, React 19, Expo 54, Vite, Tailwind CSS 4, Turborepo, pnpm, Stitch, Railway (JNB), Vercel
- **Location**: `/home/ameen/projects/studioloop2026/`

## One-Paragraph Summary
StudioLoop is a production-deployed multi-tenant fitness studio SaaS targeting independent SA gyms. FastAPI backend with 30+ SQLModel models, 17 route modules (80+ endpoints), GymScopedRepository pattern for tenant isolation, Stitch payment integration, and 4-tier RBAC. Frontend monorepo (Turborepo + pnpm) with 5 apps: gym-web, consumer-web (React 19 + Vite), consumer-mobile, gym-mobile (Expo 54 + QR scanning), and 2 Astro marketing sites. 15 epics complete (auth, gyms, staff, memberships, classes, bookings, marketplace, payments, notifications, analytics, admin). Live on Railway (JNB) + Vercel. 124 commits. March 2026 launch targeting 3-5 Cape Town pilot studios. Pricing: R499/R999/R1,999/mo.

## Key Concepts & Terminology
- **Gym** — Tenant root entity; all gym-scoped data isolated by `gym_id`
- **GymScopedRepository** — Generic CRUD repository auto-filtering by `gym_id`
- **Staff Role** — owner > manager > front_desk > instructor (4-tier RBAC)
- **ClassTemplate** — Recurring schedule definition; ClassSession is a specific instance
- **Waitlist auto-promotion** — Cancelled booking triggers next waitlist entry with 24h expiry
- **Marketplace** — Cross-gym class discovery; requires MarketplaceSubscription
- **Stitch** — SA fintech for Pay By Bank and VRP (Variable Recurring Payments)
- **Svix** — Webhook routing + signature verification service

## Architecture in Brief
Multi-tenant FastAPI backend with SQLModel ORM, GymScopedRepository for tenant isolation, JWT auth (3 systems: consumer, staff, admin), and Stitch payment integration. Frontend Turborepo monorepo with 5 React/Expo apps and auto-generated TypeScript API client from OpenAPI spec. Deployed on Railway (backend+DB, JNB) and Vercel (frontend, CDN). CI/CD via GitHub Actions.

## Current Sprint / Focus
March 2026 launch execution: domain registration, pilot studio identification (3-5 in Cape Town), pricing finalization, Stitch sandbox credential setup, production hardening.

## Important Constraints
- Multi-tenant: ALL gym-scoped queries MUST filter by `gym_id`
- Staff JWT tokens include `gym_id` claim; mismatches = 403
- TanStack Query for ALL server state; Zustand ONLY for UI preferences
- POPIA compliance: soft-delete, audit logs, JNB data residency
- ZAR currency, 15% VAT on receipts
- Operating hours enforcement for class scheduling
- Waitlist auto-promotion with 24h expiry timer

## File Map (Key Files Only)

| Path | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI entry with lifespan |
| `backend/app/models/` | 30+ SQLModel domain models |
| `backend/app/api/routes/` | 17 route modules (80+ endpoints) |
| `backend/app/repositories/` | Generic CRUD + GymScopedRepository |
| `backend/app/services/` | Payment + notification business logic |
| `backend/app/core/` | Config, security, exceptions, OAuth |
| `backend/app/alembic/` | 30+ database migrations |
| `backend/tests/` | 32 integration test files |
| `frontend/apps/gym-web/` | Staff/owner portal (React 19 + Vite) |
| `frontend/apps/consumer-web/` | Member portal |
| `frontend/apps/consumer-mobile/` | Expo 54 consumer app |
| `frontend/apps/gym-mobile/` | Expo 54 staff app (QR scanning) |
| `frontend/packages/api-client/` | @hey-api OpenAPI codegen |
| `frontend/packages/ui/` | 19 shared components |
| `CLAUDE.md` | Detailed project guidance |
| `docs/demo-walkthrough.md` | 20-min sales demo script |
| `BACKLOG.md` | Current blockers + roadmap |
