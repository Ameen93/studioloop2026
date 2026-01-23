"""Staff model for gym employees.

Staff members belong to a single gym (tenant-scoped per ARCH-28).
Staff roles determine permissions per ARCH-13 RBAC:
- owner: Full gym access, billing, staff management
- manager: Operations, scheduling, member management
- front_desk: Check-ins, bookings, basic member queries
- instructor: Own schedule, class management
"""

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import GymScopedModel, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.gym import Gym


class StaffRole(str, Enum):
    """Staff roles per ARCH-13 RBAC.

    Hierarchy: owner > manager > front_desk / instructor
    """

    OWNER = "owner"
    MANAGER = "manager"
    FRONT_DESK = "front_desk"
    INSTRUCTOR = "instructor"


class Staff(SoftDeleteMixin, GymScopedModel, table=True):
    """Staff member belonging to a gym.

    Per ARCH-28: Staff is gym-scoped (strict tenant isolation).
    One staff member belongs to ONE gym only.

    Multi-tenancy: gym_id is inherited from GymScopedModel.
    """

    __tablename__ = "staff"

    email: EmailStr = Field(index=True, max_length=255)
    hashed_password: str
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: StaffRole = Field(default=StaffRole.FRONT_DESK)
    phone: str | None = Field(default=None, max_length=20)
    is_email_verified: bool = Field(default=False)

    # Token rotation (ARCH-12)
    token_version: int = Field(
        default=1,
        description="Incremented on token refresh to invalidate old refresh tokens",
    )

    # Relationship to gym
    gym: "Gym" = Relationship(back_populates="staff")


# =============================================================================
# Request/Response Schemas
# =============================================================================


class StaffLoginRequest(SQLModel):
    """Staff login request schema."""

    email: EmailStr
    password: str = Field(min_length=8)


class StaffToken(SQLModel):
    """Token response for staff authentication.

    Includes role and gym_id for client-side routing and tenant context.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str  # Staff role for client-side routing
    gym_id: str  # Gym context for multi-tenancy
