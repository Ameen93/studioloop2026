"""Tests for GymScopedRepository tenant isolation.

CRITICAL: These tests verify that multi-tenancy isolation is enforced.
Data from one gym should NEVER be accessible from another gym's context.
"""

from uuid import uuid4

import pytest
from sqlmodel import Session

from app.core.db import engine
from app.models import Gym, Space, SpaceCreate, SpaceUpdate
from app.repositories.base import GymScopedRepository


class SpaceRepository(GymScopedRepository[Space, SpaceCreate, SpaceUpdate]):
    """Concrete space repository for testing."""

    pass


@pytest.fixture
def test_session():
    """Create a fresh session for each test."""
    with Session(engine) as session:
        yield session
        session.rollback()


class TestGymScopedRepositoryIsolation:
    """Tests verifying tenant isolation in GymScopedRepository."""

    def test_create_sets_gym_id(self, test_session: Session) -> None:
        """Test that create() automatically sets gym_id."""
        # Create gym
        gym = Gym(name="Test Gym", slug=f"gym-create-{uuid4().hex[:8]}")
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            repo = SpaceRepository(Space, test_session, gym_id=gym.id)
            space_data = SpaceCreate(name="Main Studio", capacity=30)
            space = repo.create(obj_in=space_data)

            assert space.gym_id == gym.id
            assert space.name == "Main Studio"
        finally:
            # Cleanup: delete space first, then gym
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id == gym.id)
            )
            test_session.delete(gym)
            test_session.commit()

    def test_get_filters_by_gym_id(self, test_session: Session) -> None:
        """Test that get() only returns records from current gym."""
        # Create two gyms
        gym_a = Gym(name="Gym A", slug=f"gym-a-{uuid4().hex[:8]}")
        gym_b = Gym(name="Gym B", slug=f"gym-b-{uuid4().hex[:8]}")
        test_session.add_all([gym_a, gym_b])
        test_session.commit()
        test_session.refresh(gym_a)
        test_session.refresh(gym_b)

        try:
            # Create space in gym_a
            space = Space(name="Gym A Space", gym_id=gym_a.id, capacity=20)
            test_session.add(space)
            test_session.commit()
            test_session.refresh(space)

            # Try to access from gym_b context - should return None
            repo_b = SpaceRepository(Space, test_session, gym_id=gym_b.id)
            result = repo_b.get(space.id)
            assert result is None, "SECURITY: Cross-tenant access should be denied"

            # Access from gym_a context - should work
            repo_a = SpaceRepository(Space, test_session, gym_id=gym_a.id)
            result = repo_a.get(space.id)
            assert result is not None
            assert result.id == space.id
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id.in_([gym_a.id, gym_b.id]))
            )
            test_session.delete(gym_a)
            test_session.delete(gym_b)
            test_session.commit()

    def test_get_multi_filters_by_gym_id(self, test_session: Session) -> None:
        """Test that get_multi() only returns records from current gym."""
        # Create two gyms
        gym_a = Gym(name="Gym A", slug=f"gym-multi-a-{uuid4().hex[:8]}")
        gym_b = Gym(name="Gym B", slug=f"gym-multi-b-{uuid4().hex[:8]}")
        test_session.add_all([gym_a, gym_b])
        test_session.commit()
        test_session.refresh(gym_a)
        test_session.refresh(gym_b)

        try:
            # Create spaces in both gyms
            space_a = Space(name="Gym A Space", gym_id=gym_a.id, capacity=20)
            space_b = Space(name="Gym B Space", gym_id=gym_b.id, capacity=25)
            test_session.add_all([space_a, space_b])
            test_session.commit()

            # Get from gym_a context
            repo_a = SpaceRepository(Space, test_session, gym_id=gym_a.id)
            spaces_a = repo_a.get_multi()

            # Should only see gym_a's space
            assert len(spaces_a) >= 1
            for space in spaces_a:
                assert space.gym_id == gym_a.id, "SECURITY: Cross-tenant data leaked"

            # Get from gym_b context
            repo_b = SpaceRepository(Space, test_session, gym_id=gym_b.id)
            spaces_b = repo_b.get_multi()

            # Should only see gym_b's space
            assert len(spaces_b) >= 1
            for space in spaces_b:
                assert space.gym_id == gym_b.id, "SECURITY: Cross-tenant data leaked"
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id.in_([gym_a.id, gym_b.id]))
            )
            test_session.delete(gym_a)
            test_session.delete(gym_b)
            test_session.commit()

    def test_delete_prevents_cross_tenant(self, test_session: Session) -> None:
        """Test that delete() cannot delete records from other gyms."""
        # Create two gyms
        gym_a = Gym(name="Gym A", slug=f"gym-del-a-{uuid4().hex[:8]}")
        gym_b = Gym(name="Gym B", slug=f"gym-del-b-{uuid4().hex[:8]}")
        test_session.add_all([gym_a, gym_b])
        test_session.commit()
        test_session.refresh(gym_a)
        test_session.refresh(gym_b)

        try:
            # Create space in gym_a
            space = Space(name="Gym A Space", gym_id=gym_a.id, capacity=20)
            test_session.add(space)
            test_session.commit()
            test_session.refresh(space)
            space_id = space.id

            # Try to delete from gym_b context - should fail
            repo_b = SpaceRepository(Space, test_session, gym_id=gym_b.id)
            result = repo_b.delete(id=space_id)
            assert result is None, "SECURITY: Cross-tenant delete should be denied"

            # Verify space still exists and is active
            test_session.refresh(space)
            assert space.is_active is True

            # Delete from gym_a context - should work
            repo_a = SpaceRepository(Space, test_session, gym_id=gym_a.id)
            result = repo_a.delete(id=space_id)
            assert result is not None
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id.in_([gym_a.id, gym_b.id]))
            )
            test_session.delete(gym_a)
            test_session.delete(gym_b)
            test_session.commit()

    def test_count_filters_by_gym_id(self, test_session: Session) -> None:
        """Test that count() only counts records from current gym."""
        # Create two gyms
        gym_a = Gym(name="Gym A", slug=f"gym-cnt-a-{uuid4().hex[:8]}")
        gym_b = Gym(name="Gym B", slug=f"gym-cnt-b-{uuid4().hex[:8]}")
        test_session.add_all([gym_a, gym_b])
        test_session.commit()
        test_session.refresh(gym_a)
        test_session.refresh(gym_b)

        try:
            # Create multiple spaces in gym_a
            spaces = [
                Space(name=f"Space {i}", gym_id=gym_a.id, capacity=10)
                for i in range(3)
            ]
            test_session.add_all(spaces)
            test_session.commit()

            # Count from gym_a context
            repo_a = SpaceRepository(Space, test_session, gym_id=gym_a.id)
            count_a = repo_a.count()
            assert count_a == 3

            # Count from gym_b context - should be 0
            repo_b = SpaceRepository(Space, test_session, gym_id=gym_b.id)
            count_b = repo_b.count()
            assert count_b == 0
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id.in_([gym_a.id, gym_b.id]))
            )
            test_session.delete(gym_a)
            test_session.delete(gym_b)
            test_session.commit()


class TestGymScopedRepositorySoftDelete:
    """Tests for soft-delete in GymScopedRepository."""

    def test_soft_delete_default(self, test_session: Session) -> None:
        """Test that delete() performs soft-delete by default."""
        gym = Gym(name="Test Gym", slug=f"gym-sd-{uuid4().hex[:8]}")
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            repo = SpaceRepository(Space, test_session, gym_id=gym.id)
            space = repo.create(obj_in=SpaceCreate(name="Test Space", capacity=10))
            space_id = space.id

            # Soft delete
            result = repo.delete(id=space_id)
            assert result is not None
            assert result.is_active is False
            assert result.deleted_at is not None
        finally:
            # Cleanup (hard delete)
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id == gym.id)
            )
            test_session.delete(gym)
            test_session.commit()

    def test_get_excludes_soft_deleted(self, test_session: Session) -> None:
        """Test that get() excludes soft-deleted records."""
        gym = Gym(name="Test Gym", slug=f"gym-getsd-{uuid4().hex[:8]}")
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            repo = SpaceRepository(Space, test_session, gym_id=gym.id)
            space = repo.create(obj_in=SpaceCreate(name="Test Space", capacity=10))
            space_id = space.id

            # Soft delete
            repo.delete(id=space_id)

            # get() should return None for soft-deleted record
            result = repo.get(space_id)
            assert result is None
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id == gym.id)
            )
            test_session.delete(gym)
            test_session.commit()

    def test_get_multi_excludes_soft_deleted(self, test_session: Session) -> None:
        """Test that get_multi() excludes soft-deleted records by default."""
        gym = Gym(name="Test Gym", slug=f"gym-multisd-{uuid4().hex[:8]}")
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            repo = SpaceRepository(Space, test_session, gym_id=gym.id)

            # Create two spaces
            space1 = repo.create(obj_in=SpaceCreate(name="Space 1", capacity=10))
            space2 = repo.create(obj_in=SpaceCreate(name="Space 2", capacity=10))

            # Soft delete one
            repo.delete(id=space1.id)

            # get_multi() should only return active records
            spaces = repo.get_multi()
            space_ids = [s.id for s in spaces]
            assert space1.id not in space_ids
            assert space2.id in space_ids
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id == gym.id)
            )
            test_session.delete(gym)
            test_session.commit()

    def test_get_multi_include_inactive(self, test_session: Session) -> None:
        """Test that get_multi() can include soft-deleted records."""
        gym = Gym(name="Test Gym", slug=f"gym-incl-{uuid4().hex[:8]}")
        test_session.add(gym)
        test_session.commit()
        test_session.refresh(gym)

        try:
            repo = SpaceRepository(Space, test_session, gym_id=gym.id)

            # Create and soft-delete a space
            space = repo.create(obj_in=SpaceCreate(name="Deleted Space", capacity=10))
            repo.delete(id=space.id)

            # get_multi() with include_inactive should return deleted records
            spaces = repo.get_multi(include_inactive=True)
            space_ids = [s.id for s in spaces]
            assert space.id in space_ids
        finally:
            # Cleanup
            test_session.execute(
                Space.__table__.delete().where(Space.gym_id == gym.id)
            )
            test_session.delete(gym)
            test_session.commit()
