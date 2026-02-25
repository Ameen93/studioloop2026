from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.api.deps import get_current_gym
from app.models import Gym
from app.models.staff import Staff, StaffRole


def _create_gym(db: Session, name: str = 'Dependency Gym', is_active: bool = True) -> Gym:
    gym = Gym(
        name=name,
        slug=f'dep-gym-{uuid4().hex[:8]}',
        is_active=is_active,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym


def _create_staff_for_gym(
    db: Session,
    gym: Gym,
    is_active: bool = True,
) -> Staff:
    staff = Staff(
        email=f'staff-{uuid4().hex[:8]}@example.com',
        first_name='Dep',
        last_name='Tester',
        hashed_password='staff-password-hash',
        role=StaffRole.OWNER,
        gym_id=gym.id,
        is_active=is_active,
        is_email_verified=True,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


class TestGetCurrentGym:
    def test_allows_staff_with_matching_gym(self, db: Session) -> None:
        gym = _create_gym(db, name='Staff Gym')
        staff = _create_staff_for_gym(db, gym, is_active=True)

        result = get_current_gym(gym.id, db, staff)

        assert result.id == gym.id

    def test_denies_staff_for_other_gym(self, db: Session) -> None:
        target_gym = _create_gym(db, name='Target Gym')
        other_gym = _create_gym(db, name='Other Gym')
        staff = _create_staff_for_gym(db, other_gym, is_active=True)

        with pytest.raises(HTTPException) as exc_info:
            get_current_gym(target_gym.id, db, staff)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == 'Access denied to this gym'

    def test_denies_inactive_gym(self, db: Session) -> None:
        gym = _create_gym(db, name='Inactive Gym', is_active=False)
        staff = _create_staff_for_gym(db, _create_gym(db, name='Staff Home Gym'))

        with pytest.raises(HTTPException) as exc_info:
            get_current_gym(gym.id, db, staff)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == 'Gym not found'
