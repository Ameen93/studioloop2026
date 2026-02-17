# Story 1.6: User Profile Management

Status: done

## Story

As a **user**,
I want to update my profile information,
So that my account details are current.

## Acceptance Criteria

1. **Given** I am logged in as a consumer
   **When** I navigate to profile settings
   **Then** I can view my current profile information

2. **And** I can update my first name, last name, and phone number

3. **And** phone number validates SA format (+27...)

4. **And** changes are saved immediately

5. **Given** I am logged in as a staff member
   **When** I navigate to profile settings
   **Then** I can update my first name, last name, and phone number

6. **DEFERRED**: Profile photo upload - requires CDN infrastructure (Epic 16)
   - The `avatar_url` field exists on Consumer model
   - Photo upload will be implemented after CDN/S3 infrastructure is deployed

## Tasks / Subtasks

- [x] Task 1: Create CurrentConsumer dependency (Authentication prerequisite)
  - [x] 1.1 Add `get_current_consumer()` function in `deps.py`
  - [x] 1.2 Decode JWT token and look up Consumer by `sub` (UUID)
  - [x] 1.3 Validate token type is "access" (reject refresh tokens)
  - [x] 1.4 Validate consumer is active
  - [x] 1.5 Create `CurrentConsumer = Annotated[Consumer, Depends(get_current_consumer)]`

- [x] Task 2: Create CurrentStaff dependency (Authentication prerequisite)
  - [x] 2.1 Add `get_current_staff()` function in `deps.py`
  - [x] 2.2 Decode JWT token and look up Staff by `sub` (UUID)
  - [x] 2.3 Validate token type is "access" (reject refresh tokens)
  - [x] 2.4 Validate staff is active
  - [x] 2.5 Create `CurrentStaff = Annotated[Staff, Depends(get_current_staff)]`

- [x] Task 3: Add SA phone validation utility
  - [x] 3.1 Create `validate_sa_phone()` function in `app/utils.py`
  - [x] 3.2 Validate format: +27XXXXXXXXX (11-12 digits starting with +27)
  - [x] 3.3 Allow None (phone is optional)
  - [x] 3.4 Return normalized format or raise validation error

- [x] Task 4: Create consumer profile endpoints (AC: #1, #2, #3, #4)
  - [x] 4.1 Create `GET /auth/consumer/me` endpoint to get current consumer profile
  - [x] 4.2 Create `PATCH /auth/consumer/me` endpoint to update profile
  - [x] 4.3 Use `CurrentConsumer` dependency for authentication
  - [x] 4.4 Accept partial updates (first_name, last_name, phone - all optional)
  - [x] 4.5 Validate phone with SA format if provided
  - [x] 4.6 Return updated `ConsumerPublic` response

- [x] Task 5: Create staff profile endpoints (AC: #5)
  - [x] 5.1 Create `GET /auth/staff/me` endpoint to get current staff profile
  - [x] 5.2 Create `PATCH /auth/staff/me` endpoint to update profile
  - [x] 5.3 Use `CurrentStaff` dependency for authentication
  - [x] 5.4 Accept partial updates (first_name, last_name, phone - all optional)
  - [x] 5.5 Validate phone with SA format if provided
  - [x] 5.6 Create `StaffPublic` response schema if not exists

- [x] Task 6: Update schemas
  - [x] 6.1 Verify `ConsumerUpdate` schema exists and has correct fields
  - [x] 6.2 Create `StaffUpdate` schema if not exists (first_name, last_name, phone - all optional)
  - [x] 6.3 Create `StaffPublic` schema if not exists (exclude hashed_password)

- [x] Task 7: Add backend tests for profile management
  - [x] 7.1 Test consumer GET /me returns profile data
  - [x] 7.2 Test consumer GET /me requires authentication (401 without token)
  - [x] 7.3 Test consumer PATCH /me updates first_name
  - [x] 7.4 Test consumer PATCH /me updates last_name
  - [x] 7.5 Test consumer PATCH /me updates phone with valid SA format
  - [x] 7.6 Test consumer PATCH /me rejects invalid phone format (400)
  - [x] 7.7 Test consumer PATCH /me allows null phone (clear phone)
  - [x] 7.8 Test consumer PATCH /me partial update (only one field)
  - [x] 7.9 Test staff GET /me returns profile data with role and gym_id
  - [x] 7.10 Test staff PATCH /me updates profile fields
  - [x] 7.11 Test staff PATCH /me validates phone format
  - [x] 7.12 Test inactive consumer cannot access /me (401)
  - [x] 7.13 Test inactive staff cannot access /me (401)

## Dev Notes

### Architecture Compliance

- **ARCH-10**: Custom JWT (FastAPI native) for authentication
- **ARCH-12**: JWT access tokens for authentication
- **ARCH-28**: Standard error response format with code, message, details
- **ARCH-13**: Role claims in JWT for staff (preserved after profile update)

### Existing Code to Reuse

**Consumer Model (`backend/app/models/consumer.py`):**
```python
class ConsumerUpdate(SQLModel):
    """Schema for updating consumer profile - all fields optional."""
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    accepts_marketing: bool | None = None

class ConsumerPublic(SQLModel):
    """Schema for consumer in API responses."""
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    role: UserRole
    avatar_url: str | None = None
    is_email_verified: bool
    is_active: bool
```

**Current User Pattern (`backend/app/api/deps.py`):**
```python
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # Validate token type is "access" (reject refresh tokens used as bearer)
    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```

### SA Phone Number Validation

South African phone numbers follow this format:
- International format: `+27XXXXXXXXX` (11-12 digits total)
- Mobile: `+27 6X XXX XXXX` or `+27 7X XXX XXXX` or `+27 8X XXX XXXX`
- Landline: `+27 1X XXX XXXX` or `+27 2X XXX XXXX` etc.

**Validation Regex:**
```python
import re

SA_PHONE_PATTERN = re.compile(r"^\+27[1-9]\d{8,9}$")

def validate_sa_phone(phone: str | None) -> str | None:
    """Validate and normalize SA phone number.

    Args:
        phone: Phone number to validate (None is allowed)

    Returns:
        Normalized phone number or None

    Raises:
        ValueError: If phone format is invalid
    """
    if phone is None:
        return None

    # Remove all whitespace and dashes
    normalized = re.sub(r"[\s\-]", "", phone)

    if not SA_PHONE_PATTERN.match(normalized):
        raise ValueError("Phone must be in SA format: +27XXXXXXXXX")

    return normalized
```

### Endpoint Implementation Patterns

**Consumer GET /me:**
```python
@router.get("/me", response_model=ConsumerPublic)
def get_current_consumer_profile(
    current_consumer: CurrentConsumer,
) -> Consumer:
    """Get current consumer's profile."""
    return current_consumer
```

**Consumer PATCH /me:**
```python
@router.patch("/me", response_model=ConsumerPublic)
def update_consumer_profile(
    session: SessionDep,
    current_consumer: CurrentConsumer,
    update_data: ConsumerUpdate,
) -> Consumer:
    """Update current consumer's profile.

    Allows partial updates - only provided fields are updated.
    Phone number must be in SA format (+27...) if provided.
    """
    # Validate phone if provided
    if update_data.phone is not None:
        update_data.phone = validate_sa_phone(update_data.phone)

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(current_consumer, field, value)

    session.add(current_consumer)
    session.commit()
    session.refresh(current_consumer)

    return current_consumer
```

### Error Response Format

All errors use standard format (ARCH-28):
```json
{
  "detail": {
    "code": "INVALID_PHONE_FORMAT",
    "message": "Phone must be in SA format: +27XXXXXXXXX",
    "details": {"field": "phone"}
  }
}
```

### Testing Patterns

**Consumer profile test example:**
```python
class TestConsumerProfile:
    """Tests for consumer profile endpoints."""

    def test_get_me_success(self, client, db):
        """Test GET /auth/consumer/me returns consumer profile."""
        # Create and login consumer
        email = random_email()
        password = "testpassword123"
        # ... register and login to get token

        response = client.get(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert "hashed_password" not in data

    def test_patch_me_update_phone(self, client, db):
        """Test PATCH /auth/consumer/me with valid SA phone."""
        # ... authenticate consumer

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"phone": "+27821234567"},
        )

        assert response.status_code == 200
        assert response.json()["phone"] == "+27821234567"

    def test_patch_me_invalid_phone(self, client, db):
        """Test PATCH /auth/consumer/me rejects non-SA phone."""
        # ... authenticate consumer

        response = client.patch(
            f"{settings.API_V1_STR}/auth/consumer/me",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"phone": "0821234567"},  # Missing +27
        )

        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "INVALID_PHONE_FORMAT"
```

### Previous Story Intelligence

From Story 1.5 (Password Reset):
- Token validation pattern with `verify_password_reset_token()`
- Standard error response format with code, message, details
- Session management via `session.add()`, `session.commit()`, `session.refresh()`

From Story 1.3 (Staff Login):
- Staff model has: email, first_name, last_name, phone, role, gym_id
- Staff tokens include role and gym_id claims
- Pattern for staff authentication

From Story 1.2 (Consumer Login):
- Consumer login returns access_token and refresh_token
- Consumer model has: email, first_name, last_name, phone, avatar_url
- ConsumerPublic schema excludes sensitive fields

### What NOT to Do

- **DO NOT** implement photo upload in this story (deferred to Epic 16)
- **DO NOT** allow email updates (email is identity, requires verification flow)
- **DO NOT** allow password updates via profile endpoint (use /change-password)
- **DO NOT** use 403 for authentication errors (use 401)
- **DO NOT** use generic error messages (use standard ARCH-28 format)
- **DO NOT** reveal inactive status in error messages (use generic 401)

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # UPDATE: Add CurrentConsumer, CurrentStaff
│   │   └── routes/
│   │       ├── consumers.py     # UPDATE: Add GET/PATCH /me endpoints
│   │       └── staff_auth.py    # UPDATE: Add GET/PATCH /me endpoints
│   ├── models/
│   │   └── staff.py             # UPDATE: Add StaffUpdate, StaffPublic schemas
│   └── validators.py            # NEW: SA phone validation (or add to utils.py)
├── tests/
│   └── api/routes/
│       └── test_profile.py      # NEW: Profile management tests
```

### Dependencies on Previous Stories

- Story 1-1: Consumer registration (COMPLETE) - Consumer model, ConsumerPublic
- Story 1-2: Consumer login (REVIEW) - Consumer access tokens
- Story 1-3: Staff login (DONE) - Staff model, staff access tokens
- Story 1-4: Token refresh (REVIEW) - Token validation patterns
- Story 1-5: Password reset (REVIEW) - Error response patterns

### References

- [Source: epics.md#Story 1.6 - User Profile Management]
- [Source: architecture.md - ARCH-10 JWT, ARCH-13 RBAC, ARCH-28 Error Format]
- [Source: backend/app/api/deps.py - CurrentUser pattern]
- [Source: backend/app/models/consumer.py - ConsumerUpdate, ConsumerPublic]
- [Source: backend/app/models/staff.py - Staff model]

---

## QA Checklist

### Consumer Profile Tests

- [ ] **GET /auth/consumer/me**
  - [ ] Returns 200 with consumer profile when authenticated
  - [ ] Returns 401 when no token provided
  - [ ] Returns 401 when invalid/expired token provided
  - [ ] Returns 401 when refresh token used instead of access token
  - [ ] Returns 401 when consumer is inactive
  - [ ] Response does NOT include hashed_password
  - [ ] Response includes: id, email, first_name, last_name, phone, role, is_email_verified

- [ ] **PATCH /auth/consumer/me**
  - [ ] Returns 200 and updates first_name only
  - [ ] Returns 200 and updates last_name only
  - [ ] Returns 200 and updates phone with valid SA format (+27XXXXXXXXX)
  - [ ] Returns 200 and clears phone when null is provided
  - [ ] Returns 200 with multiple fields updated at once
  - [ ] Returns 400 with INVALID_PHONE_FORMAT for invalid phone
  - [ ] Returns 400 for phone without +27 prefix
  - [ ] Returns 400 for phone with wrong digit count
  - [ ] Returns 401 when not authenticated
  - [ ] Does NOT allow email update (email field ignored if sent)
  - [ ] Does NOT allow password update via this endpoint

### Staff Profile Tests

- [ ] **GET /auth/staff/me**
  - [ ] Returns 200 with staff profile when authenticated
  - [ ] Response includes: id, email, first_name, last_name, phone, role, gym_id
  - [ ] Returns 401 when not authenticated
  - [ ] Returns 401 when staff is inactive

- [ ] **PATCH /auth/staff/me**
  - [ ] Returns 200 and updates profile fields
  - [ ] Returns 400 for invalid phone format
  - [ ] Role remains unchanged after profile update
  - [ ] gym_id remains unchanged after profile update

### Phone Validation Edge Cases

- [ ] `+27821234567` - Valid (mobile)
- [ ] `+27721234567` - Valid (mobile)
- [ ] `+27111234567` - Valid (landline)
- [ ] `+27 82 123 4567` - Valid (with spaces, normalized)
- [ ] `+27-82-123-4567` - Valid (with dashes, normalized)
- [ ] `0821234567` - Invalid (missing +27)
- [ ] `27821234567` - Invalid (missing +)
- [ ] `+1821234567` - Invalid (wrong country code)
- [ ] `+278212345` - Invalid (too short)
- [ ] `+2782123456789` - Invalid (too long)
- [ ] `null` - Valid (phone is optional)

---

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Completion Notes

- Implemented `CurrentConsumer` and `CurrentStaff` authentication dependencies in `deps.py`
- Added SA phone validation utility (`validate_sa_phone()`) to `utils.py` with normalization
- Created consumer profile endpoints: `GET /auth/consumer/me` and `PATCH /auth/consumer/me`
- Created staff profile endpoints: `GET /auth/staff/me` and `PATCH /auth/staff/me`
- Added `StaffUpdate` and `StaffPublic` schemas to `staff.py`
- Comprehensive test coverage: 27 tests covering all AC requirements
- All 201 tests pass (27 new + 174 existing), no regressions
- Phone validation supports normalization (removes spaces/dashes) and strict SA format (+27...)
- Profile photo upload deferred to Epic 16 (CDN infrastructure required)

### File List

**Modified:**
- `backend/app/api/deps.py` - Added CurrentConsumer, CurrentStaff dependencies
- `backend/app/api/routes/consumers.py` - Added GET/PATCH /me endpoints
- `backend/app/api/routes/staff_auth.py` - Added GET/PATCH /me endpoints
- `backend/app/models/staff.py` - Added StaffUpdate, StaffPublic schemas
- `backend/app/utils.py` - Added validate_sa_phone() function

**Created:**
- `backend/tests/api/routes/test_profile.py` - 27 comprehensive tests
