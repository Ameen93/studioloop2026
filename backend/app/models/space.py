"""Space model - gym-scoped example of tenant isolation.

Spaces represent physical rooms or areas within a gym where
classes are held. This is a gym-scoped model demonstrating
the multi-tenancy pattern.
"""

from uuid import UUID

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.models.base import GymScopedSoftDeleteModel


class SpaceBase(SQLModel):
    """Base properties shared by Space schemas."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Space name (e.g., 'Main Studio', 'Yoga Room')",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Space description",
    )
    capacity: int = Field(
        default=0,
        ge=0,
        description="Maximum number of participants",
    )


class Space(GymScopedSoftDeleteModel, SpaceBase, table=True):
    """Space model - gym-scoped room or area.

    Spaces are gym-scoped, meaning:
    - Each space belongs to exactly one gym
    - All queries MUST include gym_id filter
    - Spaces are isolated between gyms

    Example multi-tenancy usage:
        # CORRECT - always filter by gym_id
        spaces = session.exec(
            select(Space).where(Space.gym_id == current_gym_id)
        ).all()

        # WRONG - never query without gym_id!
        # spaces = session.exec(select(Space)).all()
    """

    __tablename__ = "spaces"

    # Relationship to Gym (parent)
    # gym: "Gym" = Relationship(back_populates="spaces")

    # Space configuration
    floor_area_sqm: float | None = Field(
        default=None,
        ge=0,
        description="Floor area in square meters",
    )

    # Amenities and equipment (can be expanded to separate table)
    has_mirrors: bool = Field(default=False)
    has_sound_system: bool = Field(default=False)
    has_air_conditioning: bool = Field(default=False)
    amenities: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    equipment: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    custom_amenities: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    custom_equipment: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )

    # Availability
    is_bookable: bool = Field(
        default=True,
        description="Whether space can be booked for classes",
    )


# Schema classes for API request/response
class SpaceCreate(SpaceBase):
    """Schema for creating a space within a gym."""

    # gym_id will be injected from path/context, not from request body
    floor_area_sqm: float | None = None
    has_mirrors: bool = False
    has_sound_system: bool = False
    has_air_conditioning: bool = False
    amenities: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    custom_amenities: list[str] = Field(default_factory=list)
    custom_equipment: list[str] = Field(default_factory=list)
    is_bookable: bool = True


class SpaceUpdate(SQLModel):
    """Schema for updating a space - all fields optional."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    capacity: int | None = Field(default=None, ge=0)
    floor_area_sqm: float | None = Field(default=None, ge=0)
    has_mirrors: bool | None = None
    has_sound_system: bool | None = None
    has_air_conditioning: bool | None = None
    amenities: list[str] | None = None
    equipment: list[str] | None = None
    custom_amenities: list[str] | None = None
    custom_equipment: list[str] | None = None
    is_bookable: bool | None = None


class SpacePublic(SpaceBase):
    """Schema for space in API responses."""

    id: UUID
    gym_id: UUID
    floor_area_sqm: float | None = None
    has_mirrors: bool
    has_sound_system: bool
    has_air_conditioning: bool
    amenities: list[str]
    equipment: list[str]
    custom_amenities: list[str]
    custom_equipment: list[str]
    is_bookable: bool
    is_active: bool
