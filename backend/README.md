# StudioLoop — backend

FastAPI + SQLModel + Alembic over PostgreSQL. See the
[root README](../README.md) for what this project is, its status, and the
architecture. This file covers only backend-local workflow.

## Requirements

- [uv](https://docs.astral.sh/uv/) for Python dependencies and the virtualenv
- Python 3.12 (pinned in `../.python-version`)
- A reachable PostgreSQL — `docker compose -f ../docker-compose.local.yml up -d db`

## Setup

Configuration is read from `../.env` (the repository root, not this directory —
see `env_file` in `app/core/config.py`). Copy the template first:

```bash
cp ../.env.example ../.env
```

Then, from this directory:

```bash
uv sync --dev
uv run alembic upgrade head
uv run python scripts/seed.py          # synthetic demo data
uv run uvicorn app.main:app --reload   # http://localhost:8000/docs
```

Run every command from `backend/`. `alembic.ini` uses a relative
`script_location`, and the settings loader resolves `../.env` relative to the
working directory, so both break if you run them from the repository root.

## Tests

```bash
uv run pytest -v
```

The suite needs a running PostgreSQL. A session-scoped autouse fixture in
`tests/conftest.py` runs `alembic upgrade head` as a subprocess and then seeds
the database named in your `.env`, and it does not clean up afterwards — so
point `.env` at a throwaway database, not one you care about. No test requires
network access or third-party credentials; Stitch, Google, Apple and SMTP are
all patched.

## Lint and types

```bash
uv run ruff check app
uv run ruff format app
uv run mypy app
```

Note that `ruff` and `mypy` currently report failures on `master` — see
"Known issues" in the root README.

## Migrations

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

Read what autogenerate produces before committing it. One migration in this
history silently dropped an `ondelete='CASCADE'` because SQLModel's
`foreign_key=` does not declare it; the root README describes the incident.

`alembic upgrade head` works against an empty database. Offline SQL generation
(`alembic upgrade head --sql`) does **not**, because
`c4b7ce0c5a91_add_gym_membership_unique_constraint.py` reflects the live schema
inside `upgrade()`.

## Layout

```
app/
  api/routes/      19 route modules
  api/deps.py      auth, RBAC, gym-scope dependencies
  models/          SQLModel domain models
  models_legacy.py FastAPI-template originals, still live (User, Item)
  repositories/    GymScopedRepository — tested, used by no route
  services/        payments/ (Stitch + two in-repo fakes), notifications/
  core/            config, security, db, oauth, rate limiting
  alembic/         26 migrations, single linear chain
  seed/            synthetic demo data
tests/             34 test files, 460 tests
scripts/           prestart, seed, alembic repair helpers
```
