# Story 2.1: Gym Registration and Owner Account

Status: complete

## Story

As a **gym owner**,
I want to register my gym on StudioLoop,
So that I can start using the platform to manage my business.

## Acceptance Criteria

1. **Given** a new gym owner visiting the registration page
   **When** I enter my email, password, gym name, and contact details
   **Then** a consumer account is created with `role: owner`

2. **And** a `gyms` table record is created with UUID primary key

3. **And** the owner is linked to the gym via `staff` table with `role: owner`

4. **And** I receive a verification email

5. **And** `gyms` table includes: `name`, `slug` (unique URL-friendly), `contact_email`, `contact_phone`, `is_active`

## Tasks / Subtasks

- [x] Task 1: Update Gym model for registration requirements (AC: #2, #5)
  - [x] 1.1 Rename `email` → `contact_email` field in Gym model (via migration)
  - [x] 1.2 Rename `phone` → `contact_phone` field in Gym model (via migration)
  - [x] 1.3 Create Alembic migration `866cf31ca2ba_rename_gym_email_phone_to_contact_fields.py`
  - [x] 1.4 Create `GymRegistrationCreate` schema for registration request

- [x] Task 2: Create gym registration endpoint (AC: #1, #2, #3, #4, #5)
  - [x] 2.1 Create `POST /auth/gym/register` endpoint in new `app/api/routes/gyms.py`
  - [x] 2.2 Validate email format and password strength (min 8 chars)
  - [x] 2.3 Generate unique slug from gym name (lowercase, hyphenated)
  - [x] 2.4 Create Consumer record with `role: owner`
  - [x] 2.5 Create Gym record with contact details and generated slug
  - [x] 2.6 Create Staff record linking Consumer to Gym with `role: owner`
  - [x] 2.7 Send verification email using existing `generate_verification_email()`
  - [x] 2.8 Handle duplicate email with `EMAIL_ALREADY_EXISTS` error (checks both Consumer and Staff tables)
  - [x] 2.9 Handle duplicate gym slug by appending number suffix

- [x] Task 3: Create gym registration response schema (AC: #1, #2, #3)
  - [x] 3.1 Create `GymRegistrationResponse` schema with owner + gym info
  - [x] 3.2 Include `gym_id`, `owner_id`, `staff_id` in response
  - [x] 3.3 Add to `models/__init__.py` exports

- [x] Task 4: Register gym router in main.py
  - [x] 4.1 Add gym router to `app/api/main.py`
  - [x] 4.2 Use prefix `/auth/gym` for gym auth endpoints

- [x] Task 5: Add backend tests for gym registration
  - [x] 5.1 Test successful registration creates Consumer, Gym, and Staff records
  - [x] 5.2 Test Consumer has `role: owner`
  - [x] 5.3 Test Staff has `role: owner` and correct `gym_id`
  - [x] 5.4 Test verification email is sent
  - [x] 5.5 Test duplicate email returns `EMAIL_ALREADY_EXISTS`
  - [x] 5.6 Test unique slug generation (hyphenation, collision handling)
  - [x] 5.7 Test password validation (min 8 chars)
  - [x] 5.8 Test response contains all required IDs

- [x] Task 6: Regenerate API client
  - [x] 6.1 Run `pnpm generate:api` in frontend workspace
  - [x] 6.2 Verify new gym registration types are generated

## Dev Notes

### Architecture Compliance

- **ARCH-10**: Custom JWT with FastAPI native (already implemented)
- **ARCH-11**: Password hashing with Argon2 via `get_password_hash()` (already implemented)
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-27**: UUIDs for all primary keys
- **ARCH-28**: Standard error response format with code, message, details
- **ARCH-29**: Gym data isolated per tenant - this creates the tenant root
- **FR7**: Gym owners can register their gym and complete onboarding

### Current Codebase State

**Gym model EXISTS at `backend/app/models/gym.py`:**
```python
class Gym(SoftDeleteMixin, BaseModel, GymBase, table=True):
    __tablename__ = "gyms"

    # Has: name, slug, description, is_marketplace_enabled
    # Has: email, phone (but AC says contact_email, contact_phone)
    # Has: address fields, coordinates
    # Missing: explicit contact_email, contact_phone per AC#5
```

**Staff model EXISTS at `backend/app/models/staff.py`:**
```python
class Staff(SoftDeleteMixin, GymScopedModel, table=True):
    __tablename__ = "staff"

    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    role: StaffRole  # OWNER, MANAGER, FRONT_DESK, INSTRUCTOR
    gym_id: UUID  # From GymScopedModel
```

**Consumer model EXISTS at `backend/app/models/consumer.py`:**
```python
class Consumer(SoftDeleteMixin, BaseModel, ConsumerBase, table=True):
    __tablename__ = "consumers"

    email: EmailStr
    hashed_password: str | None
    first_name: str
    last_name: str
    role: UserRole  # CONSUMER, OWNER, MANAGER, etc.
    is_email_verified: bool
```

### Critical Implementation Details

#### Gym Registration Flow

1. **Validate inputs**: email format, password strength, gym name
2. **Check for existing Consumer** with same email
3. **Generate unique slug** from gym name:
   ```python
   def generate_slug(name: str, session: Session) -> str:
       """Generate unique URL-friendly slug from gym name."""
       import re
       base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
       slug = base_slug
       counter = 1
       while session.exec(select(Gym).where(Gym.slug == slug)).first():
           slug = f"{base_slug}-{counter}"
           counter += 1
       return slug
   ```
4. **Create Consumer** with `role: owner`:
   ```python
   consumer = Consumer(
       email=data.email,
       hashed_password=get_password_hash(data.password),
       first_name=data.first_name,
       last_name=data.last_name,
       role=UserRole.OWNER,  # CRITICAL: Set role to owner
       is_email_verified=False,
   )
   ```
5. **Create Gym** record:
   ```python
   gym = Gym(
       name=data.gym_name,
       slug=generate_slug(data.gym_name, session),
       contact_email=data.gym_contact_email or data.email,
       contact_phone=data.gym_contact_phone,
   )
   ```
6. **Create Staff** linking Consumer to Gym as owner:
   ```python
   staff = Staff(
       email=data.email,
       hashed_password=get_password_hash(data.password),
       first_name=data.first_name,
       last_name=data.last_name,
       role=StaffRole.OWNER,  # CRITICAL: Staff role is owner
       gym_id=gym.id,
       is_email_verified=False,
   )
   ```
7. **Send verification email** using existing utilities

#### Request Schema

```python
class GymRegistrationCreate(SQLModel):
    """Schema for gym owner registration."""

    # Owner details
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

    # Gym details
    gym_name: str = Field(min_length=1, max_length=255)
    gym_contact_email: EmailStr | None = None  # Optional, defaults to owner email
    gym_contact_phone: str | None = Field(default=None, max_length=50)
```

#### Response Schema

```python
class GymRegistrationResponse(SQLModel):
    """Response after successful gym registration."""

    owner_id: UUID
    gym_id: UUID
    staff_id: UUID
    email: str
    gym_name: str
    gym_slug: str
    message: str = "Registration successful. Please verify your email."
```

#### Error Response Format

All errors use standard format (ARCH-28):
```json
{
  "detail": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "An account with this email already exists",
    "details": { "field": "email" }
  }
}
```

Error codes:
- `EMAIL_ALREADY_EXISTS`: Email already registered
- `GYM_NAME_REQUIRED`: Gym name cannot be empty
- `INVALID_PASSWORD`: Password too short

### Testing Requirements

**Test file: `tests/api/routes/test_gym_registration.py`**

Key test scenarios:
1. Successful registration creates all three records
2. Consumer record has `role: owner`
3. Staff record has `role: owner` and correct `gym_id`
4. Verification email is sent (mock `send_email`)
5. Duplicate email returns 400 with `EMAIL_ALREADY_EXISTS`
6. Slug generation: "My Awesome Gym" → "my-awesome-gym"
7. Slug collision: "My Gym" (exists) → "my-gym-1"
8. Password validation: <8 chars returns 422
9. Response contains `owner_id`, `gym_id`, `staff_id`

### Project Structure Notes

**Files to create:**
```
backend/
├── app/
│   ├── api/routes/
│   │   └── gyms.py          # NEW: Gym registration routes
│   └── models/
│       └── gym.py           # UPDATE: Add contact_email, contact_phone
├── alembic/versions/
│   └── xxxx_add_gym_contact_fields.py  # NEW: Migration
└── tests/api/routes/
    └── test_gym_registration.py  # NEW: Registration tests
```

**Files to modify:**
```
backend/
├── app/
│   ├── api/main.py          # Add gym router
│   └── models/__init__.py   # Export new schemas
```

### Previous Story Intelligence

From Epic 1 implementation:
- **Story 1.1**: Consumer registration pattern established - reuse same email verification flow
- **Story 1.3**: Staff authentication exists - staff table and StaffRole enum ready
- **All stories**: Argon2 password hashing via `get_password_hash()` is standard
- **All stories**: Error format with `code`, `message`, `details` is standard

### What NOT to Do

- **DO NOT** use bcrypt - MUST use Argon2 per ARCH-11
- **DO NOT** create a separate "gym owner" table - use Consumer with `role: owner`
- **DO NOT** allow gym registration without linking to Staff table
- **DO NOT** send verification email to gym contact email - send to owner's email
- **DO NOT** allow duplicate slugs - generate unique suffix
- **DO NOT** skip Staff record creation - owner must be in staff table for gym auth
- **DO NOT** forget to hash password for BOTH Consumer and Staff records

### Existing Utilities to Reuse

**Password hashing (`backend/app/core/security.py`):**
```python
from app.core.security import get_password_hash, verify_password
```

**Email verification (`backend/app/utils.py`):**
```python
from app.utils import (
    generate_email_verification_token,
    generate_email_verification_email,
    send_email,
)
```

### Dependencies on Previous Stories

- Story 1-1: Consumer registration (COMPLETE) - Consumer model, email verification
- Story 1-3: Staff login (COMPLETE) - Staff model, StaffRole enum
- Story 0-7: Multi-tenancy patterns (COMPLETE) - GymScopedModel base class

### References

- [Source: epics.md#Story 2.1 - Gym Registration and Owner Account]
- [Source: architecture.md#ARCH-28 - Gym Data Isolation]
- [Source: architecture.md#ARCH-29 - Consumer Profiles Platform-Owned]
- [Source: project-context.md#Multi-Tenancy]
- [Source: backend/app/models/gym.py - Existing Gym model]
- [Source: backend/app/models/staff.py - Existing Staff model]
- [Source: backend/app/models/consumer.py - Existing Consumer model]

---

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

- Renamed existing `email` and `phone` fields to `contact_email` and `contact_phone` in Gym model (fields already existed, just renamed for clarity per AC#5)
- Migration uses `op.alter_column` with `new_column_name` to preserve existing data
- Endpoint placed at `/auth/gym/register` for consistency with consumer auth pattern
- Duplicate email check covers both Consumer and Staff tables
- 15 comprehensive tests added covering all acceptance criteria
- All 285 tests pass

### File List

**Created:**
- `backend/app/api/routes/gyms.py` - Gym registration endpoint
- `backend/app/alembic/versions/866cf31ca2ba_rename_gym_email_phone_to_contact_fields.py` - Migration
- `backend/tests/api/routes/test_gym_registration.py` - 15 registration tests

**Modified:**
- `backend/app/models/gym.py` - Added schemas, renamed fields
- `backend/app/models/__init__.py` - Export new schemas
- `backend/app/api/main.py` - Register gym router
- `frontend/packages/api-client/src/generated/types.gen.ts` - Generated types
- `frontend/packages/api-client/src/generated/sdk.gen.ts` - Generated SDK
