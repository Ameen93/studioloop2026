#!/usr/bin/env python3
"""Seed database with realistic test data.

Usage:
    python scripts/seed.py          # Seed data (idempotent)
    python scripts/seed.py --reset  # Clear and re-seed data

This script populates the database with South African-style realistic
test data for development and testing purposes.

It provisions accounts with publicly known passwords (staffpass123,
password123), so it refuses to run unless ENVIRONMENT=local. It used to be the
last line of scripts/prestart.sh with no guard at all, which meant every deploy
re-provisioned those accounts.
"""

import argparse
import os
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.seed import reset_seed_data, seed_all

_TRUTHY = {"1", "true", "yes", "on"}


def assert_seeding_allowed() -> None:
    """Refuse to seed anywhere but a local development environment.

    Fails loudly — a non-zero exit — rather than skipping quietly, so a
    misconfigured deploy stops instead of silently creating demo accounts.
    """
    if settings.ENVIRONMENT == "local":
        return

    opt_in_set = os.getenv("SEED_DEMO_DATA", "").strip().lower() in _TRUTHY
    lines = [
        "=" * 60,
        "REFUSING TO SEED",
        "=" * 60,
        f"ENVIRONMENT={settings.ENVIRONMENT!r}, and demo seeding is only ever",
        "allowed when ENVIRONMENT=local. This script creates accounts with",
        "publicly known passwords (staffpass123, password123).",
    ]
    if opt_in_set:
        lines += [
            "",
            "SEED_DEMO_DATA is set. It is not an override: there is no way to",
            "seed demo data into a deployed environment.",
        ]
    raise SystemExit("\n".join(lines))


def main() -> None:
    """Main entry point for seed script."""
    parser = argparse.ArgumentParser(
        description="Seed database with realistic test data"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing seed data before re-seeding",
    )
    args = parser.parse_args()

    assert_seeding_allowed()

    print("=" * 60)
    print("StudioLoop Database Seeder")
    print("=" * 60)

    with Session(engine) as session:
        if args.reset:
            print("\n[RESET MODE] Clearing existing seed data...")
            reset_seed_data(session)
            print("Seed data cleared successfully.\n")

        print("Seeding database with test data...\n")
        summary = seed_all(session)

        print("\n" + "=" * 60)
        print("SEED SUMMARY")
        print("=" * 60)
        for entity, count in summary.items():
            status = "created/found" if count > 0 else "skipped (model not ready)"
            print(f"  {entity}: {count} {status}")

        print("\n" + "=" * 60)
        print("Seeding complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()
