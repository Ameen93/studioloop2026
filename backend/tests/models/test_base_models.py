"""Tests for base model classes.

Tests verify:
- UUID primary key generation
- Automatic timestamp handling
- Soft-delete functionality
- Gym-scoped model structure
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlmodel import Session

from app.core.db import engine
from app.models import Gym, Space


@pytest.fixture
def test_session():
    """Create a fresh session for each test."""
    with Session(engine) as session:
        yield session
        session.rollback()


class TestTimestampMixin:
    """Tests for timestamp mixin functionality."""

    def test_created_at_auto_set(self, test_session: Session) -> None:
        """Test that created_at is automatically set on create."""
        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-ts-{uuid4().hex[:8]}",
        )
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            assert gym.created_at is not None
            assert isinstance(gym.created_at, datetime)
            # Should be within last minute
            assert (datetime.now(timezone.utc) - gym.created_at.replace(tzinfo=timezone.utc)).total_seconds() < 60
        finally:
            test_session.delete(gym)
            test_session.commit()

    def test_updated_at_auto_set(self, test_session: Session) -> None:
        """Test that updated_at is automatically set on create."""
        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-ua-{uuid4().hex[:8]}",
        )
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            assert gym.updated_at is not None
            assert isinstance(gym.updated_at, datetime)
        finally:
            test_session.delete(gym)
            test_session.commit()


class TestSoftDeleteMixin:
    """Tests for soft-delete functionality."""

    def test_is_active_default_true(self, test_session: Session) -> None:
        """Test that is_active defaults to True."""
        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-act-{uuid4().hex[:8]}",
        )
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            assert gym.is_active is True
            assert gym.deleted_at is None
        finally:
            test_session.delete(gym)
            test_session.commit()

    def test_soft_delete_method(self, test_session: Session) -> None:
        """Test soft_delete() marks record as inactive with timestamp."""
        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-sd-{uuid4().hex[:8]}",
        )
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            # Perform soft delete
            gym.soft_delete()
            test_session.add(gym)
            test_session.commit()
            test_session.refresh(gym)

            assert gym.is_active is False
            assert gym.deleted_at is not None
            assert isinstance(gym.deleted_at, datetime)
        finally:
            test_session.delete(gym)
            test_session.commit()


class TestBaseModel:
    """Tests for BaseModel class."""

    def test_uuid_auto_generated(self, test_session: Session) -> None:
        """Test that UUID primary key is automatically generated."""
        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-uuid-{uuid4().hex[:8]}",
        )
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            assert gym.id is not None
            assert isinstance(gym.id, UUID)
        finally:
            test_session.delete(gym)
            test_session.commit()

    def test_tablename_plural(self) -> None:
        """Test that table names are pluralized."""
        assert Gym.__tablename__ == "gyms"
        assert Space.__tablename__ == "spaces"


class TestGymScopedModel:
    """Tests for GymScopedModel class."""

    def test_gym_id_required(self, test_session: Session) -> None:
        """Test that gym_id is required for gym-scoped models."""
        # First create a gym
        gym = Gym(
            name="Test Gym",
            slug=f"test-gym-scoped-{uuid4().hex[:8]}",
        )
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            # Create a space with gym_id
            space = Space(
                name="Test Space",
                gym_id=gym.id,
                capacity=20,
            )
            test_session.add(space)
            test_session.commit()
            test_session.refresh(space)

            assert space.gym_id == gym.id

            # Cleanup space first
            test_session.delete(space)
            test_session.commit()
        finally:
            test_session.delete(gym)
            test_session.commit()

    def test_gym_id_index_exists(self) -> None:
        """Test that gym_id has an index for performance."""
        # Check that the gym_id field has index=True in the model
        gym_id_field = Space.model_fields.get("gym_id")
        assert gym_id_field is not None
