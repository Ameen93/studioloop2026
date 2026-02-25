#!/usr/bin/env bash
# Deploy database: run migrations and/or seed data against a remote Neon DB.
#
# Usage:
#   export NEON_DATABASE_URL="postgresql+psycopg://user:pass@ep-xxx.neon.tech/neondb?sslmode=require"
#   ./scripts/deploy-db.sh migrate   # migrations only
#   ./scripts/deploy-db.sh seed      # seed only
#   ./scripts/deploy-db.sh both      # migrations + seed (default)

set -euo pipefail

if [ -z "${NEON_DATABASE_URL:-}" ]; then
  echo "Error: NEON_DATABASE_URL is not set."
  echo "Export it first: export NEON_DATABASE_URL=\"postgresql+psycopg://...\""
  exit 1
fi

ACTION="${1:-both}"
BACKEND_DIR="$(cd "$(dirname "$0")/../backend" && pwd)"

export DATABASE_URL="$NEON_DATABASE_URL"

run_migrate() {
  echo "==> Running Alembic migrations..."
  cd "$BACKEND_DIR"
  uv run alembic upgrade head
  echo "==> Migrations complete."
}

run_seed() {
  echo "==> Seeding database..."
  cd "$BACKEND_DIR"
  uv run python scripts/seed.py
  echo "==> Seed complete."
}

case "$ACTION" in
  migrate)
    run_migrate
    ;;
  seed)
    run_seed
    ;;
  both)
    run_migrate
    run_seed
    ;;
  *)
    echo "Unknown action: $ACTION"
    echo "Usage: $0 [migrate|seed|both]"
    exit 1
    ;;
esac

echo "Done!"
