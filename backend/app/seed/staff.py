"""Seed data for Staff entities.

DEFERRED: Staff model will be created in Epic 3 (Staff Management & Permissions).

This module is a placeholder that documents the planned staff seed data
structure for when the model becomes available.

Planned Staff Roles:
- Owner: Gym creator with full access to all features
- Manager: Can manage scheduling, staff, and member data
- Front Desk: Can handle check-ins and view basic member info
- Instructor: Can view/manage only their own assigned classes

Planned Seed Data:
- Each gym will get 1 owner, 1-2 managers, 1-2 front desk staff
- Some gyms will have instructors
- Staff will have realistic SA names and working hours
"""

from typing import TYPE_CHECKING

from sqlmodel import Session

if TYPE_CHECKING:
    from app.models import Gym


def seed_staff(_session: Session, _gyms: list["Gym"]) -> int:
    """Seed staff members for each gym.

    DEFERRED: Returns 0 until Staff model is created in Epic 3.

    Planned implementation:
    - Create owner for each gym
    - Create 1-2 managers per gym
    - Create 1-2 front desk staff per gym
    - Assign instructors to relevant gyms

    Args:
        session: SQLModel database session
        gyms: List of Gym objects to create staff for

    Returns:
        Number of staff members created (currently 0)
    """
    # TODO: Implement when Staff model is created in Epic 3
    # See Epic 3: Staff Management & Permissions for model definition

    return 0
