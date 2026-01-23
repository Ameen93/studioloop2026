"""StudioLoop domain models.

This package contains all SQLModel database models organized by domain:
- base: Base classes (BaseModel, GymScopedModel, mixins)
- auth: User and authentication models
- gym: Gym (tenant root) model
- consumer: Consumer (platform-scoped) model
- space: Space (gym-scoped) model

All models follow:
- UUID primary keys (ARCH-27)
- snake_case naming (ARCH-24)
- Automatic timestamps
"""

# Base classes and mixins
from app.models.base import (
    BaseModel,
    GymScopedModel,
    GymScopedSoftDeleteModel,
    SoftDeleteMixin,
    TimestampMixin,
)

# Domain models
from app.models.gym import Gym, GymCreate, GymPublic, GymUpdate
from app.models.consumer import Consumer, ConsumerCreate, ConsumerPublic, ConsumerUpdate
from app.models.space import Space, SpaceCreate, SpacePublic, SpaceUpdate

# Re-export existing models from old location for backward compatibility
# TODO: Migrate these to app.models.auth in future story
from app.models_legacy import (
    Item,
    ItemBase,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    Message,
    NewPassword,
    Token,
    TokenPayload,
    UpdatePassword,
    User,
    UserBase,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

__all__ = [
    # Base classes
    "BaseModel",
    "GymScopedModel",
    "GymScopedSoftDeleteModel",
    "SoftDeleteMixin",
    "TimestampMixin",
    # Domain models
    "Gym",
    "GymCreate",
    "GymUpdate",
    "GymPublic",
    "Consumer",
    "ConsumerCreate",
    "ConsumerUpdate",
    "ConsumerPublic",
    "Space",
    "SpaceCreate",
    "SpaceUpdate",
    "SpacePublic",
    # Legacy models (from models_legacy.py)
    "User",
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UpdatePassword",
    "UserPublic",
    "UsersPublic",
    "Item",
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemPublic",
    "ItemsPublic",
    "Message",
    "Token",
    "TokenPayload",
    "NewPassword",
]
