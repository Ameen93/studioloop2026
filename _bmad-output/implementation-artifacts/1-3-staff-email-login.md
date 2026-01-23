# Story 1.3: Staff Email Login

Status: done

## Story

As a **gym staff member**,
I want to login with my email and password,
So that I can access the gym management app.

## Acceptance Criteria

1. **Given** I have an active staff account at a gym
   **When** I enter correct email and password
   **Then** I receive a JWT with role claims (owner/manager/front_desk/instructor)

2. **And** the token includes `gym_id` for tenant context

3. **And** I am redirected to the gym dashboard

4. **And** `staff` table is created with `gym_id` foreign key

5. **And** inactive staff accounts cannot login

## Tasks / Subtasks

- [ ] Task 1: Create Staff model and database table (AC: #4)
  - [ ] 1.1 Create `backend/app/models/staff.py` with Staff SQLModel
  - [ ] 1.2 Add StaffRole enum: `owner`, `manager`, `front_desk`, `instructor`
  - [ ] 1.3 Add fields: `id`, `gym_id` (FK), `email`, `hashed_password`, `first_name`, `last_name`, `role`, `phone`, `is_active`, `is_email_verified`, `created_at`, `updated_at`
  - [ ] 1.4 Add relationship to Gym model
  - [ ] 1.5 Export Staff from `models/__init__.py`
  - [ ] 1.6 Create Alembic migration for staff table

- [ ] Task 2: Create staff login endpoint (AC: #1, #2, #5)
  - [ ] 2.1 Create `backend/app/api/routes/staff_auth.py` router
  - [ ] 2.2 Add `POST /auth/staff/login` endpoint
  - [ ] 2.3 Validate email/password using existing `verify_password`
  - [ ] 2.4 Check `is_active` flag - reject if false
  - [ ] 2.5 Check `is_email_verified` flag - reject if false (optional, may defer)
  - [ ] 2.6 Generate JWT with role and gym_id claims in payload
  - [ ] 2.7 Return token response with `access_token`, `refresh_token`, `token_type`

- [ ] Task 3: Update token generation for staff claims (AC: #1, #2)
  - [ ] 3.1 Modify `create_access_token` to accept optional `role` and `gym_id` claims
  - [ ] 3.2 Modify `create_refresh_token` similarly
  - [ ] 3.3 Update `TokenPayload` model to include `role` and `gym_id` fields
  - [ ] 3.4 Ensure consumer tokens still work (backward compatible)

- [ ] Task 4: Create staff login schemas (AC: #1)
  - [ ] 4.1 Create `StaffLoginRequest` schema (email, password)
  - [ ] 4.2 Create `StaffToken` response schema (access_token, refresh_token, token_type, role, gym_id)

- [ ] Task 5: Register staff auth router (AC: #1)
  - [ ] 5.1 Add staff_auth router to `api/main.py`
  - [ ] 5.2 Regenerate API client with new endpoints

- [ ] Task 6: Add backend tests (AC: all)
  - [ ] 6.1 Test successful staff login returns tokens with role/gym_id
  - [ ] 6.2 Test invalid credentials returns 401
  - [ ] 6.3 Test inactive staff returns 401 (same error, no enumeration)
  - [ ] 6.4 Test staff model creation with gym relationship

## Dev Notes

### Architecture Compliance

- **ARCH-10**: Custom JWT (FastAPI native) - extend for staff with role claims
- **ARCH-11**: Password verification with Argon2 (reuse existing `verify_password`)
- **ARCH-12**: JWT access (<24h) + refresh rotation - same pattern as consumer
- **ARCH-13**: RBAC - Role claims in JWT: Owner, Manager, Front Desk, Instructor
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-28**: Standard error response format with code, message, details
- **ARCH-28**: Gym data isolation - staff belongs to ONE gym (gym_id FK)

### Current Codebase State

**Security module EXISTS at `backend/app/core/security.py`:**
```python
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**TokenPayload model at `backend/app/models_legacy.py`:**
```python
class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None  # "access" or "refresh"
```

**Consumer login EXISTS at `backend/app/api/routes/consumers.py`:**
- Pattern to follow for staff login implementation
- Uses same error response format

**Gym model EXISTS at `backend/app/models/gym.py`:**
- Staff will have `gym_id` foreign key to this table
- Multi-tenancy pattern already established

**Seed placeholder at `backend/app/seed/staff.py`:**
- Documents planned staff roles: owner, manager, front_desk, instructor
- Will need updating once Staff model is created

### Critical Implementation Details

#### Staff Model Definition

**Create `backend/app/models/staff.py`:**
```python
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import GymScopedModel

if TYPE_CHECKING:
    from app.models.gym import Gym


class StaffRole(str, Enum):
    """Staff roles per ARCH-13."""
    OWNER = "owner"
    MANAGER = "manager"
    FRONT_DESK = "front_desk"
    INSTRUCTOR = "instructor"


class Staff(GymScopedModel, table=True):
    """Staff member belonging to a gym.

    Per ARCH-28: Staff is gym-scoped (strict tenant isolation).
    One staff member belongs to ONE gym only.
    """
    __tablename__ = "staff"

    email: EmailStr = Field(index=True)
    hashed_password: str
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: StaffRole = Field(default=StaffRole.FRONT_DESK)
    phone: str | None = Field(default=None, max_length=20)
    is_email_verified: bool = Field(default=False)

    # Relationship to gym
    gym: "Gym" = Relationship(back_populates="staff")


# Request/Response schemas
class StaffLoginRequest(SQLModel):
    """Staff login request."""
    email: EmailStr
    password: str = Field(min_length=8)


class StaffToken(SQLModel):
    """Token response for staff authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str  # Staff role for client-side routing
    gym_id: str  # Gym context for multi-tenancy
```

#### Staff Login Endpoint

**Create `backend/app/api/routes/staff_auth.py`:**
```python
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    needs_rehash,
    verify_password,
)
from app.models.staff import Staff, StaffLoginRequest, StaffToken

router = APIRouter(prefix="/auth/staff", tags=["staff-auth"])


@router.post("/login", response_model=StaffToken)
def login_staff(
    session: SessionDep,
    login_data: StaffLoginRequest,
) -> StaffToken:
    """Authenticate staff member and return tokens with role/gym claims."""
    staff = session.exec(
        select(Staff).where(Staff.email == login_data.email)
    ).first()

    # Same error for invalid email or password (prevent enumeration)
    if not staff or not staff.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    if not verify_password(login_data.password, staff.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Check if staff is active (AC #5)
    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Upgrade legacy bcrypt hash if needed
    if needs_rehash(staff.hashed_password):
        staff.hashed_password = get_password_hash(login_data.password)
        session.add(staff)
        session.commit()

    # Generate tokens with role and gym_id claims (AC #1, #2)
    access_token = create_access_token(
        subject=str(staff.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )
    refresh_token = create_refresh_token(
        subject=str(staff.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )

    return StaffToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=staff.role.value,
        gym_id=str(staff.gym_id),
    )
```

#### Token Generation Updates

**Update `backend/app/core/security.py`:**
```python
def create_access_token(
    subject: str | Any,
    expires_delta: timedelta,
    role: str | None = None,
    gym_id: str | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        subject: The token subject (typically user ID)
        expires_delta: Token validity duration
        role: Optional staff role claim
        gym_id: Optional gym ID for tenant context
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    if role:
        to_encode["role"] = role
    if gym_id:
        to_encode["gym_id"] = gym_id
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta,
    role: str | None = None,
    gym_id: str | None = None,
) -> str:
    """Create a JWT refresh token with optional role/gym claims."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    if role:
        to_encode["role"] = role
    if gym_id:
        to_encode["gym_id"] = gym_id
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### TokenPayload Update

**Update `backend/app/models_legacy.py`:**
```python
class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None  # "access" or "refresh"
    role: str | None = None  # Staff role if applicable
    gym_id: str | None = None  # Gym ID for tenant context
```

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── api/routes/
│   │   └── staff_auth.py        # NEW: Staff login endpoint
│   ├── core/
│   │   └── security.py          # UPDATE: Add role/gym_id to tokens
│   ├── models/
│   │   ├── __init__.py          # UPDATE: Export Staff
│   │   └── staff.py             # NEW: Staff model and schemas
│   └── models_legacy.py         # UPDATE: TokenPayload with role/gym_id
├── alembic/versions/
│   └── xxxx_add_staff_table.py  # NEW: Migration for staff table
├── tests/
│   └── api/routes/
│       └── test_staff_auth.py   # NEW: Staff login tests
```

### Testing Requirements

**Backend tests (`tests/api/routes/test_staff_auth.py`):**
1. `test_staff_login_success` - Valid credentials return tokens with role/gym_id
2. `test_staff_login_invalid_password` - Returns 401 INVALID_CREDENTIALS
3. `test_staff_login_nonexistent_email` - Returns 401 (same error)
4. `test_staff_login_inactive` - Returns 401 (same error)
5. `test_staff_token_has_role_claim` - Token payload includes role
6. `test_staff_token_has_gym_id_claim` - Token payload includes gym_id

### What NOT to Do

- **DO NOT** create separate User table for staff - use Staff model with gym_id FK
- **DO NOT** allow staff to belong to multiple gyms (that's a future feature)
- **DO NOT** reveal whether email exists in login errors (security)
- **DO NOT** break existing consumer login (backward compatible token changes)
- **DO NOT** skip is_active check (deactivated staff cannot login)
- **DO NOT** use camelCase in API request/response - use `snake_case`

### Previous Story Intelligence

From Story 1.2 completion:
- Token generation with `type` claim already implemented
- `create_access_token` and `create_refresh_token` exist with type claims
- `TokenPayload` has `type` field - just need to add `role` and `gym_id`
- Consumer login pattern established - follow same structure for staff
- Error response format with `code`, `message`, `details` already in use
- Token type validation in `get_current_user` - staff tokens will pass (type="access")

From Story 1.2 Review:
- Token type validation added to deps.py - ensures only access tokens work as bearer
- is_active check added for consumers - apply same pattern for staff
- MMKV v4 uses `createMMKV()` not `new MMKV()` - but staff login is backend-only for now

### Git Intelligence

Recent commits (last 5):
- `61ed350` Merge pull request #9 (story/1-2-consumer-email-login)
- `a333eac` feat(auth): implement consumer email login (Story 1.2)
- `4050f7a` Merge pull request #8 (story/1-1-consumer-email-registration)
- `3d7f19d` style: format consumers.py and utils.py with ruff
- `fcbd7ef` fix(lint): allow print statements in CLI scripts

Pattern insights:
- Feature branch naming: `story/1-3-staff-email-login`
- Commit prefix: `feat(auth):` for auth features
- Login implementation pattern well-established from 1-2

### Dependencies on Previous Stories

- Story 1-1: Consumer registration (COMPLETE) - established model patterns
- Story 1-2: Consumer login (REVIEW) - established login/token patterns
- Gym model (EXISTS) - Staff FK relationship target
- GymScopedModel base class (EXISTS) - Staff extends this

### What's Deferred to Future Stories

- Staff registration/invitation (Epic 3, Story 3.1)
- Staff email verification flow
- Gym mobile app login screen
- Gym web app login screen (will be created when frontend stories start)

### References

- [Source: epics.md#Story 1.3]
- [Source: epics.md#ARCH-10 through ARCH-14]
- [Source: architecture.md#RBAC - Role claims in JWT]
- [Source: architecture.md#Multi-Tenancy - Staff is gym-scoped]
- [Source: project-context.md#Multi-Tenancy (CRITICAL)]
- [Source: backend/app/core/security.py - Token generation]
- [Source: backend/app/api/routes/consumers.py - Login pattern]
- [Source: backend/app/seed/staff.py - Planned staff roles]
- [Source: story 1-2-consumer-email-login.md - Previous implementation]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None

### Completion Notes List

1. Created Staff model with StaffRole enum (owner, manager, front_desk, instructor)
2. Staff model extends GymScopedModel for tenant isolation with gym_id FK
3. Created staff login endpoint at POST /auth/staff/login
4. Updated create_access_token and create_refresh_token to accept optional role and gym_id claims
5. Updated TokenPayload model with role and gym_id fields for backward compatibility
6. Tokens include role and gym_id claims for RBAC and multi-tenancy
7. Inactive staff (is_active=False) cannot login - returns same INVALID_CREDENTIALS error
8. Updated seed orchestrator to delete staff before gyms in reset_seed_data
9. All 129 backend tests passing including 13 new staff auth tests

### File List

**Created:**
- backend/app/models/staff.py - Staff model, StaffRole enum, StaffLoginRequest, StaffToken schemas
- backend/app/api/routes/staff_auth.py - Staff login endpoint
- backend/app/alembic/versions/ee64873623c4_add_staff_table.py - Migration for staff table
- backend/tests/api/routes/test_staff_auth.py - 13 tests for staff auth

**Modified:**
- backend/app/models/gym.py - Added staff relationship
- backend/app/models/__init__.py - Exported Staff, StaffRole, StaffLoginRequest, StaffToken
- backend/app/core/security.py - Added role/gym_id params to token functions
- backend/app/models_legacy.py - Added role/gym_id to TokenPayload
- backend/app/api/main.py - Registered staff_auth router
- backend/app/seed/orchestrator.py - Added Staff to reset_seed_data
