---
project: studioloop2026
type: overview
status: active
stack: FastAPI, SQLModel, PostgreSQL, React 19, Expo, Vite, Tailwind, Turborepo, pnpm, Stitch, Railway, Vercel
domain: fitness, saas, marketplace
last_analyzed: 2026-03-14
tags: studioloop, fitness, saas, marketplace, south-africa, multi-tenant, payments
---

# StudioLoop 2026
> Multi-tenant SaaS platform for South African fitness studio management — class scheduling, bookings, payments, marketplace, and mobile check-in.

## What This Is
StudioLoop is a production-ready fitness studio management platform targeting independent SA gyms and boutique studios. It's a full-stack multi-tenant SaaS with a FastAPI backend (30+ SQLModel domain models, 17 route modules, 80+ endpoints), a pnpm/Turborepo frontend monorepo (5 web/mobile apps), and live deployments on Railway (backend, JNB region) and Vercel (frontend).

The platform covers the complete studio lifecycle: gym onboarding, staff management with RBAC (owner/manager/front_desk/instructor), membership plans (R299/R499/R699), class scheduling with approval workflows, booking with waitlists, QR check-in (mobile), Stitch payment integration (Pay By Bank, VRP), marketplace for cross-gym class discovery, analytics dashboards, and multi-channel notifications (email, SMS, in-app, WhatsApp).

15 epics completed across 124 commits. Currently in March 2026 launch execution phase, targeting 3-5 pilot studios in Cape Town.

## Problem It Solves
Independent SA fitness studios manage bookings, payments, and member communication across disconnected tools (spreadsheets, WhatsApp groups, manual payment tracking). StudioLoop consolidates everything into a single platform with proper multi-tenancy, automated payments via local providers (Stitch), and a marketplace for consumers to discover classes across studios.

## Target User
- **Gym owners**: Independent studios and boutique fitness businesses in SA
- **Staff**: Instructors, front desk, managers
- **Consumers**: Fitness enthusiasts discovering and booking classes
- **Initial market**: Cape Town independent gyms

## Current Status
**Active / Near launch** — 85-90% ready for March 2026 launch. All 15 epics complete. Live production deployments running. Blocking items: domain registration (studioloop.co.za), Stitch sandbox credentials, pilot studio identification, pricing finalization.

## Key Links & Entry Points

| Item | Path/URL |
|------|----------|
| Backend Entry | `backend/app/main.py` |
| API Docs | https://backend-production-e3cc8.up.railway.app/docs |
| Gym Web Portal | https://sl-gym.vercel.app |
| Consumer Web | https://sl-consumer.vercel.app |
| Marketing (Gyms) | https://sl-marketing-gyms.vercel.app |
| Marketing (Consumers) | https://sl-marketing-consumers.vercel.app |
| Domain Models | `backend/app/models/` (30+ models) |
| API Routes | `backend/app/api/routes/` (17 modules) |
| Frontend Monorepo | `frontend/` (pnpm + Turborepo) |
| Mobile Apps | `frontend/apps/consumer-mobile/`, `frontend/apps/gym-mobile/` |
| CLAUDE.md | `CLAUDE.md` |
| Demo Guide | `docs/demo-walkthrough.md` |
| Pricing | `docs/launch-pricing-ops-march-2026.md` |
| BACKLOG | `BACKLOG.md` |
