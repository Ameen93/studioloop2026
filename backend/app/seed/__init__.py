"""Seed data module for StudioLoop.

This module provides functions to populate the database with realistic
South African test data for development and testing purposes.

Usage:
    from app.seed import seed_all, reset_seed_data

    # Seed all data (idempotent)
    with Session(engine) as session:
        summary = seed_all(session)

    # Reset and re-seed
    with Session(engine) as session:
        reset_seed_data(session)
        summary = seed_all(session)
"""

from app.seed.orchestrator import reset_seed_data, seed_all

__all__ = ["seed_all", "reset_seed_data"]
