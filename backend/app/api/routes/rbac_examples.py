"""Example routes demonstrating role-based access control (Story 1.8).

These routes are for testing RBAC functionality and serve as patterns
for implementing protected routes in future epics.

Routes:
- /rbac/owner-only: Only owners can access
- /rbac/manager-or-above: Owners and managers can access
- /rbac/any-staff: Any staff role can access
- /rbac/gyms/{gym_id}/staff-area: Staff with gym access validation
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import (
    CurrentStaff,
    RequireOwner,
    RequireOwnerOrManager,
    RequireStaff,
    RoleChecker,
    StaffGymDep,
)
from app.models import Message

router = APIRouter(prefix="/rbac", tags=["rbac-examples"])


@router.get(
    "/owner-only",
    response_model=Message,
    dependencies=[RequireOwner],
)
def owner_only_route(current_staff: CurrentStaff) -> Message:
    """Route accessible only by owners.

    Demonstrates RequireOwner dependency usage.
    """
    return Message(
        message=f"Welcome, owner {current_staff.first_name}! "
        f"You have full access to gym {current_staff.gym_id}."
    )


@router.get(
    "/manager-or-above",
    response_model=Message,
    dependencies=[RequireOwnerOrManager],
)
def manager_or_above_route(current_staff: CurrentStaff) -> Message:
    """Route accessible by owners and managers.

    Demonstrates RequireOwnerOrManager dependency usage.
    """
    return Message(
        message=f"Welcome, {current_staff.role.value} {current_staff.first_name}! "
        f"You have management access."
    )


@router.get(
    "/any-staff",
    response_model=Message,
    dependencies=[RequireStaff],
)
def any_staff_route(current_staff: CurrentStaff) -> Message:
    """Route accessible by any staff role.

    Demonstrates RequireStaff dependency usage.
    """
    return Message(
        message=f"Welcome, {current_staff.role.value} {current_staff.first_name}! "
        f"You are a verified staff member."
    )


@router.get(
    "/gyms/{gym_id}/staff-area",
    response_model=Message,
)
def gym_staff_area(
    gym_id: UUID,
    staff: StaffGymDep,
) -> Message:
    """Route with gym-scoped access validation.

    Demonstrates StaffGymDep dependency that validates:
    1. User is authenticated staff
    2. Staff belongs to the requested gym

    Args:
        gym_id: Gym ID from path (validated against staff's gym_id)
        staff: Current staff with gym access validated
    """
    return Message(
        message=f"Welcome to gym {gym_id} staff area, {staff.first_name}! "
        f"Your role: {staff.role.value}"
    )


@router.get(
    "/gyms/{gym_id}/owner-area",
    response_model=Message,
    dependencies=[RequireOwner],
)
def gym_owner_area(
    gym_id: UUID,
    staff: StaffGymDep,
) -> Message:
    """Route requiring both gym access AND owner role.

    Demonstrates combining StaffGymDep with role requirements.
    Staff must:
    1. Be authenticated
    2. Have owner role
    3. Belong to the requested gym
    """
    return Message(
        message=f"Welcome to gym {gym_id} owner dashboard, {staff.first_name}!"
    )


@router.get(
    "/inline-role-check",
    response_model=Message,
)
def inline_role_check_route(
    current_staff: CurrentStaff,
    _: None = Depends(RoleChecker(["owner", "manager"])),
) -> Message:
    """Route demonstrating inline RoleChecker usage.

    Shows how to use RoleChecker as a parameter dependency
    instead of in the dependencies list.
    """
    return Message(
        message=f"Access granted via inline role check for {current_staff.role.value}!"
    )
