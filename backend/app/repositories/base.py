"""Base repository classes for data access.

This module provides generic repository implementations following the
Repository Pattern. Repositories handle all database operations and
enforce multi-tenancy isolation for gym-scoped entities.

Usage:
    # For platform-scoped models (no tenant filtering)
    class ConsumerRepository(BaseRepository[Consumer, ConsumerCreate, ConsumerUpdate]):
        pass

    # For gym-scoped models (automatic tenant filtering)
    class SpaceRepository(GymScopedRepository[Space, SpaceCreate, SpaceUpdate]):
        pass
"""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlmodel import Session, SQLModel, select

from app.models.base import GymScopedModel, SoftDeleteMixin

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic base repository for CRUD operations.

    Provides standard database operations for any SQLModel.
    For gym-scoped models, use GymScopedRepository instead.

    Type Parameters:
        ModelType: The database model class
        CreateSchemaType: Schema for creating new instances
        UpdateSchemaType: Schema for updating instances
    """

    def __init__(self, model: type[ModelType], session: Session):
        """Initialize repository with model class and database session.

        Args:
            model: The SQLModel class this repository manages
            session: SQLModel/SQLAlchemy database session
        """
        self.model = model
        self.session = session

    def get(self, id: UUID) -> ModelType | None:
        """Get a single record by ID.

        Args:
            id: UUID of the record

        Returns:
            Model instance or None if not found
        """
        obj = self.session.get(self.model, id)
        # Check soft-delete if model supports it
        if obj and isinstance(obj, SoftDeleteMixin) and not obj.is_active:
            return None
        return obj

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[ModelType]:
        """Get multiple records with pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            include_inactive: If True, include soft-deleted records

        Returns:
            List of model instances
        """
        statement = select(self.model)

        # Apply soft-delete filter if model supports it
        if not include_inactive and issubclass(self.model, SoftDeleteMixin):
            statement = statement.where(self.model.is_active == True)  # noqa: E712

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record.

        Args:
            obj_in: Schema with data for the new record

        Returns:
            Created model instance
        """
        db_obj = self.model.model_validate(obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Update an existing record.

        Args:
            db_obj: Existing model instance to update
            obj_in: Schema or dict with update data

        Returns:
            Updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # Update timestamp if model supports it
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.now(timezone.utc)  # type: ignore

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, *, id: UUID, soft: bool = True) -> ModelType | None:
        """Delete a record by ID.

        Args:
            id: UUID of the record to delete
            soft: If True, soft-delete (set is_active=False). If False, hard delete.

        Returns:
            Deleted model instance or None if not found
        """
        obj = self.session.get(self.model, id)
        if not obj:
            return None

        if soft and isinstance(obj, SoftDeleteMixin):
            obj.soft_delete()
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
        else:
            self.session.delete(obj)
            self.session.commit()

        return obj

    def count(self, *, include_inactive: bool = False) -> int:
        """Count total records.

        Args:
            include_inactive: If True, include soft-deleted records

        Returns:
            Total count of records
        """
        from sqlalchemy import func

        statement = select(func.count()).select_from(self.model)

        if not include_inactive and issubclass(self.model, SoftDeleteMixin):
            statement = statement.where(self.model.is_active == True)  # noqa: E712

        result = self.session.exec(statement).one()
        return result


class GymScopedRepository(
    BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    """Repository for gym-scoped (tenant-isolated) models.

    CRITICAL: This repository automatically filters ALL queries by gym_id
    to enforce multi-tenancy isolation. Use this for all gym-scoped models.

    Example:
        class SpaceRepository(GymScopedRepository[Space, SpaceCreate, SpaceUpdate]):
            pass

        # Usage in route
        repo = SpaceRepository(Space, session, gym_id=current_gym.id)
        spaces = repo.get_multi()  # Automatically filtered by gym_id
    """

    def __init__(
        self,
        model: type[ModelType],
        session: Session,
        gym_id: UUID,
    ):
        """Initialize gym-scoped repository.

        Args:
            model: The SQLModel class (must inherit from GymScopedModel)
            session: Database session
            gym_id: Gym ID (tenant identifier) for filtering
        """
        super().__init__(model, session)
        self.gym_id = gym_id

        # Validate that model is gym-scoped
        if not issubclass(model, GymScopedModel):
            raise TypeError(
                f"{model.__name__} must inherit from GymScopedModel "
                "to use GymScopedRepository"
            )

    def get(self, id: UUID) -> ModelType | None:
        """Get a single record by ID within the current gym.

        CRITICAL: Always filters by gym_id to prevent cross-tenant access.

        Args:
            id: UUID of the record

        Returns:
            Model instance or None if not found (or belongs to different gym)
        """
        statement = select(self.model).where(
            self.model.id == id,
            self.model.gym_id == self.gym_id,  # type: ignore
        )

        # Apply soft-delete filter if model supports it
        if issubclass(self.model, SoftDeleteMixin):
            statement = statement.where(self.model.is_active == True)  # noqa: E712

        return self.session.exec(statement).first()

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[ModelType]:
        """Get multiple records within the current gym.

        CRITICAL: Always filters by gym_id to prevent cross-tenant access.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            include_inactive: If True, include soft-deleted records

        Returns:
            List of model instances belonging to the current gym
        """
        statement = select(self.model).where(
            self.model.gym_id == self.gym_id  # type: ignore
        )

        # Apply soft-delete filter if model supports it
        if not include_inactive and issubclass(self.model, SoftDeleteMixin):
            statement = statement.where(self.model.is_active == True)  # noqa: E712

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record within the current gym.

        Automatically sets gym_id on the new record.

        Args:
            obj_in: Schema with data for the new record

        Returns:
            Created model instance with gym_id set
        """
        obj_data = obj_in.model_dump()
        obj_data["gym_id"] = self.gym_id
        db_obj = self.model.model_validate(obj_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, *, id: UUID, soft: bool = True) -> ModelType | None:
        """Delete a record within the current gym.

        CRITICAL: Validates gym_id before deletion to prevent cross-tenant access.

        Args:
            id: UUID of the record to delete
            soft: If True, soft-delete (set is_active=False). If False, hard delete.

        Returns:
            Deleted model instance or None if not found/wrong gym
        """
        # First, verify the record belongs to this gym
        obj = self.get(id)
        if not obj:
            return None

        if soft and isinstance(obj, SoftDeleteMixin):
            obj.soft_delete()
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
        else:
            self.session.delete(obj)
            self.session.commit()

        return obj

    def count(self, *, include_inactive: bool = False) -> int:
        """Count records within the current gym.

        CRITICAL: Always filters by gym_id.

        Args:
            include_inactive: If True, include soft-deleted records

        Returns:
            Total count of records in the current gym
        """
        from sqlalchemy import func

        statement = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.gym_id == self.gym_id)  # type: ignore
        )

        if not include_inactive and issubclass(self.model, SoftDeleteMixin):
            statement = statement.where(self.model.is_active == True)  # noqa: E712

        result = self.session.exec(statement).one()
        return result
