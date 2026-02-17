#!/usr/bin/env python3
"""Seed database with realistic test data.

Usage:
    python scripts/seed.py          # Seed data (idempotent)
    python scripts/seed.py --reset  # Clear and re-seed data

This script populates the database with South African-style realistic
test data for development and testing purposes.
"""

import argparse
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session

from app.core.db import engine
from app.seed import reset_seed_data, seed_all


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
