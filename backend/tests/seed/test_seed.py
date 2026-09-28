"""Tests for seed data functionality.

Tests verify:
1. Idempotency: Running seed twice doesn't create duplicates
2. Reset: Reset clears all seeded data
3. Data integrity: FK relationships are valid
4. Count verification: Expected counts after seeding
"""

import pytest
from sqlmodel import Session, select

from app.core.db import engine
from app.models import Consumer, Gym, Space
from app.seed import reset_seed_data, seed_all
from app.seed.consumers import SEED_CONSUMERS
from app.seed.gyms import SEED_GYMS
from app.seed.spaces import GYM_SPACE_ASSIGNMENTS


@pytest.fixture(scope="module")
def db_session(db: Session):
    """Provide a clean database session for seed tests.

    Resets seed data before tests to ensure isolation from other test modules
    that may have created test data (e.g., RBAC tests creating test gyms).

    Takes the session-scoped `db` fixture purely to release it first. That
    session is left idle-in-transaction by any seeder that short-circuits on an
    already-populated database, or by whichever test ran last, and the ACCESS
    SHARE locks it holds block the TRUNCATE inside reset_seed_data until the
    statement times out. Without this the whole module errors on any database
    that is not freshly created — which is to say, on every second run.
    """
    db.rollback()
    with Session(engine) as session:
        # Reset to clean slate - seed tests need to verify exact counts
        reset_seed_data(session)
        yield session


class TestSeedIdempotency:
    """Tests verifying seed operations are idempotent."""

    def test_seed_gyms_idempotent(self, db_session: Session) -> None:
        """Running seed twice should not create duplicate gyms."""
        # First seed
        summary1 = seed_all(db_session)

        # Count gyms after first seed
        count1 = len(db_session.exec(select(Gym)).all())

        # Second seed
        summary2 = seed_all(db_session)

        # Count after second seed
        count2 = len(db_session.exec(select(Gym)).all())

        # Counts should be equal
        assert count1 == count2, "Seed should be idempotent - no duplicates"
        assert summary1["gyms"] == summary2["gyms"]

    def test_seed_consumers_idempotent(self, db_session: Session) -> None:
        """Running seed twice should not create duplicate consumers."""
        # Seed
        seed_all(db_session)

        # Count consumers
        count1 = len(db_session.exec(select(Consumer)).all())

        # Seed again
        seed_all(db_session)

        # Count again
        count2 = len(db_session.exec(select(Consumer)).all())

        assert count1 == count2, "Seed should be idempotent - no duplicate consumers"

    def test_seed_spaces_idempotent(self, db_session: Session) -> None:
        """Running seed twice should not create duplicate spaces."""
        # Seed
        seed_all(db_session)

        # Count spaces
        count1 = len(db_session.exec(select(Space)).all())

        # Seed again
        seed_all(db_session)

        # Count again
        count2 = len(db_session.exec(select(Space)).all())

        assert count1 == count2, "Seed should be idempotent - no duplicate spaces"


class TestSeedCounts:
    """Tests verifying expected record counts after seeding."""

    def test_gym_count_matches_seed_data(self, db_session: Session) -> None:
        """Number of gyms should match SEED_GYMS list."""
        seed_all(db_session)

        gyms = db_session.exec(select(Gym)).all()
        assert len(gyms) == len(SEED_GYMS), f"Expected {len(SEED_GYMS)} gyms"

    def test_consumer_count_matches_seed_data(self, db_session: Session) -> None:
        """Number of consumers should match SEED_CONSUMERS list."""
        seed_all(db_session)

        consumers = db_session.exec(select(Consumer)).all()
        assert len(consumers) >= len(
            SEED_CONSUMERS
        ), f"Expected at least {len(SEED_CONSUMERS)} consumers"

    def test_space_count_matches_assignments(self, db_session: Session) -> None:
        """Number of spaces should match GYM_SPACE_ASSIGNMENTS."""
        seed_all(db_session)

        expected_count = sum(len(spaces) for spaces in GYM_SPACE_ASSIGNMENTS.values())
        spaces = db_session.exec(select(Space)).all()
        assert len(spaces) == expected_count, f"Expected {expected_count} spaces"


class TestSeedDataIntegrity:
    """Tests verifying data integrity and FK relationships."""

    def test_all_spaces_have_valid_gym_id(self, db_session: Session) -> None:
        """Every space should reference a valid gym."""
        seed_all(db_session)

        spaces = db_session.exec(select(Space)).all()
        gym_ids = {g.id for g in db_session.exec(select(Gym)).all()}

        for space in spaces:
            assert space.gym_id in gym_ids, f"Space {space.name} has invalid gym_id"

    def test_test_consumer_exists(self, db_session: Session) -> None:
        """Test consumer account should exist after seeding."""
        seed_all(db_session)

        test_consumer = db_session.exec(
            select(Consumer).where(Consumer.email == "test@studioloop.com")
        ).first()

        assert test_consumer is not None, "Test consumer should exist"
        assert test_consumer.first_name == "Test"
        assert test_consumer.last_name == "User"
        assert test_consumer.is_email_verified is True

    def test_gyms_have_sa_data(self, db_session: Session) -> None:
        """Gyms should have South African location data."""
        seed_all(db_session)

        gyms = db_session.exec(select(Gym)).all()

        for gym in gyms:
            assert gym.country == "ZA", f"Gym {gym.name} should have ZA country code"
            assert gym.province is not None, f"Gym {gym.name} should have province"
            assert gym.city is not None, f"Gym {gym.name} should have city"


class TestSeedReset:
    """Tests verifying reset functionality."""

    def test_reset_clears_all_seed_data(self, db_session: Session) -> None:
        """Reset should clear all seeded entities."""
        # First seed data
        seed_all(db_session)

        # Verify data exists
        assert len(db_session.exec(select(Gym)).all()) > 0
        assert len(db_session.exec(select(Consumer)).all()) > 0
        assert len(db_session.exec(select(Space)).all()) > 0

        # Reset
        reset_seed_data(db_session)

        # Verify all cleared
        assert len(db_session.exec(select(Gym)).all()) == 0, "Gyms should be cleared"
        assert (
            len(db_session.exec(select(Consumer)).all()) == 0
        ), "Consumers should be cleared"
        assert (
            len(db_session.exec(select(Space)).all()) == 0
        ), "Spaces should be cleared"

    def test_can_reseed_after_reset(self, db_session: Session) -> None:
        """Should be able to seed again after reset."""
        # Seed
        seed_all(db_session)

        # Reset
        reset_seed_data(db_session)

        # Seed again
        summary = seed_all(db_session)

        assert summary["gyms"] == len(SEED_GYMS)
        assert summary["consumers"] == len(SEED_CONSUMERS)
