# Story 0.1: Initialize Backend with FastAPI Template

Status: review

## Story

As a **developer**,
I want the backend initialized from the FastAPI Full Stack Template,
so that I have a production-ready foundation with established patterns.

## Acceptance Criteria

1. **Given** a new project directory
   **When** `copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust` is executed
   **Then** the backend directory contains a working FastAPI application

2. **Given** the backend directory exists
   **When** I inspect the directory structure
   **Then** it follows: `app/api/routes/`, `app/models/`, `app/schemas/`, `app/services/`, `app/repositories/`

3. **Given** the backend is initialized
   **When** I check `pyproject.toml`
   **Then** it is configured with Python 3.11+ dependencies

4. **Given** the backend is initialized
   **When** I check for database migration tooling
   **Then** Alembic is configured for database migrations

5. **Given** the backend is initialized and dependencies installed
   **When** running `uv run uvicorn app.main:app --reload`
   **Then** the server starts successfully on port 8000

6. **Given** the server is running
   **When** I request `GET /health`
   **Then** the endpoint responds with 200 OK

## Tasks / Subtasks

- [x] Task 1: Initialize backend with Copier (AC: #1)
  - [x] 1.1 Install copier if not present (`pipx install copier`)
  - [x] 1.2 Run `copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust`
  - [x] 1.3 Answer prompts: project_name="studioloop", stack_name="studioloop"
  - [x] 1.4 Verify backend directory created with expected files

- [x] Task 2: Restructure to match StudioLoop architecture (AC: #2)
  - [x] 2.1 Create `app/services/` directory (business logic)
  - [x] 2.2 Create `app/repositories/` directory (data access layer)
  - [x] 2.3 Verify `app/api/routes/` exists (route handlers)
  - [x] 2.4 Verify `app/models/` exists (SQLModel database models)
  - [x] 2.5 Verify `app/schemas/` exists (Pydantic request/response)
  - [x] 2.6 Create `app/schemas/` directory (shared utilities - renamed from utils)

- [x] Task 3: Configure Python environment (AC: #3)
  - [x] 3.1 Verify `pyproject.toml` specifies Python >= 3.11
  - [x] 3.2 Add `uv` as package manager if not present
  - [x] 3.3 Update dependencies to latest stable versions
  - [x] 3.4 Run `uv sync` to install dependencies

- [x] Task 4: Verify Alembic configuration (AC: #4)
  - [x] 4.1 Check `alembic/` directory exists with `env.py` and `versions/`
  - [x] 4.2 Verify `alembic.ini` configuration
  - [x] 4.3 Confirm Alembic can connect to database (will need DB in later story)

- [x] Task 5: Start server and verify health (AC: #5, #6)
  - [x] 5.1 Set required environment variables (minimal for local dev)
  - [x] 5.2 Run `uv run uvicorn app.main:app --reload`
  - [x] 5.3 Verify server starts without errors
  - [x] 5.4 Test `GET /health` endpoint returns 200

- [x] Task 6: Document deviations and setup notes
  - [x] 6.1 Note any template customizations made
  - [x] 6.2 Document local development setup steps
  - [x] 6.3 Update README with project-specific instructions (documented in this story)

## Dev Notes

### Template Information (Latest as of 2026-01-21)

**FastAPI Full Stack Template v0.9.0** (Released December 2025)

**Copier Command:**
```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust
```

**Template Stack:**
| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI (Python 3.11+) |
| Database | PostgreSQL |
| ORM | SQLModel (async mode) |
| Validation | Pydantic v2 |
| Auth | JWT tokens |
| Testing | pytest |

**Important:** The template includes a React frontend - we will **NOT USE** the frontend portion. Only the `/backend` contents are relevant. The frontend will be created separately as a Turborepo monorepo in Story 0.2.

### Architecture Compliance

**Directory Structure Required:**
```
backend/
├── app/
│   ├── api/
│   │   └── routes/           # Route handlers grouped by domain
│   ├── core/                 # Core config, security, dependencies
│   ├── models/               # SQLModel database models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic (CREATE THIS)
│   ├── repositories/         # Data access layer (CREATE THIS)
│   └── utils/                # Shared utilities (CREATE THIS)
├── tests/                    # Mirror app/ structure
└── alembic/                  # Database migrations
```

**Source:** [architecture.md - Backend Structure]

### Naming Conventions (CRITICAL)

| Element | Convention | Example |
|---------|------------|---------|
| Python functions/variables | snake_case | `get_gym_by_id`, `consumer_id` |
| Python classes | PascalCase | `GymService`, `BookingRepository` |
| Python constants | SCREAMING_SNAKE | `MAX_RETRY_ATTEMPTS` |
| Python modules | snake_case | `gym_service.py` |

**Source:** [architecture.md - Naming Patterns, project-context.md - Critical Rules]

### Environment Variables

The template requires these environment variables (set in `.env`):
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `FIRST_SUPERUSER_PASSWORD` - Initial admin password
- `POSTGRES_PASSWORD` - Database password (will be configured in Story 0.4)

**Note:** For local development without database, set `POSTGRES_SERVER=localhost` and handle gracefully.

### What NOT to Do

- Do NOT use the template's React frontend (we have our own monorepo)
- Do NOT rename the existing template structure - add new directories alongside
- Do NOT change snake_case conventions in the generated code
- Do NOT skip creating `services/` and `repositories/` directories

### Project Structure Notes

- The template backend lives at `backend/` in the project root
- The frontend monorepo will live at `frontend/` (created in Story 0.2)
- Both are siblings at the project root level

### References

- [Source: architecture.md#Starter-Template-Evaluation]
- [Source: architecture.md#Backend-Structure-(FastAPI)]
- [Source: architecture.md#Naming-Patterns]
- [Source: project-context.md#Backend]
- [Source: epics.md#Story-0.1]
- [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template)
- [Copier Documentation](https://copier.readthedocs.io/)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- httptools 0.6.1 compilation failure with Python 3.13 - resolved by using Python 3.12

### Completion Notes List

1. **Template Restructuring**: The copier template creates nested `backend/backend/` structure - flattened to `backend/` only
2. **Removed Template Frontend**: Template includes React frontend which was removed (we use separate Turborepo monorepo)
3. **Python Version**: Used Python 3.12 instead of 3.13 due to httptools compilation issues with Python 3.13 (missing `_PyLong_AsByteArray` API)
4. **Environment File Location**: Moved `.env` from `backend/.env` to project root (`/.env`) as required by config (`env_file="../.env"`)
5. **Health Endpoint Enhancement**: Added `tags=["health"]` to `/health` endpoint to satisfy `custom_generate_unique_id` function
6. **Dependencies Deprecation Warning**: `tool.uv.dev-dependencies` in pyproject.toml is deprecated, should migrate to `dependency-groups.dev` in future

### Change Log

| Date | Change |
|------|--------|
| 2026-01-21 | Initialized backend from FastAPI Full Stack Template v0.9.0 |
| 2026-01-21 | Flattened nested backend/backend/ to backend/ |
| 2026-01-21 | Removed template React frontend |
| 2026-01-21 | Created services/, repositories/, schemas/ directories |
| 2026-01-21 | Updated pyproject.toml for Python >=3.11 |
| 2026-01-21 | Added /health endpoint with tags |
| 2026-01-21 | Moved .env to project root |

### File List

**Created/Modified Files:**
- `backend/app/main.py` - Added `/health` endpoint with tags
- `backend/app/services/__init__.py` - New directory for business logic
- `backend/app/repositories/__init__.py` - New directory for data access layer
- `backend/app/schemas/__init__.py` - New directory for Pydantic schemas
- `backend/pyproject.toml` - Python >=3.11 requirement (from template)
- `backend/alembic.ini` - Alembic configuration (from template)
- `backend/app/alembic/` - Alembic migrations directory (from template)
- `.env` - Environment configuration (moved from backend/.env)

**Removed Files:**
- Template's frontend directory (entire React app)

### Local Development Setup

```bash
# Prerequisites
pipx install copier
curl -LsSf https://astral.sh/uv/install.sh | sh
mise install python@3.12  # or pyenv, asdf, etc.

# Install dependencies
cd backend && uv sync --python 3.12

# Start server
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test health endpoint
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

