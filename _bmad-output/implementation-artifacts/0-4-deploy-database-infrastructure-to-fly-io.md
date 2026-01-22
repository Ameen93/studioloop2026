# Story 0.4: Deploy Database Infrastructure to Fly.io

Status: ready-for-dev

## Story

As a **developer**,
I want PostgreSQL 16 and Redis deployed to Fly.io Johannesburg,
So that we have POPIA-compliant data residency.

## Acceptance Criteria

1. **Given** a Fly.io account and CLI installed
   **When** I deploy database infrastructure
   **Then** PostgreSQL 16 with PostGIS is running in `jnb` region via Fly Postgres

2. **Given** PostgreSQL is deployed
   **When** I check the Redis deployment
   **Then** Redis is running on a Fly.io machine in `jnb` region

3. **Given** both databases are deployed
   **When** I check the secrets configuration
   **Then** connection strings are stored in Fly secrets

4. **Given** the backend application exists
   **When** I test database connectivity
   **Then** backend can connect to both PostgreSQL and Redis

5. **Given** PostgreSQL is running
   **When** I check SSL configuration
   **Then** database accepts connections with SSL enabled

6. **Given** all infrastructure is deployed
   **When** I check the backend deployment configuration
   **Then** `fly.toml` is configured for the backend deployment

## Tasks / Subtasks

- [ ] Task 1: Set up Fly.io CLI and authenticate (AC: #1)
  - [ ] 1.1 Install flyctl CLI if not already installed
  - [ ] 1.2 Authenticate with `fly auth login`
  - [ ] 1.3 Verify organization access and create studioloop org if needed

- [ ] Task 2: Deploy PostgreSQL 16 to Fly.io Johannesburg (AC: #1, #5)
  - [ ] 2.1 Create Fly Postgres cluster with `fly postgres create --name studioloop-db --region jnb`
  - [ ] 2.2 Select Development config for MVP (1x shared CPU, 256MB RAM, 1GB disk)
  - [ ] 2.3 Store generated password securely
  - [ ] 2.4 Verify PostgreSQL is running with `fly postgres connect -a studioloop-db`
  - [ ] 2.5 Enable PostGIS extension: `CREATE EXTENSION IF NOT EXISTS postgis;`
  - [ ] 2.6 Verify SSL is enabled on connections

- [ ] Task 3: Deploy self-hosted Redis to Fly.io Johannesburg (AC: #2)
  - [ ] 3.1 Create Redis volume: `fly volume create redis_data --region jnb --size 1 -a studioloop-redis`
  - [ ] 3.2 Create fly.toml for Redis deployment
  - [ ] 3.3 Set Redis password secret: `fly secrets set REDIS_PASSWORD=<generated>`
  - [ ] 3.4 Deploy Redis with `fly deploy -a studioloop-redis`
  - [ ] 3.5 Verify Redis is running and accessible via internal network

- [ ] Task 4: Configure backend fly.toml (AC: #6)
  - [ ] 4.1 Create `backend/fly.toml` with app name `studioloop-api`
  - [ ] 4.2 Configure primary region as `jnb`
  - [ ] 4.3 Set up health check endpoint
  - [ ] 4.4 Configure HTTP service with port 8000
  - [ ] 4.5 Add environment variables section

- [ ] Task 5: Store connection secrets in Fly.io (AC: #3)
  - [ ] 5.1 Attach Postgres to backend app: `fly postgres attach studioloop-db -a studioloop-api`
  - [ ] 5.2 Set REDIS_URL secret for backend: `fly secrets set REDIS_URL=redis://:password@studioloop-redis.internal:6379`
  - [ ] 5.3 Verify secrets are set: `fly secrets list -a studioloop-api`

- [ ] Task 6: Update backend configuration for Fly.io (AC: #4)
  - [ ] 6.1 Update `backend/app/core/config.py` to read DATABASE_URL from env
  - [ ] 6.2 Update `backend/app/core/config.py` to read REDIS_URL from env
  - [ ] 6.3 Ensure SSL mode is configured for PostgreSQL connection
  - [ ] 6.4 Update `backend/app/core/database.py` for async connection
  - [ ] 6.5 Update `backend/app/core/redis.py` for Redis client setup

- [ ] Task 7: Test database connectivity (AC: #4)
  - [ ] 7.1 Deploy backend to Fly.io: `fly deploy -a studioloop-api`
  - [ ] 7.2 Verify PostgreSQL connection via application logs
  - [ ] 7.3 Verify Redis connection via application logs
  - [ ] 7.4 Run health check endpoint to confirm connectivity

## Dev Notes

### Previous Story Intelligence

From Story 0.3 (done):
- Frontend monorepo fully configured with NativeWind + Tailwind
- All UI primitives created (Button, Input, Card, Modal)
- TypeScript strict mode working across all packages
- pnpm workspaces with Turborepo operational

From Story 0.2 (review):
- Frontend monorepo at `frontend/` with Turborepo + pnpm
- Apps: `@sl/consumer-mobile`, `@sl/gym-mobile`, `@sl/web`
- Packages: `@sl/api-client`, `@sl/ui`, `@sl/utils`

From Story 0.1 (review):
- Backend initialized from FastAPI Full Stack Template
- Backend structure at `backend/`
- Uses SQLModel async, Alembic for migrations
- Pydantic v2 for validation

**Current Backend State:**
- FastAPI template initialized
- Basic structure in place
- Database configuration needs updating for Fly.io
- No deployment configuration exists yet

### Critical Architecture Requirements

**From ARCH-3 (Hosting):**
- Deploy to Fly.io Johannesburg (`jnb`) region for POPIA data residency compliance
- All user data MUST remain in South Africa

**From ARCH-4 (Database):**
- PostgreSQL 16 with PostGIS on Fly Postgres (Johannesburg)
- SQLModel async ORM
- UUIDs for ALL primary keys

**From ARCH-5 (Caching):**
- Redis self-hosted on Fly.io for sessions, real-time pub/sub, booking locks
- NOT Upstash (managed) - self-hosted for cost control and data residency

**From project-context.md:**
- Database tables use `snake_case` plural: `class_sessions`, `membership_plans`
- Database columns use `snake_case`: `created_at`, `gym_id`
- All timestamps use `timestamptz` (stored as UTC)

### Fly.io Deployment Details

**PostgreSQL Creation Command:**
```bash
fly postgres create \
  --name studioloop-db \
  --region jnb \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1
```

**Self-Hosted Redis fly.toml:**
```toml
app = "studioloop-redis"
primary_region = "jnb"

[build]
  image = "redis:7-alpine"

[mounts]
  source = "redis_data"
  destination = "/data"

[env]
  REDIS_ARGS = "--requirepass ${REDIS_PASSWORD} --appendonly yes"

[[services]]
  internal_port = 6379
  protocol = "tcp"

  [[services.ports]]
    port = 6379
```

**Backend fly.toml:**
```toml
app = "studioloop-api"
primary_region = "jnb"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  ENVIRONMENT = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0

[[http_service.checks]]
  interval = "30s"
  timeout = "5s"
  grace_period = "10s"
  method = "GET"
  path = "/health"
```

### Database Connection String Format

**PostgreSQL (from Fly attach):**
```
postgresql://postgres:<password>@studioloop-db.internal:5432/studioloop?sslmode=require
```

**Redis (internal network):**
```
redis://:<password>@studioloop-redis.internal:6379
```

### Backend Configuration Updates

**backend/app/core/config.py:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://..."

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
```

**backend/app/core/database.py:**
```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### What NOT to Do

- **DO NOT** use Upstash Redis - use self-hosted Redis for POPIA compliance and cost control
- **DO NOT** deploy to any region other than `jnb` - data residency requirement
- **DO NOT** skip SSL configuration for PostgreSQL - security requirement
- **DO NOT** store database passwords in fly.toml - use `fly secrets`
- **DO NOT** use integer IDs - always use UUIDs per architecture
- **DO NOT** use camelCase in database - all columns are `snake_case`

### References

- [Source: architecture.md#Infrastructure-&-Deployment]
- [Source: architecture.md#Data-Architecture]
- [Source: project-context.md#SA-Specific-Rules]
- [Source: epics.md#Story-0.4]
- [Fly Postgres Create Docs](https://fly.io/docs/flyctl/postgres-create/)
- [Fly Redis Self-Hosted Guide](https://fly.io/docs/app-guides/redis/)
- [Fly.io Secrets Management](https://fly.io/docs/reference/secrets/)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### Change Log

| Date | Change |
|------|--------|

### File List

**Files to Create:**
- `backend/fly.toml` - Backend deployment configuration
- `infrastructure/redis/fly.toml` - Redis deployment configuration
- `infrastructure/redis/Dockerfile` - Redis Dockerfile (optional, can use image directly)

**Files to Modify:**
- `backend/app/core/config.py` - Add DATABASE_URL, REDIS_URL settings
- `backend/app/core/database.py` - Configure async engine for Fly Postgres
- `backend/app/core/redis.py` - Create Redis client setup (if not exists)
- `.env.example` - Add example environment variables

### Local Development Verification

```bash
# Install Fly CLI (if not installed)
curl -L https://fly.io/install.sh | sh

# Authenticate
fly auth login

# Deploy PostgreSQL
fly postgres create --name studioloop-db --region jnb

# Create Redis volume
fly volume create redis_data --region jnb --size 1 -a studioloop-redis

# Deploy Redis
cd infrastructure/redis && fly deploy

# Attach Postgres to backend
fly postgres attach studioloop-db -a studioloop-api

# Set Redis secret
fly secrets set REDIS_URL=redis://:password@studioloop-redis.internal:6379 -a studioloop-api

# Deploy backend
cd backend && fly deploy

# Verify health
curl https://studioloop-api.fly.dev/health
```
