---
project: studioloop2026
type: architecture
status: parked
stack: FastAPI, SQLModel, PostgreSQL, React 19, Expo, Vite, Tailwind, Turborepo, pnpm, Stitch, Railway, Vercel
domain: fitness, saas, marketplace
last_analyzed: 2026-03-14
tags: studioloop, architecture, multi-tenant, fastapi, react, expo
---

# Architecture

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI 0.114+ | Async REST API |
| ORM | SQLModel 0.0.21 | Pydantic v2 + SQLAlchemy models |
| Database | PostgreSQL 17 | Multi-tenant data (Railway, JNB region) |
| Auth | JWT HS256 (pyjwt) | Access: 24h, Refresh: 7d |
| OAuth | Google + Apple Sign-In (authlib) | Social login |
| Passwords | Argon2 + bcrypt fallback (pwdlib) | Secure hashing |
| Payments | Stitch (GraphQL) | Pay By Bank, VRP |
| Webhooks | Svix | Payment webhook routing + signing |
| Email | SMTP + Jinja2 | Transactional emails |
| Migrations | Alembic | 26 migration versions, linear chain |
| Monitoring | Sentry | Error tracking (non-local) |
| Testing (Backend) | pytest | 34 test files, 460 tests |
| Build System | Turborepo 2.7 | Monorepo build orchestration |
| Package Mgr | pnpm 10.28 | Frontend dependency management |
| Web Framework | React 19.1 | Staff + consumer portals |
| Bundler | Vite 7.2 | Fast builds + HMR |
| Styling | Tailwind CSS 4 | Utility-first CSS |
| Server State | TanStack Query 5 | API data management |
| Client State | Zustand | UI preferences only |
| Mobile | Expo 54 + React Native | Consumer + staff mobile apps |
| Mobile Storage | MMKV | Key-value (not AsyncStorage) |
| Marketing | Astro 5 | Static sites |
| API Client Gen | @hey-api/openapi-ts | Typed SDK from OpenAPI |
| E2E Testing | Playwright 1.57 | Browser automation |
| Frontend Deploy | Vercel | Global CDN |
| Backend Deploy | Railway (JNB) | Docker, SA data residency |

## System Diagram

```
┌─────────────────────────────────────────────────┐
│                   Consumers                      │
│  consumer-web (Vercel) │ consumer-mobile (Expo)  │
└──────────────────┬──────────────────────────────┘
                   │
┌─────────────────────────────────────────────────┐
│                 Gym Staff                        │
│    gym-web (Vercel)  │  gym-mobile (Expo+QR)    │
└──────────────────┬──────────────────────────────┘
                   │
          ┌────────┴────────┐
          │ @hey-api client │ (auto-generated from OpenAPI)
          └────────┬────────┘
                   │
┌─────────────────────────────────────────────────┐
│            FastAPI Backend (Railway JNB)          │
│                                                  │
│  Auth: JWT + Google/Apple OAuth                  │
│  RBAC: owner > manager > front_desk/instructor   │
│                                                  │
│  17 Route Modules:                               │
│  login, consumers, gyms, staff_auth,             │
│  staff_memberships, class_scheduling,            │
│  bookings, marketplace, payments, webhooks,      │
│  notifications, analytics, admin, realtime...    │
│                                                  │
│  Repository Pattern:                             │
│  GymScopedRepository (auto gym_id filtering)     │
│                                                  │
│  Services: payments, notifications               │
└──────────────────┬──────────────────────────────┘
                   │
     ┌─────────────┼──────────────┐
     ▼             ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│PostgreSQL│ │  Stitch  │ │   SMTP   │
│  (JNB)   │ │ Payments │ │  Email   │
│ 30+ tbls │ │ GraphQL  │ │ Jinja2   │
└──────────┘ └──────────┘ └──────────┘

┌─────────────────────────────────────────────────┐
│              Marketing Sites (Vercel)             │
│  marketing-gyms (Astro) │ marketing-consumers    │
└─────────────────────────────────────────────────┘
```

## Key Components

### Multi-Tenancy Pattern
`Gym` is the tenant root. All gym-scoped data inherits from `GymScopedModel` which enforces `gym_id` FK. `GymScopedRepository` auto-filters all queries by `gym_id`. Staff JWT tokens include `gym_id` claim; mismatches raise `TenantAccessError` (403).

### Authentication (3 systems)
1. **Consumer** — Email/password + Google/Apple OAuth. Mobile tokens in MMKV.
2. **Staff** — Email/password + OAuth with `gym_id` claim. 4-tier RBAC.
3. **Admin** — Superuser (legacy, will deprecate in favor of staff+RBAC).

### Domain Models (30+)
Grouped into: Auth (User, Consumer, Staff), Gym Ops (Gym, Space, ClassTemplate, ClassSession), Memberships (MembershipPlan, GymMembership, Booking, WaitlistEntry), Payments (Payment, PaymentWebhookEvent, PaymentReceipt, MarketplaceSubscription), Notifications (Notification, NotificationTemplate), Admin (Complaint, CreditLog, AuditLog, WebhookEndpoint).

### Frontend Monorepo (5 apps)
- **gym-web** (React 19, Vite, port 5174) — Staff/owner portal
- **consumer-web** (React 19, Vite, port 5175) — Member portal
- **consumer-mobile** (Expo 54, NativeWind) — Consumer app
- **gym-mobile** (Expo 54 + QR scanning) — Staff app with check-in
- **marketing-gyms** + **marketing-consumers** (Astro 5) — Landing pages

### Shared Packages
- **api-client** — @hey-api OpenAPI codegen + TanStack Query hooks
- **ui** — 19 shared components (Button, Input, Card, Modal, MetricCard, ClassCard, etc.)
- **utils** — Shared utilities

## External Dependencies

| Service | Role | Status |
|---------|------|--------|
| Stitch | Payments (Pay By Bank, VRP) | Integration tested |
| Svix | Webhook routing + signing | Active |
| Google OAuth | Consumer + staff social login | Active |
| Apple Sign-In | Consumer + staff social login | Active |
| SMTP | Transactional email | Active |
| Sentry | Error monitoring | Active (non-local) |
| Railway | Backend + PostgreSQL hosting (JNB) | Active |
| Vercel | Frontend hosting (CDN) | Active |

## Notable Patterns

1. **GymScopedRepository** — Generic CRUD with automatic `gym_id` filtering. Prevents tenant data leaks at the ORM level.
2. **Consistent error responses** — `StudioLoopError` hierarchy (NotFound, Validation, Conflict, PermissionDenied, TenantAccess, BusinessRule) with standard JSON structure.
3. **OpenAPI client codegen** — Backend OpenAPI spec auto-generates typed TypeScript SDK + TanStack Query hooks.
4. **Design tokens via CSS vars** — `data-theme` attribute toggles dark/light themes. Tailwind v4 CSS variable overrides.
5. **Waitlist auto-promotion** — When a class booking is cancelled, next waitlist entry is auto-promoted with 24h expiry.
6. **Soft-delete with audit** — `GymScopedSoftDeleteModel` for data preservation + AuditLog for POPIA compliance.
