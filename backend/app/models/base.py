"""Base models for StudioLoop backend.

This module provides foundational model classes that establish:
- UUID primary keys (ARCH-27)
- Automatic timestamps (created_at, updated_at)
- snake_case naming conventions (ARCH-24)
- Soft-delete support
- Multi-tenancy via gym_id scoping

All domain models should inherit from these base classes.
"""

import re
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _pluralize(name: str) -> str:
    """Simple pluralization for table names."""
    if name.endswith("s"):
        return name + "es"
    if name.endswith("y"):
        return name[:-1] + "ies"
    return name + "s"


# =============================================================================
# Mixin Classes - These are NOT table models, just provide fields
# =============================================================================


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamps.

    Timestamps use UTC timezone for consistency.
    This is a pure Python mixin, not an SQLModel class.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        description="Record creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        description="Record last update timestamp (UTC)",
    )


class SoftDeleteMixin:
    """Mixin providing soft-delete capability.

    Instead of permanently deleting records, mark them as inactive.
    This is a pure Python mixin, not an SQLModel class.
    """

    is_active: bool = Field(
        default=True,
        nullable=False,
        index=True,
        description="Whether this record is active (soft-delete flag)",
    )
    deleted_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp when record was soft-deleted (UTC)",
    )

    def soft_delete(self) -> None:
        """Mark record as soft-deleted."""
        self.is_active = False
        self.deleted_at = datetime.now(timezone.utc)


# =============================================================================
# Base Model Classes - These CAN be table models
# =============================================================================


class BaseModel(TimestampMixin, SQLModel):
    """Base model with UUID primary key and timestamps.

    All database models should inherit from this class.
    Provides:
    - UUID primary key (per ARCH-27)
    - created_at, updated_at timestamps
    - Automatic snake_case, pluralized table names (per ARCH-24)

    Usage:
        class Gym(BaseModel, table=True):
            name: str
            # ... other fields
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier (UUID v4)",
    )

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Auto-generate __tablename__ from class name in snake_case, plural form."""
        super().__init_subclass__(**kwargs)
        # Only set tablename for actual table classes
        if kwargs.get("table", False) and not hasattr(cls, "__tablename__"):
            # Convert CamelCase to snake_case and pluralize
            snake_name = _snake_case(cls.__name__)
            cls.__tablename__ = _pluralize(snake_name)  # type: ignore


class GymScopedModel(BaseModel):
    """Base model for gym-scoped (tenant-isolated) entities.

    CRITICAL: All gym-scoped data MUST use this base class to ensure
    proper tenant isolation. Every query on gym-scoped tables MUST
    include a gym_id filter.

    Multi-Tenancy Pattern:
    - Gym data is STRICTLY isolated - never leak across tenants
    - Every gym-scoped query MUST include gym_id filter
    - Row-level security on all gym tables

    Usage:
        class Space(GymScopedModel, table=True):
            name: str
            # gym_id is automatically available
    """

    # NOTE: gym_id foreign key is defined here but the actual FK constraint
    # will be established when Gym model is created. This is a forward reference.
    gym_id: UUID = Field(
        foreign_key="gyms.id",
        nullable=False,
        index=True,
        description="Gym tenant ID (foreign key to gyms.id)",
    )


class GymScopedSoftDeleteModel(SoftDeleteMixin, GymScopedModel):
    """Gym-scoped model with soft-delete support.

    Combines tenant isolation with soft-delete capability.
    Use this for entities that should never be permanently deleted.
    """

    pass
