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
from app.models.class_session import (
    ClassSession,
    ClassSessionCreate,
    ClassSessionPublic,
    ClassSessionStatus,
)
from app.models.consumer import (
    AccountDeletionRequest,
    AuthProvider,
    Consumer,
    ConsumerCreate,
    ConsumerPublic,
    ConsumerUpdate,
    UserRole,
)
from app.models.gym import Gym, GymCreate, GymPublic, GymSubscriptionTier, GymUpdate
from app.models.gym_closure import GymClosure, GymClosureCreate, GymClosurePublic
from app.models.digital_waiver import DigitalWaiverAcceptance
from app.models.gym_membership import (
    GymMembership,
    GymMembershipStatus,
    GymMembershipTier,
)
from app.models.membership_plan import (
    MembershipBillingCycle,
    MembershipPlan,
    MembershipPlanCreate,
    MembershipPlanPublic,
    MembershipPlanUpdate,
)
from app.models.space import Space, SpaceCreate, SpacePublic, SpaceUpdate
from app.models.staff import Staff, StaffLoginRequest, StaffRole, StaffToken

# Re-export existing models from old location for backward compatibility
# TODO: Migrate these to app.models.auth in future story
from app.models_legacy import (
    ForgotPasswordRequest,
    Item,
    ItemBase,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    Message,
    NewPassword,
    RefreshTokenRequest,
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
    "GymSubscriptionTier",
    "GymClosure",
    "GymClosureCreate",
    "GymClosurePublic",
    "AccountDeletionRequest",
    "AuthProvider",
    "Consumer",
    "ConsumerCreate",
    "ConsumerUpdate",
    "ConsumerPublic",
    "UserRole",
    "Space",
    "SpaceCreate",
    "SpaceUpdate",
    "SpacePublic",
    "ClassSession",
    "ClassSessionCreate",
    "ClassSessionPublic",
    "ClassSessionStatus",
    "GymMembership",
    "GymMembershipStatus",
    "GymMembershipTier",
    "DigitalWaiverAcceptance",
    "MembershipPlan",
    "MembershipPlanCreate",
    "MembershipPlanUpdate",
    "MembershipPlanPublic",
    "MembershipBillingCycle",
    "Staff",
    "StaffRole",
    "StaffLoginRequest",
    "StaffToken",
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
    "RefreshTokenRequest",
    "NewPassword",
    "ForgotPasswordRequest",
]
