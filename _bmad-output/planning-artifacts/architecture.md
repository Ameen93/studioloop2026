---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
status: 'complete'
completedAt: '2026-01-21'
inputDocuments:
  - prd.md
  - product-brief-studioloop-2026-01-21.md
  - api-brainstorm.md
  - gym-management-app-brainstorm.md
  - consumer-app-brainstorm.md
workflowType: 'architecture'
project_name: 'studioloop'
user_name: 'Ameen'
date: '2026-01-21'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
The PRD defines 85 functional requirements across 13 capability areas. The core value propositions are:
1. **Gym operations** (FR7-FR30): Replace spreadsheet chaos with structured member, staff, and space management
2. **Class lifecycle** (FR31-FR48): End-to-end scheduling with approval workflows, booking, waitlists, and check-in (QR scanner on Gym Mobile, manual on Gym Web)
3. **Marketplace discovery** (FR49-FR56): Cross-gym class browsing with subscriptions and pay-per-class
4. **Revenue enablement** (FR57-FR76): Payment tracking, notifications, and actionable analytics

**Non-Functional Requirements:**
38 NFRs establish hard constraints that will drive architectural decisions:
- **Performance**: <200ms API p95, <1s WebSocket latency, <2s QR scan check-in (Gym Mobile)
- **Security**: AES-256 at rest, TLS 1.2+, JWT <24h expiry, zero cross-tenant leakage
- **Scalability**: 5,000+ concurrent users, 10,000 WebSocket connections, 100 bookings/min peak
- **Reliability**: 99.5% uptime, offline QR capability, <4hr RTO
- **Compliance**: POPIA (SA data protection), data residency, consent tracking

**Scale & Complexity:**

- Primary domain: Full-stack SaaS platform with B2B (web + mobile) and B2C (web + mobile) applications
- Complexity level: Medium-High
- Estimated architectural components: 6-8 major subsystems

### Technical Constraints & Dependencies

| Constraint | Impact |
|------------|--------|
| POPIA compliance | SA-hosted or compliant cloud, data export/deletion flows, consent tracking |
| Multi-tenancy | Database-level isolation for gym data, shared consumer identity layer |
| Offline QR capability | Local QR code generation (consumer), offline QR scanning (gym mobile), sync queue when connectivity restored |
| Payment gateway deferred | Abstracted interface required, Ozow/PayFast integration post-MVP |
| WhatsApp preference | Business API integration for notifications |
| Mobile-first SA users | Lightweight initial bundle (<1MB), lazy loading, data-conscious design |

### Cross-Cutting Concerns Identified

| Concern | Affected Components | Architectural Implication |
|---------|---------------------|---------------------------|
| **Multi-tenancy** | All gym data, API authorization | Tenant-aware middleware, row-level security |
| **Authentication** | Consumer app, Gym app, Admin | Unified auth service with role-based token claims |
| **Real-time sync** | Class availability, waitlist, bookings | WebSocket gateway with Redis pub/sub |
| **Booking integrity** | Sessions, waitlist, check-in | Optimistic locking, idempotent operations |
| **Payment abstraction** | Memberships, marketplace, bookings | Strategy pattern for provider swapping |
| **Offline resilience** | QR code display + scanner, cached class data | Local-first architecture for critical paths |
| **Notification orchestration** | Email, push, WhatsApp | Unified notification service with channel routing |
| **Audit & compliance** | All user data operations | Event sourcing or audit log pattern |

## Starter Template Evaluation

### Primary Technology Domain

Full-stack TypeScript platform with:
- Python/FastAPI backend (API layer)
- React Native/Expo mobile apps (consumer + gym management)
- React web applications (gym management + consumer)

### Platform Strategy

StudioLoop consists of **6 client applications** plus the backend:

| Component | Platform | URL/Distribution | Purpose |
|-----------|----------|------------------|---------|
| **FastAPI Backend** | Server | `api.studioloop.co.za` | Shared API layer |
| **Gym Management Web** | React | `manage.studioloop.co.za` | Full gym operations, reports, settings |
| **Consumer Web** | React | `app.studioloop.co.za` | Class browsing, booking, QR display |
| **Consumer Mobile App** | iOS + Android | App Store / Play Store | On-the-go booking, QR code display |
| **Gym Management Mobile App** | iOS + Android | App Store / Play Store | On-floor QR scanner, quick access |

**Development Priority (Web-First Validation):**
1. Gym Management Web — validate all gym features first
2. Consumer Web — validate all consumer features
3. Consumer Mobile (iOS + Android) — port validated features
4. Gym Management Mobile (iOS + Android) — add mobile-specific tools

**Platform-Specific Features:**
| Feature | Consumer Web | Consumer Mobile | Gym Web | Gym Mobile |
|---------|--------------|-----------------|---------|------------|
| QR code display | ✅ | ✅ | — | — |
| QR scanner | — | — | — | ✅ Only |
| Full reports/analytics | — | — | ✅ | ✅ |
| Class browsing/booking | ✅ | ✅ | — | — |
| Member management | — | — | ✅ | ✅ |

**Rationale:** Web-first approach validates features before mobile investment. Two separate web applications (`manage.` and `app.`) provide clear separation of concerns and distinct user experiences.

### Starter Options Considered

| Component | Options Evaluated | Selected |
|-----------|-------------------|----------|
| Backend | Official FastAPI Template, Minimal FastAPI Postgres | Official Full Stack FastAPI Template |
| Mobile Framework | Flutter, React Native/Expo | React Native with Expo |
| Monorepo Tool | Nx, Turborepo, Lerna | Turborepo + pnpm |
| Web Framework | Next.js, Vite+React, Remix | Vite + React (or Next.js for SEO) |

### Selected Architecture: TypeScript Monorepo + FastAPI Backend

**Rationale:**
1. **Code sharing** - Single language (TypeScript) across web + mobile enables shared API clients, types, and utilities
2. **Web-first validation** - Build and validate features on web apps first, then port to mobile
3. **Offline support** - Expo SQLite + React Query provide robust offline-first patterns for mobile
4. **Styling consistency** - NativeWind (Tailwind for RN) + Tailwind CSS ensures design system parity
5. **Build efficiency** - Turborepo caching reduces CI/CD times significantly

### Repository Structure

```
studioloop/
├── backend/                    # FastAPI + PostgreSQL
│   └── (Full Stack FastAPI Template)
│
└── frontend/                   # Turborepo + pnpm monorepo
    ├── apps/
    │   ├── gym-web/            # React (Vite) - manage.studioloop.co.za [Priority 1]
    │   ├── consumer-web/       # React (Vite) - app.studioloop.co.za [Priority 2]
    │   ├── consumer-mobile/    # Expo React Native [Priority 3]
    │   └── gym-mobile/         # Expo React Native [Priority 4]
    │
    └── packages/
        ├── api-client/         # Shared API client + types (generated via Hey API)
        ├── ui/                 # Shared components (Tailwind for web, NativeWind for mobile)
        └── utils/              # Shared utilities (formatting, validation)
```

### Initialization Commands

**Backend:**
```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust
```

**Frontend Monorepo:**
```bash
mkdir frontend && cd frontend
pnpm init
pnpm add -D turbo
# Configure workspaces and add apps/packages per structure
```

### Architectural Decisions Provided by Starters

**Language & Runtime:**
- Backend: Python 3.11+ with FastAPI, async/await throughout
- Frontend: TypeScript 5.x strict mode across all apps

**Styling Solution:**
- Mobile: NativeWind v4 (Tailwind CSS for React Native)
- Web: Tailwind CSS v4
- Shared design tokens via packages/ui

**Build Tooling:**
- Backend: Docker, uvicorn, gunicorn
- Frontend: Turborepo for orchestration, Metro for RN, Vite for web

**Testing Framework:**
- Backend: pytest with async support
- Frontend: Jest + React Testing Library, Detox for E2E mobile

**Code Organization:**
- Feature-based modules in backend
- Screen-based organization in mobile apps
- Route-based organization in web app
- Shared packages for cross-cutting concerns

**Development Experience:**
- Hot reload across all platforms
- TypeScript strict mode with shared configs
- ESLint + Prettier with pre-commit hooks
- Turborepo remote caching for CI

**Note:** Project initialization using these commands should be the first implementation epic.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Authentication strategy
- Database and caching
- API client generation
- Hosting infrastructure (POPIA compliance)

**Important Decisions (Shape Architecture):**
- State management approach
- Offline storage strategy
- Payment gateway selection

**Deferred Decisions (Post-MVP):**
- Advanced analytics/ML
- Multi-region scaling
- Third-party integrations beyond core

### Authentication & Security

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Auth Strategy** | Custom JWT (FastAPI native) | Full POPIA compliance control, no vendor lock-in, included in starter template |
| **Token Management** | JWT access (<24h) + refresh rotation | Security best practice, mobile-friendly |
| **Password Hashing** | Argon2 via pwdlib | Current recommendation, memory-hard algorithm |
| **Social Login** | Authlib (Google, Apple) | Add when needed, clean abstraction |
| **RBAC** | Role claims in JWT | Owner, Manager, Front Desk, Instructor, Consumer, Platform Admin |

**Security Layers:**
- TLS 1.2+ for all communications
- AES-256 encryption at rest
- Row-level security for multi-tenant isolation
- Rate limiting per user/gym
- Audit logging for compliance

### Data Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Primary Database** | PostgreSQL 16 + PostGIS | Relational data, geo queries for class discovery, mature ecosystem |
| **ORM** | SQLModel (async) | Combines Pydantic + SQLAlchemy, FastAPI native |
| **Migrations** | Alembic | Industry standard, included in starter |
| **Caching** | Redis (self-hosted on Fly.io) | Session storage, real-time pub/sub, booking locks |
| **Validation** | Pydantic v2 | Request/response schemas, automatic OpenAPI |

**Caching Strategy:**
- Redis for: auth tokens, class availability (30s TTL), rate limiting, WebSocket pub/sub, booking locks
- Application-level caching for: static config, membership plans

### API & Communication

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **API Style** | REST | Clear resource URLs, good caching, already designed in brainstorm |
| **Documentation** | OpenAPI 3.1 (auto-generated) | FastAPI native, single source of truth |
| **Client Generation** | Hey API (@hey-api/openapi-ts) | FastAPI official recommendation, TanStack Query hooks |
| **Real-time** | WebSocket + Redis pub/sub | Class availability, waitlist updates, booking confirmations |
| **Webhooks** | Outbound events for gym integrations | booking.*, membership.*, payment.* events |

**Error Handling Standard:**
```json
{
  "error": {
    "code": "BOOKING_CONFLICT",
    "message": "Class is fully booked",
    "details": { "session_id": "...", "spots_available": 0 }
  }
}
```

### Frontend Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Server State** | TanStack Query v5 | Industry standard, caching, background sync, offline support |
| **Client State** | Zustand | Lightweight, minimal boilerplate, works with Query |
| **Offline (KV)** | MMKV | 30x faster than AsyncStorage for tokens/preferences |
| **Offline (Relational)** | Expo SQLite | Complex offline data, booking queue, check-in sync |
| **Navigation** | Expo Router | File-based routing, deep linking support |
| **Styling** | NativeWind v4 + Tailwind CSS v4 | Consistent design system across mobile and web |

**Offline Strategy:**
- MMKV: Auth tokens, user preferences, feature flags
- Expo SQLite: Cached class schedules, pending bookings, check-in queue
- Sync on reconnect with conflict resolution (server wins for bookings)

### Infrastructure & Deployment

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Hosting (MVP)** | Fly.io Johannesburg (`jnb`) | SA data residency for POPIA, cost-effective |
| **Database** | Fly Postgres (Johannesburg) | Managed, same region as app, automatic backups |
| **Redis** | Self-hosted on Fly.io | No managed Redis in SA, simple single-node for MVP |
| **Mobile Builds** | EAS Build (Expo) | Cloud builds, OTA updates, app store submission |
| **CI/CD** | GitHub Actions + Turborepo | Caching, parallel builds, deploy on merge |
| **Monitoring** | Sentry + Fly Metrics | Error tracking, performance monitoring |

**Scaling Path:**
- MVP: Single Fly machine + Fly Postgres + Redis
- Growth: Multiple machines with load balancing
- Scale: Migrate to AWS Cape Town (ECS + RDS + ElastiCache) if needed

### Payment Integration

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Primary Gateway** | Ozow | 80% SA instant EFT market share, lower fees (2.5% → 1.5%) |
| **Secondary Gateway** | PayFast | Cards, SnapScan, Zapper for broader coverage |
| **Architecture** | Abstracted payment interface | Strategy pattern for easy provider swapping |
| **Implementation** | Deferred to pre-launch | Interface ready, integration when business ready |

**Payment Flow:**
```
Consumer → StudioLoop API → Payment Service → Ozow/PayFast → Bank
                              ↓
                        Webhook callback → Update booking/membership status
```

### Decision Impact Analysis

**Implementation Sequence:**
1. Backend setup (FastAPI template + Fly.io deployment)
2. Database schema + migrations
3. Auth system (JWT + RBAC)
4. Core API endpoints
5. Frontend monorepo setup
6. API client generation (Hey API)
7. Mobile app scaffolding (consumer + gym)
8. Web app scaffolding
9. Feature implementation by epic

**Cross-Component Dependencies:**

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │  Auth   │  │   API   │  │ WebSocket│  │   Background    │ │
│  │ Service │  │ Routes  │  │ Gateway  │  │   Workers       │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘ │
│       │            │            │                 │          │
│       └────────────┴────────────┴─────────────────┘          │
│                           │                                   │
│              ┌────────────┴────────────┐                     │
│              │     PostgreSQL + Redis   │                     │
│              └──────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                            │
                    OpenAPI Schema
                            │
                    ┌───────┴───────┐
                    │   Hey API     │
                    │  (codegen)    │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────┴───────┐   ┌───────┴───────┐   ┌───────┴───────┐
│ Consumer App  │   │   Gym App     │   │   Web App     │
│ (Expo RN)     │   │  (Expo RN)    │   │  (React)      │
│               │   │               │   │               │
│ TanStack Query│   │ TanStack Query│   │ TanStack Query│
│ + Zustand     │   │ + Zustand     │   │ + Zustand     │
│ + MMKV/SQLite │   │ + MMKV/SQLite │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Implementation Patterns & Consistency Rules

These patterns ensure AI agents and developers write consistent, compatible code that integrates seamlessly.

### Pattern Categories Defined

**Critical Conflict Points Identified:** 25+ areas where AI agents could make different choices, organized into naming, structure, format, communication, and process patterns.

### Naming Patterns

#### Database Naming (PostgreSQL)

| Element | Convention | Example |
|---------|------------|---------|
| Tables | snake_case, plural | `gyms`, `class_sessions`, `membership_plans` |
| Columns | snake_case | `created_at`, `gym_id`, `is_active` |
| Foreign keys | `{table}_id` | `gym_id`, `consumer_id` |
| Indexes | `idx_{table}_{columns}` | `idx_bookings_session_id` |
| Constraints | `{table}_{type}_{column}` | `bookings_fk_consumer_id` |

#### API Naming (REST)

| Element | Convention | Example |
|---------|------------|---------|
| Endpoints | snake_case, plural nouns | `/gyms`, `/class_sessions`, `/membership_plans` |
| Path params | snake_case | `/gyms/{gym_id}/sessions/{session_id}` |
| Query params | snake_case | `?start_date=2026-01-21&class_type=yoga` |
| Request/Response body | snake_case | `{ "gym_id": "...", "start_time": "..." }` |

#### Code Naming

| Language | Element | Convention | Example |
|----------|---------|------------|---------|
| Python | Functions/variables | snake_case | `get_gym_by_id`, `consumer_id` |
| Python | Classes | PascalCase | `GymService`, `BookingRepository` |
| Python | Constants | SCREAMING_SNAKE | `MAX_RETRY_ATTEMPTS` |
| TypeScript | Functions/variables | camelCase | `getGymById`, `consumerId` |
| TypeScript | Components | PascalCase | `GymCard`, `BookingList` |
| TypeScript | Types/Interfaces | PascalCase | `Gym`, `BookingResponse` |
| TypeScript | Constants | SCREAMING_SNAKE | `MAX_RETRY_ATTEMPTS` |

#### File Naming

| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `gym_service.py`, `booking_repository.py` |
| React components | PascalCase | `GymCard.tsx`, `BookingList.tsx` |
| TypeScript utils | camelCase | `formatDate.ts`, `apiClient.ts` |
| Test files | `*.test.ts` or `*.spec.ts` | `GymCard.test.tsx` |

### Structure Patterns

#### Backend Structure (FastAPI)

```
backend/
├── app/
│   ├── api/
│   │   └── routes/           # Route handlers grouped by domain
│   │       ├── gyms.py
│   │       ├── bookings.py
│   │       └── auth.py
│   ├── core/                 # Core config, security, dependencies
│   ├── models/               # SQLModel database models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic
│   ├── repositories/         # Data access layer
│   └── utils/                # Shared utilities
├── tests/                    # Mirror app/ structure
│   ├── api/
│   ├── services/
│   └── conftest.py
└── alembic/                  # Database migrations
```

#### Frontend Structure (Monorepo)

```
frontend/
├── apps/
│   ├── gym-web/              # React (Vite) - Priority 1
│   │   └── src/
│   │       ├── routes/       # React Router screens
│   │       ├── components/   # Screen-specific components
│   │       ├── hooks/        # Custom hooks
│   │       └── stores/       # Zustand stores
│   ├── consumer-web/         # React (Vite) - Priority 2
│   │   └── src/              # Same structure as gym-web
│   ├── consumer-mobile/      # Expo React Native - Priority 3
│   │   └── src/
│   │       ├── app/          # Expo Router screens
│   │       ├── components/   # Screen-specific components
│   │       ├── hooks/        # Custom hooks
│   │       └── stores/       # Zustand stores
│   └── gym-mobile/           # Expo React Native - Priority 4
│       └── src/              # Same structure as consumer-mobile
│
└── packages/
    ├── api-client/           # Generated API client + custom hooks
    ├── ui/                   # Shared UI components
    │   └── src/
    │       ├── components/   # Reusable components
    │       └── primitives/   # Base elements (Button, Input)
    └── utils/                # Shared utilities
        └── src/
            ├── formatting/   # Date, currency, etc.
            └── validation/   # Shared validators
```

#### Test Location

| Type | Location | Rationale |
|------|----------|-----------|
| Unit tests | Co-located `*.test.ts` | Easy to find, maintain together |
| Integration tests | `tests/` directory | Separate from source |
| E2E tests | `e2e/` at app root | Detox/Playwright separation |

### Format Patterns

#### API Response Format

**Success Response (direct data):**
```json
{
  "id": "uuid",
  "name": "string",
  "created_at": "2026-01-21T10:00:00Z"
}
```

**List Response (with pagination):**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

#### Date/Time Format

| Context | Format | Example |
|---------|--------|---------|
| API (JSON) | ISO 8601 with timezone | `2026-01-21T10:00:00Z` |
| Database | timestamptz | Stored as UTC |
| Display (SA) | `DD MMM YYYY, HH:mm` | `21 Jan 2026, 10:00` |

#### ID Format

- Use UUIDs (v4) for all primary keys
- Format: `550e8400-e29b-41d4-a716-446655440000`

### Communication Patterns

#### WebSocket Events

```json
{
  "event": "session.spots_updated",
  "data": {
    "session_id": "uuid",
    "spots_available": 3,
    "timestamp": "2026-01-21T10:00:00Z"
  }
}
```

**Event Naming:** `{domain}.{action}` — e.g., `session.spots_updated`, `waitlist.spot_offered`, `booking.confirmed`

#### Webhook Events (Outbound)

**Naming:** `{resource}.{past_tense_action}` — e.g., `booking.created`, `membership.renewed`, `payment.failed`

#### State Management (Zustand)

```typescript
// Store naming: use{Domain}Store
const useBookingStore = create<BookingStore>((set) => ({
  pendingBookings: [],
  addPendingBooking: (booking) => set(...),
  removePendingBooking: (id) => set(...),
  clearPendingBookings: () => set(...),
}));
```

**Action Naming:** `verb` + `noun` — e.g., `addPendingBooking`, `clearPendingBookings`

### Process Patterns

#### Error Handling

**Frontend:**
- Use error boundaries for unexpected errors
- Toast notifications for API errors
- User-friendly messages, log technical details

**Backend:**
```python
class BookingConflictError(AppException):
    code = "BOOKING_CONFLICT"
    status_code = 409
```

#### Loading States

- TanStack Query handles via `isLoading`, `isFetching`
- Use skeleton components for content areas, not spinners
- Optimistic updates for mutations where appropriate

#### Offline Sync Pattern

1. Write to local SQLite
2. Queue for sync
3. On reconnect, process queue (FIFO)
4. Server wins for conflicts (bookings)
5. Show sync status indicator in UI

### Enforcement Guidelines

**All AI Agents MUST:**

1. Follow snake_case for all API/database identifiers
2. Follow camelCase for TypeScript variables, PascalCase for components/types
3. Use the standard error response format
4. Co-locate unit tests with source files (`*.test.ts`)
5. Use ISO 8601 for all date/time in APIs
6. Use UUIDs for all entity IDs
7. Follow the established project structure

**Pattern Verification:**

- ESLint rules enforce naming conventions
- Pre-commit hooks validate formatting (Prettier, Ruff)
- CI/CD fails on pattern violations
- Code review checklist includes pattern compliance

### Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `userId` in API response | `user_id` |
| `Users` table name | `users` |
| Spinners for content loading | Skeleton components |
| Wrapper objects for simple responses | Direct data response |
| `GET /user` (singular) | `GET /users` (plural) |
| `createdAt` in database | `created_at` |

## Project Structure & Boundaries

### Complete Project Directory Structure

```
studioloop/
├── README.md
├── docker-compose.yml              # Local dev: Postgres + Redis
├── docker-compose.prod.yml         # Production config
├── Makefile                        # Common dev commands
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint, test, type-check
│       ├── deploy-backend.yml      # Deploy to Fly.io
│       ├── deploy-gym-web.yml      # Deploy gym-web to Vercel/Fly.io
│       ├── deploy-consumer-web.yml # Deploy consumer-web to Vercel/Fly.io
│       └── deploy-mobile.yml       # EAS Build trigger for mobile apps
│
├── backend/                        # FastAPI Backend
│   ├── README.md
│   ├── pyproject.toml              # Poetry/uv dependencies
│   ├── Dockerfile
│   ├── fly.toml                    # Fly.io deployment config
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/               # Migration files
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Settings from env
│   │   │   ├── database.py         # Async SQLModel setup
│   │   │   ├── redis.py            # Redis client
│   │   │   ├── security.py         # JWT, password hashing
│   │   │   └── dependencies.py     # FastAPI dependencies
│   │   │
│   │   ├── models/                 # SQLModel database models
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base model with UUID, timestamps
│   │   │   ├── gym.py              # Gym, Space
│   │   │   ├── consumer.py         # Consumer
│   │   │   ├── staff.py            # Staff, StaffShift
│   │   │   ├── membership.py       # Membership, MembershipPlan
│   │   │   ├── class_session.py    # Class, ClassSession
│   │   │   ├── booking.py          # Booking, WaitlistEntry
│   │   │   ├── payment.py          # Payment
│   │   │   └── marketplace.py      # MarketplaceSubscription
│   │   │
│   │   ├── schemas/                # Pydantic request/response
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── gym.py
│   │   │   ├── consumer.py
│   │   │   ├── staff.py
│   │   │   ├── membership.py
│   │   │   ├── class_session.py
│   │   │   ├── booking.py
│   │   │   ├── payment.py
│   │   │   ├── marketplace.py
│   │   │   └── common.py           # Pagination, errors
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Route dependencies
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py         # Consumer + Staff auth
│   │   │       ├── gyms.py         # Gym CRUD, dashboard
│   │   │       ├── spaces.py       # Space management
│   │   │       ├── staff.py        # Staff management
│   │   │       ├── memberships.py  # Plans + memberships
│   │   │       ├── classes.py      # Class templates
│   │   │       ├── sessions.py     # Class sessions, scheduling
│   │   │       ├── bookings.py     # Booking, check-in
│   │   │       ├── waitlist.py     # Waitlist operations
│   │   │       ├── marketplace.py  # Discovery, subscriptions
│   │   │       ├── payments.py     # Payment interface
│   │   │       ├── notifications.py
│   │   │       ├── reports.py      # Gym analytics
│   │   │       ├── webhooks.py     # Webhook management
│   │   │       └── admin.py        # Platform admin
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── gym_service.py
│   │   │   ├── membership_service.py
│   │   │   ├── booking_service.py
│   │   │   ├── waitlist_service.py
│   │   │   ├── marketplace_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── payment_service.py  # Abstracted interface
│   │   │   ├── report_service.py
│   │   │   └── webhook_service.py
│   │   │
│   │   ├── repositories/           # Data access
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Generic CRUD repository
│   │   │   ├── gym_repository.py
│   │   │   ├── consumer_repository.py
│   │   │   ├── membership_repository.py
│   │   │   ├── booking_repository.py
│   │   │   └── session_repository.py
│   │   │
│   │   ├── websocket/              # Real-time
│   │   │   ├── __init__.py
│   │   │   ├── manager.py          # Connection manager
│   │   │   ├── handlers.py         # Event handlers
│   │   │   └── events.py           # Event definitions
│   │   │
│   │   ├── workers/                # Background tasks
│   │   │   ├── __init__.py
│   │   │   ├── notification_worker.py
│   │   │   ├── payment_worker.py
│   │   │   └── webhook_worker.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── datetime.py         # Timezone handling
│   │       ├── qr_code.py          # QR generation/validation
│   │       └── exceptions.py       # Custom exceptions
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # Fixtures, test DB
│       ├── api/
│       │   ├── test_auth.py
│       │   ├── test_gyms.py
│       │   ├── test_bookings.py
│       │   └── test_marketplace.py
│       ├── services/
│       │   ├── test_booking_service.py
│       │   └── test_waitlist_service.py
│       └── integration/
│           └── test_booking_flow.py
│
└── frontend/                       # TypeScript Monorepo
    ├── README.md
    ├── package.json                # Workspace root
    ├── pnpm-workspace.yaml
    ├── pnpm-lock.yaml
    ├── turbo.json                  # Turborepo config
    ├── tsconfig.base.json          # Shared TS config
    ├── .eslintrc.js                # Shared ESLint
    ├── .prettierrc                 # Shared Prettier
    ├── .npmrc                      # pnpm config (hoisted)
    │
    ├── apps/
    │   ├── consumer-mobile/        # Consumer Expo App
    │   │   ├── package.json
    │   │   ├── app.json            # Expo config
    │   │   ├── eas.json            # EAS Build config
    │   │   ├── tsconfig.json
    │   │   ├── tailwind.config.js  # NativeWind
    │   │   ├── metro.config.js
    │   │   ├── babel.config.js
    │   │   ├── index.ts
    │   │   │
    │   │   └── src/
    │   │       ├── app/            # Expo Router
    │   │       │   ├── _layout.tsx
    │   │       │   ├── index.tsx   # Home (bookings)
    │   │       │   ├── (auth)/
    │   │       │   │   ├── login.tsx
    │   │       │   │   ├── register.tsx
    │   │       │   │   └── onboarding.tsx
    │   │       │   ├── (tabs)/
    │   │       │   │   ├── _layout.tsx
    │   │       │   │   ├── home.tsx
    │   │       │   │   ├── discover.tsx
    │   │       │   │   ├── memberships.tsx
    │   │       │   │   └── profile.tsx
    │   │       │   ├── class/[session_id].tsx
    │   │       │   ├── gym/[gym_id].tsx
    │   │       │   ├── booking/[booking_id].tsx
    │   │       │   └── qr-code.tsx
    │   │       │
    │   │       ├── components/
    │   │       │   ├── BookingCard.tsx
    │   │       │   ├── ClassCard.tsx
    │   │       │   ├── GymCard.tsx
    │   │       │   ├── QRCodeDisplay.tsx
    │   │       │   └── skeletons/
    │   │       │
    │   │       ├── hooks/
    │   │       │   ├── useAuth.ts
    │   │       │   ├── useBookings.ts
    │   │       │   └── useOfflineSync.ts
    │   │       │
    │   │       ├── stores/
    │   │       │   ├── authStore.ts
    │   │       │   ├── bookingStore.ts
    │   │       │   └── syncStore.ts
    │   │       │
    │   │       └── lib/
    │   │           ├── sqlite.ts   # Expo SQLite setup
    │   │           └── mmkv.ts     # MMKV setup
    │   │
    │   ├── gym-mobile/             # Gym Management Expo App
    │   │   ├── package.json
    │   │   ├── app.json
    │   │   ├── eas.json
    │   │   ├── tsconfig.json
    │   │   ├── tailwind.config.js
    │   │   │
    │   │   └── src/
    │   │       ├── app/
    │   │       │   ├── _layout.tsx
    │   │       │   ├── index.tsx   # Dashboard
    │   │       │   ├── (auth)/
    │   │       │   │   └── login.tsx
    │   │       │   ├── (tabs)/
    │   │       │   │   ├── _layout.tsx
    │   │       │   │   ├── dashboard.tsx
    │   │       │   │   ├── check-in.tsx
    │   │       │   │   ├── schedule.tsx
    │   │       │   │   └── members.tsx
    │   │       │   ├── class/[session_id].tsx
    │   │       │   ├── member/[consumer_id].tsx
    │   │       │   ├── settings/
    │   │       │   │   ├── gym-profile.tsx
    │   │       │   │   ├── staff.tsx
    │   │       │   │   ├── spaces.tsx
    │   │       │   │   └── membership-plans.tsx
    │   │       │   └── reports/
    │   │       │       ├── revenue.tsx
    │   │       │       └── attendance.tsx
    │   │       │
    │   │       ├── components/
    │   │       │   ├── DashboardCard.tsx
    │   │       │   ├── CheckInScanner.tsx
    │   │       │   ├── MemberCard.tsx
    │   │       │   ├── SessionCard.tsx
    │   │       │   └── ActionItem.tsx
    │   │       │
    │   │       ├── hooks/
    │   │       │   ├── useGymAuth.ts
    │   │       │   ├── useDashboard.ts
    │   │       │   └── useCheckIn.ts
    │   │       │
    │   │       └── stores/
    │   │           ├── gymAuthStore.ts
    │   │           └── checkInStore.ts
    │   │
    │   ├── gym-web/                 # Gym Management Web App [Priority 1]
    │   │   │                        # manage.studioloop.co.za
    │   │   ├── package.json
    │   │   ├── vite.config.ts
    │   │   ├── tsconfig.json
    │   │   ├── tailwind.config.js
    │   │   ├── index.html
    │   │   │
    │   │   └── src/
    │   │       ├── main.tsx
    │   │       ├── App.tsx
    │   │       ├── index.css
    │   │       │
    │   │       ├── routes/         # React Router
    │   │       │   ├── index.tsx
    │   │       │   ├── auth/
    │   │       │   │   └── Login.tsx
    │   │       │   ├── dashboard/
    │   │       │   │   └── Dashboard.tsx
    │   │       │   ├── members/
    │   │       │   │   ├── MemberList.tsx
    │   │       │   │   └── MemberDetail.tsx
    │   │       │   ├── schedule/
    │   │       │   │   ├── Schedule.tsx
    │   │       │   │   └── ClassDetail.tsx
    │   │       │   ├── check-in/
    │   │       │   │   └── CheckIn.tsx  # Manual check-in (no scanner)
    │   │       │   ├── reports/
    │   │       │   │   ├── Revenue.tsx
    │   │       │   │   ├── Attendance.tsx
    │   │       │   │   └── Membership.tsx
    │   │       │   └── settings/
    │   │       │       ├── GymProfile.tsx
    │   │       │       ├── Staff.tsx
    │   │       │       ├── Spaces.tsx
    │   │       │       └── MembershipPlans.tsx
    │   │       │
    │   │       ├── components/
    │   │       │   ├── layout/
    │   │       │   │   ├── Header.tsx
    │   │       │   │   ├── Sidebar.tsx
    │   │       │   │   └── Footer.tsx
    │   │       │   ├── dashboard/
    │   │       │   ├── members/
    │   │       │   ├── schedule/
    │   │       │   └── reports/
    │   │       │
    │   │       ├── hooks/
    │   │       │   ├── useGymAuth.ts
    │   │       │   └── useDashboard.ts
    │   │       │
    │   │       └── stores/
    │   │           └── gymAuthStore.ts
    │   │
    │   └── consumer-web/            # Consumer Web App [Priority 2]
    │       │                        # app.studioloop.co.za
    │       ├── package.json
    │       ├── vite.config.ts
    │       ├── tsconfig.json
    │       ├── tailwind.config.js
    │       ├── index.html
    │       │
    │       └── src/
    │           ├── main.tsx
    │           ├── App.tsx
    │           ├── index.css
    │           │
    │           ├── routes/         # React Router
    │           │   ├── index.tsx
    │           │   ├── auth/
    │           │   │   ├── Login.tsx
    │           │   │   └── Register.tsx
    │           │   ├── home/
    │           │   │   └── Home.tsx       # Bookings list
    │           │   ├── discover/
    │           │   │   ├── Discover.tsx   # Class browse
    │           │   │   ├── ClassDetail.tsx
    │           │   │   └── GymDetail.tsx
    │           │   ├── memberships/
    │           │   │   └── Memberships.tsx
    │           │   ├── qr-code/
    │           │   │   └── QRCode.tsx     # QR display for check-in
    │           │   └── profile/
    │           │       └── Profile.tsx
    │           │
    │           ├── components/
    │           │   ├── layout/
    │           │   │   ├── Header.tsx
    │           │   │   └── Footer.tsx
    │           │   ├── home/
    │           │   ├── discover/
    │           │   └── qr/
    │           │
    │           ├── hooks/
    │           │   ├── useAuth.ts
    │           │   └── useBookings.ts
    │           │
    │           └── stores/
    │               └── authStore.ts
    │
    └── packages/
        ├── api-client/             # Generated + Custom
        │   ├── package.json
        │   ├── tsconfig.json
        │   ├── src/
        │   │   ├── index.ts
        │   │   ├── generated/      # Hey API output
        │   │   │   ├── client.ts
        │   │   │   ├── types.ts
        │   │   │   └── services/
        │   │   ├── hooks/          # Custom TanStack Query hooks
        │   │   │   ├── useGyms.ts
        │   │   │   ├── useBookings.ts
        │   │   │   ├── useSessions.ts
        │   │   │   └── useMarketplace.ts
        │   │   └── websocket/
        │   │       └── client.ts
        │   └── scripts/
        │       └── generate.ts     # OpenAPI codegen script
        │
        ├── ui/                     # Shared UI Components
        │   ├── package.json
        │   ├── tsconfig.json
        │   ├── src/
        │   │   ├── index.ts
        │   │   ├── primitives/
        │   │   │   ├── Button.tsx
        │   │   │   ├── Input.tsx
        │   │   │   ├── Card.tsx
        │   │   │   ├── Modal.tsx
        │   │   │   └── Toast.tsx
        │   │   ├── components/
        │   │   │   ├── Avatar.tsx
        │   │   │   ├── Badge.tsx
        │   │   │   ├── Skeleton.tsx
        │   │   │   └── EmptyState.tsx
        │   │   └── tokens/
        │   │       ├── colors.ts
        │   │       ├── spacing.ts
        │   │       └── typography.ts
        │   └── tailwind.config.js  # Shared Tailwind preset
        │
        └── utils/                  # Shared Utilities
            ├── package.json
            ├── tsconfig.json
            └── src/
                ├── index.ts
                ├── formatting/
                │   ├── date.ts     # SA date formatting
                │   ├── currency.ts # ZAR formatting
                │   └── time.ts     # Duration, relative time
                ├── validation/
                │   ├── email.ts
                │   ├── phone.ts    # SA phone validation
                │   └── id.ts       # SA ID number
                └── constants/
                    ├── routes.ts
                    └── config.ts
```

### Architectural Boundaries

#### API Boundaries

| Boundary | Endpoint Pattern | Responsibility |
|----------|------------------|----------------|
| Consumer Auth | `POST /auth/consumer/*` | Consumer registration, login, tokens |
| Staff Auth | `POST /auth/staff/*` | Staff login, gym-scoped access |
| Gym Management | `/gyms/{gym_id}/*` | Gym-scoped operations, tenant isolated |
| Marketplace | `/marketplace/*` | Cross-gym discovery, subscriptions |
| Platform Admin | `/admin/*` | Platform-wide administration |
| WebSocket | `WS /ws` | Real-time events, authenticated |
| Webhooks | `POST /webhooks/{provider}` | Payment callbacks |

#### Service Boundaries

| Service | Owns | Communicates With |
|---------|------|-------------------|
| **Auth Service** | JWT tokens, sessions, password reset | All services (via dependency injection) |
| **Gym Service** | Gym profiles, spaces, settings | Staff Service |
| **Membership Service** | Plans, active memberships, benefits | Booking Service, Payment Service |
| **Booking Service** | Bookings, check-ins, cancellations | Waitlist, Notification, Payment |
| **Waitlist Service** | Waitlist queue, spot offers | Booking, Notification |
| **Marketplace Service** | Subscriptions, class discovery | Booking, Payment |
| **Payment Service** | Payment abstraction, transactions | External gateways (Ozow, PayFast) |
| **Notification Service** | Multi-channel dispatch | Email, Push, WhatsApp providers |
| **Report Service** | Analytics, aggregations | Read-only access to all data |

#### Data Boundaries (Multi-Tenant Isolation)

| Domain | Tables | Isolation Level |
|--------|--------|-----------------|
| **Platform** | `consumers`, `marketplace_subscriptions` | Shared (platform-owned) |
| **Gym-Scoped** | `gyms`, `spaces`, `staff`, `classes`, `class_sessions`, `membership_plans` | Strict tenant isolation |
| **Cross-Tenant** | `bookings`, `memberships`, `payments` | Consumer + Gym access |
| **Audit** | `audit_logs` | Platform admin only |

### Requirements to Structure Mapping

#### Backend Mapping (FR → Module)

| FR Category | Route Module | Service | Repository |
|-------------|--------------|---------|------------|
| FR1-FR6 (Auth) | `auth.py` | `auth_service.py` | — |
| FR7-FR13 (Gym Mgmt) | `gyms.py` | `gym_service.py` | `gym_repository.py` |
| FR14-FR20 (Consumer/Membership) | `memberships.py` | `membership_service.py` | `membership_repository.py` |
| FR21-FR26 (Staff) | `staff.py` | — | — |
| FR27-FR30 (Spaces) | `spaces.py` | — | — |
| FR31-FR38 (Classes) | `sessions.py` | `booking_service.py` | `session_repository.py` |
| FR39-FR48 (Bookings) | `bookings.py` | `booking_service.py` | `booking_repository.py` |
| FR49-FR56 (Marketplace) | `marketplace.py` | `marketplace_service.py` | — |
| FR57-FR62 (Payments) | `payments.py` | `payment_service.py` | — |
| FR63-FR69 (Notifications) | `notifications.py` | `notification_service.py` | — |
| FR70-FR76 (Reports) | `reports.py` | `report_service.py` | — |
| FR83-FR85 (Real-time) | `websocket/` | — | — |

#### Frontend Mapping (FR → Screens)

| FR Category | Gym Web | Consumer Web | Consumer Mobile | Gym Mobile |
|-------------|---------|--------------|-----------------|------------|
| Auth | `routes/auth/*` | `routes/auth/*` | `(auth)/*` | `(auth)/*` |
| Dashboard | `routes/dashboard/*` | — | — | `(tabs)/dashboard.tsx` |
| Home/Bookings | — | `routes/home/*` | `(tabs)/home.tsx` | — |
| Discovery | — | `routes/discover/*` | `(tabs)/discover.tsx` | — |
| Class Detail | `routes/schedule/*` | `routes/discover/ClassDetail.tsx` | `class/[session_id].tsx` | `class/[session_id].tsx` |
| Memberships | `routes/settings/MembershipPlans.tsx` | `routes/memberships/*` | `(tabs)/memberships.tsx` | — |
| QR Display | — | `routes/qr-code/*` | `qr-code.tsx` | — |
| QR Scanner | — | — | — | `(tabs)/check-in.tsx` |
| Manual Check-in | `routes/check-in/*` | — | — | — |
| Schedule | `routes/schedule/*` | — | — | `(tabs)/schedule.tsx` |
| Members | `routes/members/*` | — | — | `(tabs)/members.tsx` |
| Reports | `routes/reports/*` | — | — | `reports/*` |
| Settings | `routes/settings/*` | `routes/profile/*` | `(tabs)/profile.tsx` | `settings/*` |

### Integration Points

#### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Apps                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │ Consumer App  │  │   Gym App     │  │   Web App     │        │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘        │
│          │                  │                  │                 │
│          └──────────────────┼──────────────────┘                 │
│                             │                                    │
│                    ┌────────┴────────┐                          │
│                    │  @sl/api-client │  (packages/api-client)   │
│                    │  TanStack Query │                          │
│                    └────────┬────────┘                          │
└─────────────────────────────┼───────────────────────────────────┘
                              │ HTTPS / WSS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API Layer                             │    │
│  │  /auth  /gyms  /bookings  /marketplace  /ws  /webhooks  │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────┴───────────────────────────────┐    │
│  │                  Service Layer                           │    │
│  │  AuthService  BookingService  MarketplaceService  ...   │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────┴───────────────────────────────┐    │
│  │                Repository Layer                          │    │
│  │  GymRepo  ConsumerRepo  BookingRepo  SessionRepo  ...   │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────┴───────────────────────────────┐    │
│  │              PostgreSQL + Redis                          │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌─────────┐    ┌─────────┐    ┌─────────────┐
        │  Ozow   │    │ PayFast │    │  WhatsApp   │
        │  API    │    │  API    │    │ Business API│
        └─────────┘    └─────────┘    └─────────────┘
```

#### External Integration Points

| Integration | Location | Authentication |
|-------------|----------|----------------|
| Ozow | `services/payment_service.py` | API Key + Signature |
| PayFast | `services/payment_service.py` | Merchant ID + Passphrase |
| WhatsApp Business | `workers/notification_worker.py` | Access Token |
| SendGrid | `workers/notification_worker.py` | API Key |
| Firebase Cloud Messaging | `workers/notification_worker.py` | Service Account |
| Apple Push Notification | EAS Build config | APNs Key |

### Development Workflow

#### Local Development

```bash
# Start infrastructure
docker-compose up -d  # Postgres + Redis

# Backend
cd backend
uv sync               # Install dependencies
uv run alembic upgrade head  # Run migrations
uv run uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
pnpm install
pnpm dev              # Starts all apps via Turborepo
```

#### Build & Deploy

```bash
# Backend (Fly.io)
cd backend
fly deploy

# Mobile (EAS Build)
cd frontend/apps/consumer-mobile
eas build --platform all

# Web (Vercel/Fly.io)
cd frontend/apps/web
pnpm build
```

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

| Decision A | Decision B | Status |
|------------|------------|--------|
| FastAPI (Python) | PostgreSQL + SQLModel | ✅ Native async support |
| React Native/Expo | TypeScript monorepo | ✅ Standard pattern |
| NativeWind | Tailwind CSS | ✅ Same utility classes |
| TanStack Query | Hey API codegen | ✅ Generates Query hooks |
| JWT auth | MMKV storage | ✅ Secure token persistence |
| WebSocket | Redis pub/sub | ✅ Scalable real-time |
| Fly.io JNB | POPIA compliance | ✅ SA data residency |

**Pattern Consistency:**
- ✅ snake_case in API/DB aligns with Python conventions
- ✅ camelCase in TypeScript aligns with JS ecosystem
- ✅ File naming patterns consistent across apps
- ✅ Error response format used by all API routes

**Structure Alignment:**
- ✅ Backend structure follows FastAPI best practices (routes → services → repositories)
- ✅ Frontend monorepo enables code sharing via packages
- ✅ Test locations follow co-location pattern (mobile) + separate directory (backend)

### Requirements Coverage Validation ✅

**Functional Requirements (85 FRs):**

| FR Category | Count | Backend Coverage | Frontend Coverage |
|-------------|-------|------------------|-------------------|
| FR1-FR6 (Auth) | 6 | `auth.py` + `auth_service.py` | All apps: `(auth)/*` |
| FR7-FR13 (Gym Mgmt) | 7 | `gyms.py` + `gym_service.py` | Gym app: `settings/*` |
| FR14-FR20 (Consumer) | 7 | `memberships.py` | Consumer: `(tabs)/memberships` |
| FR21-FR26 (Staff) | 6 | `staff.py` | Gym app: `settings/staff` |
| FR27-FR30 (Spaces) | 4 | `spaces.py` | Gym app: `settings/spaces` |
| FR31-FR38 (Classes) | 8 | `sessions.py` | Schedule screens |
| FR39-FR48 (Bookings) | 10 | `bookings.py` | Home, class detail screens |
| FR49-FR56 (Marketplace) | 8 | `marketplace.py` | Discover screens |
| FR57-FR62 (Payments) | 6 | `payments.py` | Checkout flows |
| FR63-FR69 (Notifications) | 7 | `notification_worker.py` | Push/toast handlers |
| FR70-FR76 (Reports) | 7 | `reports.py` | Gym app: `reports/*` |
| FR77-FR82 (Admin) | 6 | `admin.py` | Web admin section |
| FR83-FR85 (Real-time) | 3 | `websocket/*` | All apps via hooks |

**All 85 FRs have architectural support.** ✅

**Non-Functional Requirements (38 NFRs):**

| NFR Category | Requirements | Architectural Support |
|--------------|--------------|----------------------|
| **Performance** | <200ms API, <1s WS, <2s QR | ✅ Async FastAPI, Redis caching, Fly.io JNB |
| **Security** | AES-256, TLS 1.2+, JWT <24h | ✅ PostgreSQL encryption, HTTPS, token rotation |
| **Scalability** | 5K concurrent, 10K WS, 100 bookings/min | ✅ Fly.io scaling, Redis pub/sub, optimistic locking |
| **Reliability** | 99.5% uptime, offline QR, <4hr RTO | ✅ Fly.io SLA, Expo SQLite, Postgres backups |
| **Compliance** | POPIA, data residency, consent | ✅ Fly.io Johannesburg, audit logs |

**All 38 NFRs have architectural support.** ✅

### Implementation Readiness Validation ✅

**Decision Completeness:**
- ✅ All critical tech decisions documented with specific versions/tools
- ✅ Auth strategy fully specified (JWT, Argon2, role claims)
- ✅ Payment gateway strategy defined (Ozow primary, PayFast secondary)
- ✅ Hosting decision finalized (Fly.io Johannesburg)

**Structure Completeness:**
- ✅ 100+ files/directories explicitly defined in project tree
- ✅ Backend: routes, services, repositories, models, schemas, workers
- ✅ Frontend: apps (3), packages (3), all screens mapped
- ✅ Integration points documented with auth methods

**Pattern Completeness:**
- ✅ Naming conventions cover DB, API, code, files
- ✅ API response formats with examples
- ✅ Error handling patterns for frontend and backend
- ✅ Offline sync pattern with conflict resolution
- ✅ Anti-patterns documented to prevent mistakes

### Gap Analysis Results

**Critical Gaps:** None identified ✅

**Important Gaps (Non-blocking, address during implementation):**

| Gap | Impact | Resolution |
|-----|--------|------------|
| Database indexes not specified | Performance at scale | Define in migration files as needed |
| Rate limiting specifics | API protection | Configure in FastAPI middleware |
| CI/CD workflow details | Deployment automation | Expand GitHub Actions during Epic 0 |

**Nice-to-Have (Post-MVP):**

| Gap | Notes |
|-----|-------|
| Load testing strategy | Add k6/Locust tests after MVP |
| Feature flags system | Add LaunchDarkly or custom solution later |
| Analytics/observability | Expand beyond Sentry post-launch |

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed (85 FRs, 38 NFRs)
- [x] Scale and complexity assessed (Medium-High)
- [x] Technical constraints identified (POPIA, offline capability, mobile-first SA users)
- [x] Cross-cutting concerns mapped (multi-tenancy, auth, real-time, payments)

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions (FastAPI, PostgreSQL 16, Expo SDK 54)
- [x] Technology stack fully specified (Python + TypeScript)
- [x] Integration patterns defined (REST, WebSocket, webhooks)
- [x] Performance considerations addressed (caching, async, Fly.io JNB)

**✅ Implementation Patterns**
- [x] Naming conventions established (snake_case API, camelCase TS)
- [x] Structure patterns defined (feature-based backend, screen-based frontend)
- [x] Communication patterns specified (events, state management)
- [x] Process patterns documented (error handling, loading, offline sync)

**✅ Project Structure**
- [x] Complete directory structure defined (100+ files)
- [x] Component boundaries established (services, repositories, packages)
- [x] Integration points mapped (external APIs, data flow)
- [x] Requirements to structure mapping complete (FR → modules → screens)

### Architecture Readiness Assessment

**Overall Status:** ✅ READY FOR IMPLEMENTATION

**Confidence Level:** HIGH

**Key Strengths:**
1. **SA-optimized** — Fly.io Johannesburg for POPIA, Ozow for payments, WhatsApp for notifications
2. **Web-first validation** — Build and validate features on web before mobile investment
3. **Code sharing** — Monorepo enables 60%+ shared code across 4 frontend apps
4. **Type safety** — End-to-end TypeScript with generated API client
5. **Scalable foundation** — Clear path from MVP (single Fly machine) to scale (AWS)

**Areas for Future Enhancement:**
- Rate limiting configuration (implement during auth epic)
- Advanced analytics beyond basic reports (post-MVP)
- Feature flag system for gradual rollouts (post-launch)
- Load testing suite (pre-production)

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and boundaries
- Refer to this document for all architectural questions

**First Implementation Priority:**
1. Initialize backend with FastAPI template
2. Initialize frontend monorepo with Turborepo + pnpm
3. Set up CI/CD pipelines
4. Deploy infrastructure to Fly.io Johannesburg
5. Build Gym Management Web (validate gym features)
6. Build Consumer Web (validate consumer features)
7. Build Consumer Mobile (port validated features)
8. Build Gym Management Mobile (add QR scanner)

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2026-01-21
**Document Location:** `_bmad-output/planning-artifacts/architecture.md`

### Final Architecture Deliverables

**Complete Architecture Document**
- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**Implementation Ready Foundation**
- 30+ architectural decisions made
- 25+ implementation patterns defined
- 5 major components specified (Backend, Gym Web, Consumer Web, Consumer Mobile, Gym Mobile)
- 85 functional requirements + 38 non-functional requirements fully supported

**AI Agent Implementation Guide**
- Technology stack with verified versions
- Consistency rules that prevent implementation conflicts
- Project structure with clear boundaries
- Integration patterns and communication standards

### Quality Assurance Checklist

**✅ Architecture Coherence**
- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**
- [x] All functional requirements are supported
- [x] All non-functional requirements are addressed
- [x] Cross-cutting concerns are handled
- [x] Integration points are defined

**✅ Implementation Readiness**
- [x] Decisions are specific and actionable
- [x] Patterns prevent agent conflicts
- [x] Structure is complete and unambiguous
- [x] Examples are provided for clarity

### Project Success Factors

**Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction.

**Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly.

**Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs to technical implementation.

**Solid Foundation**
The chosen starter template and architectural patterns provide a production-ready foundation following current best practices.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation.
