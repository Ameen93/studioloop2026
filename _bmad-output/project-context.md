---
project_name: 'studioloop'
user_name: 'Ameen'
date: '2026-01-21'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Backend
- **Python**: 3.11+ (async/await throughout)
- **FastAPI**: Latest (async routes required)
- **PostgreSQL**: 17 (local via Docker, production on Fly.io)
- **SQLModel**: Latest (async mode)
- **Redis**: 7 (local via Docker, production on Fly.io)
- **Alembic**: Latest (migrations)
- **Pydantic**: v2 (validation)

### Frontend
- **TypeScript**: 5.x (strict mode required)
- **React Native**: Latest with Expo SDK 54
- **React**: 19 (web app)
- **TanStack Query**: v5 (server state ONLY)
- **Zustand**: Latest (client state ONLY)
- **NativeWind**: v4 (mobile styling)
- **Tailwind CSS**: v4 (web styling)

### Tooling
- **Turborepo**: Monorepo orchestration
- **pnpm**: Package manager (NOT npm/yarn)
- **Hey API**: OpenAPI client generation
- **Expo Router**: File-based navigation

---

## Critical Implementation Rules

### API & Database Naming (CRITICAL)
- ALL API endpoints use `snake_case`: `/class_sessions`, NOT `/classSessions`
- ALL request/response JSON uses `snake_case`: `{ "gym_id": "..." }`
- ALL database tables use `snake_case` plural: `class_sessions`, `membership_plans`
- ALL database columns use `snake_case`: `created_at`, `gym_id`
- UUIDs for ALL primary keys (never auto-increment integers)

### TypeScript Naming
- Variables/functions: `camelCase` — `getGymById`, `consumerId`
- Components/Types: `PascalCase` — `GymCard`, `BookingResponse`
- Constants: `SCREAMING_SNAKE` — `MAX_RETRY_ATTEMPTS`
- Files: Components `PascalCase.tsx`, utils `camelCase.ts`

### Multi-Tenancy (CRITICAL)
- Gym data is STRICTLY isolated — never leak across tenants
- Consumer profiles are SHARED (platform-owned identity)
- Every gym-scoped query MUST include `gym_id` filter
- Row-level security on all gym tables

### State Management Split (CRITICAL)
- TanStack Query: ALL server/API state
- Zustand: ONLY client-side state (UI preferences, local flags)
- NEVER duplicate server state in Zustand
- NEVER use Zustand for data that comes from API

### Offline-First Patterns
- QR check-in MUST work offline (Expo SQLite queue)
- Pending bookings stored in SQLite, synced on reconnect
- Server wins for booking conflicts
- Auth tokens in MMKV (NOT AsyncStorage)

### Error Response Format
All API errors MUST use this structure:
```json
{
  "error": {
    "code": "BOOKING_CONFLICT",
    "message": "Human readable message",
    "details": { "field": "value" }
  }
}
```

### Date/Time Handling
- API: ISO 8601 with timezone — `2026-01-21T10:00:00Z`
- Database: `timestamptz` (stored as UTC)
- Display (SA): `DD MMM YYYY, HH:mm` — `21 Jan 2026, 10:00`

---

## Testing Rules

- Unit tests: Co-located as `*.test.ts` or `*.test.tsx`
- Integration tests: `tests/` directory
- Backend: pytest with async support
- Frontend: Jest + React Testing Library
- E2E mobile: Detox (when needed)

---

## Code Organization

### Backend Structure
```
app/
├── api/routes/     # Route handlers (thin, delegate to services)
├── services/       # Business logic
├── repositories/   # Data access (SQLModel queries)
├── models/         # SQLModel database models
├── schemas/        # Pydantic request/response schemas
└── workers/        # Background tasks
```

### Frontend Structure
```
src/
├── app/           # Expo Router screens (mobile) or routes/ (web)
├── components/    # Screen-specific components
├── hooks/         # Custom hooks
└── stores/        # Zustand stores (client state only)
```

### Shared Packages
- `packages/api-client`: Generated API client + TanStack Query hooks
- `packages/ui`: Shared UI components (NativeWind/Tailwind)
- `packages/utils`: Shared utilities (formatting, validation)

---

## Anti-Patterns to AVOID

| DO NOT | DO THIS INSTEAD |
|--------|-----------------|
| `userId` in API response | `user_id` |
| `Users` table name | `users` |
| Spinners for content loading | Skeleton components |
| `GET /user` (singular) | `GET /users` (plural) |
| Store API data in Zustand | Use TanStack Query |
| Use AsyncStorage | Use MMKV for KV, SQLite for relational |
| Direct console.log in prod | Use structured logging |
| Skip gym_id in queries | ALWAYS filter by tenant |
| Wrapper objects for simple responses | Direct data response |
| `createdAt` in database | `created_at` |

---

## Local Development Setup

```bash
# Start local services (Postgres + Redis + Adminer)
docker compose -f docker-compose.local.yml up -d

# Stop local services
docker compose -f docker-compose.local.yml down

# Access Adminer (DB UI)
http://localhost:8080
```

**Local Service Ports:**
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Adminer: `localhost:8080`

---

## SA-Specific Rules

- **POPIA compliance**: All user data deletable, consent tracked
- **Hosting (Production)**: Fly.io Johannesburg (`jnb`) for data residency
- **Payments**: Ozow (primary), PayFast (secondary)
- **Notifications**: WhatsApp Business API preferred
- **Phone validation**: SA format (+27...)
- **Currency**: ZAR formatting (R 1,234.56)

---

## Quick Reference

### API Response Patterns

**Success (single item):**
```json
{ "id": "uuid", "name": "string", "created_at": "2026-01-21T10:00:00Z" }
```

**Success (list with pagination):**
```json
{
  "data": [...],
  "pagination": { "page": 1, "per_page": 20, "total": 150, "total_pages": 8 }
}
```

**Error:**
```json
{ "error": { "code": "ERROR_CODE", "message": "Human message", "details": {} } }
```

### WebSocket Events
- Naming: `{domain}.{action}` — `session.spots_updated`, `booking.confirmed`
- Payload: `{ "event": "...", "data": { ... }, "timestamp": "..." }`

### Zustand Store Pattern
```typescript
const useBookingStore = create<BookingStore>((set) => ({
  pendingBookings: [],
  addPendingBooking: (booking) => set(...),
  clearPendingBookings: () => set(...),
}));
```

---

_Last updated: 2026-01-22_
_Source: architecture.md, local-first development strategy_
