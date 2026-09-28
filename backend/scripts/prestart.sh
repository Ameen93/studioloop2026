#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py

# Demo data. scripts/seed.py provisions accounts with publicly known passwords
# (staffpass123, password123), so it must never run on a deployed environment.
# This block used to be an unconditional `python scripts/seed.py`, which meant
# every deploy re-provisioned those accounts.
#
#   ENVIRONMENT=local           -> seed
#   anything else               -> skip
#   anything else + SEED_DEMO_DATA set -> fail the deploy, loudly
#
# SEED_DEMO_DATA defaults to off and exists to make the intent explicit; it is
# never a way to seed a deployed environment. scripts/seed.py enforces the same
# rule itself, so running it by hand is guarded too.
seed_demo_data="$(printf '%s' "${SEED_DEMO_DATA:-}" | tr '[:upper:]' '[:lower:]')"
case "$seed_demo_data" in
    1|true|yes|on) seed_requested=1 ;;
    *)             seed_requested=0 ;;
esac

if [ "${ENVIRONMENT:-local}" = "local" ]; then
    python scripts/seed.py
elif [ "$seed_requested" = "1" ]; then
    set +x
    echo "FATAL: SEED_DEMO_DATA is set but ENVIRONMENT=${ENVIRONMENT:-local}." >&2
    echo "       Demo seeding provisions accounts with publicly known passwords" >&2
    echo "       and is only ever allowed when ENVIRONMENT=local. Refusing to start." >&2
    exit 1
else
    set +x
    echo "Skipping demo seed: ENVIRONMENT=${ENVIRONMENT:-local} is not local."
fi
