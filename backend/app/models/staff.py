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
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import JSON, Column
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
    invitation_status: str = Field(default="accepted", max_length=20)
    working_hours: dict[str, dict[str, str | bool | None]] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    hourly_rate_cents: int | None = Field(default=None, ge=0)

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


class StaffUpdate(SQLModel):
    """Schema for updating staff profile - all fields optional."""

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)


class StaffPublic(SQLModel):
    """Schema for staff in API responses (excludes sensitive fields)."""

    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    role: StaffRole
    gym_id: UUID
    is_email_verified: bool
    is_active: bool
