from enum import StrEnum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import GymScopedSoftDeleteModel


class ClassType(StrEnum):
    YOGA = "yoga"
    PILATES = "pilates"
    HIIT = "hiit"
    CROSSFIT = "crossfit"
    CYCLING = "cycling"
    BOXING = "boxing"
    STRENGTH = "strength"
    SWIMMING = "swimming"
    DANCE = "dance"
    MARTIAL_ARTS = "martial_arts"
    OTHER = "other"


class ClassTemplateBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    default_duration_minutes: int = Field(default=60, ge=5, le=480)
    default_capacity: int = Field(default=20, ge=1)
    class_type: ClassType = Field(default=ClassType.OTHER, max_length=20)
    default_instructor_staff_id: UUID | None = Field(
        default=None, foreign_key="staff.id", index=True
    )
    default_space_id: UUID | None = Field(
        default=None, foreign_key="spaces.id", index=True
    )
    default_price_cents: int = Field(default=0, ge=0)
    waitlist_enabled: bool = Field(default=True)
    color: str = Field(default="#3B82F6", max_length=7)


class ClassTemplate(GymScopedSoftDeleteModel, ClassTemplateBase, table=True):
    __tablename__ = "class_templates"


class ClassTemplateCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    default_duration_minutes: int = Field(default=60, ge=5, le=480)
    default_capacity: int = Field(default=20, ge=1)
    class_type: ClassType = Field(default=ClassType.OTHER, max_length=20)
    default_instructor_staff_id: UUID | None = None
    default_space_id: UUID | None = None
    default_price_cents: int = Field(default=0, ge=0)
    waitlist_enabled: bool = Field(default=True)
    color: str = Field(default="#3B82F6", max_length=7)


class ClassTemplateUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    default_duration_minutes: int | None = Field(default=None, ge=5, le=480)
    default_capacity: int | None = Field(default=None, ge=1)
    class_type: ClassType | None = None
    default_instructor_staff_id: UUID | None = None
    default_space_id: UUID | None = None
    default_price_cents: int | None = Field(default=None, ge=0)
    waitlist_enabled: bool | None = None
    color: str | None = Field(default=None, max_length=7)


class ClassTemplatePublic(SQLModel):
    id: UUID
    gym_id: UUID
    name: str
    description: str | None
    default_duration_minutes: int
    default_capacity: int
    class_type: ClassType
    default_instructor_staff_id: UUID | None
    default_space_id: UUID | None
    default_price_cents: int
    waitlist_enabled: bool
    color: str
    is_active: bool
