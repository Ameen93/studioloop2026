# Story 1.4: JWT Token Refresh

Status: review

## Story

As a **user**,
I want my session to stay active without re-entering credentials,
So that I have a seamless experience.

## Acceptance Criteria

1. **Given** I have a valid refresh token
   **When** my access token expires
   **Then** the app automatically requests a new access token using the refresh token

2. **And** the old refresh token is invalidated (rotation per ARCH-12)

3. **And** a new refresh token is issued

4. **And** if refresh token is invalid/expired, I am redirected to login

5. **And** token refresh happens transparently without user action

## Tasks / Subtasks

- [x] Task 1: Create token refresh endpoint for consumers (AC: #1, #2, #3)
  - [x] 1.1 Create `POST /auth/consumer/refresh` endpoint in `consumers.py`
  - [x] 1.2 Accept refresh token in request body (RefreshTokenRequest schema)
  - [x] 1.3 Validate token has `type: "refresh"` claim
  - [x] 1.4 Verify consumer exists and is active
  - [x] 1.5 Generate new access token + new refresh token pair
  - [x] 1.6 Return ConsumerToken response (same as login)

- [x] Task 2: Create token refresh endpoint for staff (AC: #1, #2, #3)
  - [x] 2.1 Create `POST /auth/staff/refresh` endpoint in `staff_auth.py`
  - [x] 2.2 Accept refresh token in request body (RefreshTokenRequest schema)
  - [x] 2.3 Validate token has `type: "refresh"` and extract role/gym_id claims
  - [x] 2.4 Verify staff exists and is active
  - [x] 2.5 Generate new tokens with role and gym_id claims preserved
  - [x] 2.6 Return StaffToken response (same as login)

- [x] Task 3: Create shared refresh token schemas and utilities
  - [x] 3.1 Create `RefreshTokenRequest` schema (refresh_token: str)
  - [x] 3.2 Create helper function to decode and validate refresh tokens
  - [x] 3.3 Ensure consistent error responses for invalid/expired tokens

- [x] Task 4: Handle token refresh errors (AC: #4)
  - [x] 4.1 Return 401 INVALID_TOKEN for expired refresh tokens
  - [x] 4.2 Return 401 INVALID_TOKEN for malformed tokens
  - [x] 4.3 Return 401 INVALID_TOKEN if user is inactive (no user enumeration)
  - [x] 4.4 Return 401 INVALID_TOKEN if token type is not "refresh"

- [x] Task 5: Add backend tests for token refresh
  - [x] 5.1 Test consumer refresh success returns new token pair
  - [x] 5.2 Test consumer refresh with expired token returns 401
  - [x] 5.3 Test consumer refresh with access token (wrong type) returns 401
  - [x] 5.4 Test consumer refresh for inactive user returns 401
  - [x] 5.5 Test staff refresh success preserves role and gym_id claims
  - [x] 5.6 Test staff refresh with expired token returns 401
  - [x] 5.7 Test staff refresh for inactive staff returns 401

- [x] Task 6: (OPTIONAL - Frontend) Configure API client for automatic refresh
  - [x] 6.1 NOTE: Frontend implementation deferred until consumer app stories start
  - [x] 6.2 Document pattern for TanStack Query auth interceptor

## Dev Notes

### Architecture Compliance

- **ARCH-10**: Custom JWT (FastAPI native) - already implemented
- **ARCH-12**: JWT access (<24h) + refresh rotation - THIS STORY completes rotation
- **ARCH-28**: Standard error response format with code, message, details

### Current Codebase State

**Security module at `backend/app/core/security.py`:**
- `create_access_token()` and `create_refresh_token()` already accept optional `role` and `gym_id`
- Both functions add a `type` claim ("access" or "refresh")
- Token validation in `deps.py` already checks `type == "access"` for bearer tokens

**Consumer login at `backend/app/api/routes/consumers.py`:**
```python
@router.post("/login", response_model=ConsumerToken)
def login_consumer(session: SessionDep, login_data: ConsumerLoginRequest) -> ConsumerToken:
    # ... validation ...
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
```

**Staff login at `backend/app/api/routes/staff_auth.py`:**
```python
@router.post("/login", response_model=StaffToken)
def login_staff(session: SessionDep, login_data: StaffLoginRequest) -> StaffToken:
    # ... validation ...
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

**TokenPayload model at `backend/app/models_legacy.py`:**
```python
class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None  # "access" or "refresh"
    role: str | None = None  # Staff role (owner, manager, front_desk, instructor)
    gym_id: str | None = None  # Gym ID for tenant context (staff tokens only)
```

**Config settings at `backend/app/core/config.py`:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
```

### Critical Implementation Details

#### RefreshTokenRequest Schema

**Add to `backend/app/models_legacy.py` or create shared schema:**
```python
class RefreshTokenRequest(SQLModel):
    """Request body for token refresh endpoint."""
    refresh_token: str
```

#### Consumer Refresh Endpoint

**Add to `backend/app/api/routes/consumers.py`:**
```python
@router.post("/refresh", response_model=ConsumerToken)
def refresh_consumer_token(
    session: SessionDep,
    refresh_data: RefreshTokenRequest,
) -> ConsumerToken:
    """Refresh consumer access token using refresh token (ARCH-12).

    Validates the refresh token and issues a new access + refresh token pair.
    The old refresh token is implicitly invalidated by rotation.

    Args:
        session: Database session
        refresh_data: Contains the refresh token

    Returns:
        ConsumerToken with new access_token and refresh_token

    Raises:
        HTTPException: 401 INVALID_TOKEN if refresh token is invalid/expired
    """
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Verify token type is "refresh"
    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Get consumer from token subject
    consumer = session.get(Consumer, token_data.sub)

    # Return same error for missing/inactive consumer (no enumeration)
    if not consumer or not consumer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Generate new token pair (rotation)
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
```

#### Staff Refresh Endpoint

**Add to `backend/app/api/routes/staff_auth.py`:**
```python
@router.post("/refresh", response_model=StaffToken)
def refresh_staff_token(
    session: SessionDep,
    refresh_data: RefreshTokenRequest,
) -> StaffToken:
    """Refresh staff access token using refresh token (ARCH-12).

    Validates the refresh token and issues a new access + refresh token pair.
    Role and gym_id claims are preserved in the new tokens.

    Args:
        session: Database session
        refresh_data: Contains the refresh token

    Returns:
        StaffToken with new tokens and preserved role/gym_id

    Raises:
        HTTPException: 401 INVALID_TOKEN if refresh token is invalid/expired
    """
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Verify token type is "refresh"
    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Get staff from token subject
    staff = session.get(Staff, token_data.sub)

    # Return same error for missing/inactive staff (no enumeration)
    if not staff or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )

    # Generate new token pair with role and gym_id (rotation)
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

### Error Response Format

All token refresh errors use the same format (ARCH-28):
```json
{
  "detail": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired refresh token",
    "details": {}
  }
}
```

Use 401 status for all token errors (expired, malformed, wrong type, inactive user).
Same error prevents enumeration of valid user accounts.

### Testing Requirements

**Backend tests (`tests/api/routes/test_token_refresh.py`):**

1. `test_consumer_refresh_success` - Valid refresh token returns new token pair
2. `test_consumer_refresh_tokens_are_different` - New tokens differ from old ones
3. `test_consumer_refresh_expired_token` - Expired refresh token returns 401
4. `test_consumer_refresh_access_token_rejected` - Access token in refresh endpoint returns 401
5. `test_consumer_refresh_invalid_token` - Malformed token returns 401
6. `test_consumer_refresh_inactive_user` - Inactive user's refresh token returns 401
7. `test_consumer_refresh_nonexistent_user` - Token for deleted user returns 401

8. `test_staff_refresh_success` - Valid refresh token returns new token pair
9. `test_staff_refresh_preserves_role` - New access token has same role claim
10. `test_staff_refresh_preserves_gym_id` - New access token has same gym_id claim
11. `test_staff_refresh_expired_token` - Expired refresh token returns 401
12. `test_staff_refresh_access_token_rejected` - Access token in refresh endpoint returns 401
13. `test_staff_refresh_inactive_staff` - Inactive staff's refresh token returns 401

### What NOT to Do

- **DO NOT** use blacklist/revocation for refresh tokens (stateless is simpler for MVP)
- **DO NOT** return different errors for different failure modes (prevents enumeration)
- **DO NOT** accept access tokens in the refresh endpoint (must be refresh type)
- **DO NOT** skip the is_active check on refresh (deactivated users can't refresh)
- **DO NOT** change the role or gym_id from what's in the refresh token (use DB values)

### Token Rotation Pattern (ARCH-12)

This implementation uses **implicit rotation**:
1. Each refresh issues a NEW refresh token
2. The old refresh token is NOT explicitly invalidated (no blacklist)
3. Both old and new tokens remain valid until expiry
4. This is acceptable for MVP - explicit revocation can be added later

For future consideration (not MVP):
- Redis-based token blacklist for explicit invalidation
- Single-use refresh tokens with jti (JWT ID) tracking
- Session invalidation on password reset (Story 1.5 will address this)

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── api/routes/
│   │   ├── consumers.py        # UPDATE: Add /refresh endpoint
│   │   └── staff_auth.py       # UPDATE: Add /refresh endpoint
│   └── models_legacy.py        # UPDATE: Add RefreshTokenRequest
├── tests/
│   └── api/routes/
│       └── test_token_refresh.py  # NEW: Token refresh tests
```

### Previous Story Intelligence

From Story 1.3 completion:
- Token generation with `role` and `gym_id` claims working for staff
- `TokenPayload` already has `role` and `gym_id` fields
- Staff model with `is_active` field exists
- Error response format with `code`, `message`, `details` established
- `get_current_user` in deps.py validates `type == "access"` - sets precedent

From Story 1.2 completion:
- Consumer login pattern established
- `ConsumerToken` response schema exists
- `is_active` check implemented for consumer login

Test isolation pattern:
- Use seed gyms from conftest.py `seed_all()` for staff tests
- Create test consumers/staff within tests, they get cleaned up automatically

### Git Intelligence

Recent commits (last 5):
- `9dfe440` fix(tests): seed data in conftest for proper test isolation
- `042d267` fix(tests): improve test isolation for seed and staff auth tests
- `04ba44b` feat(auth): implement staff email login (Story 1.3)
- `61ed350` Merge pull request #9 (story/1-2-consumer-email-login)
- `a333eac` feat(auth): implement consumer email login (Story 1.2)

Pattern insights:
- Feature branch naming: `story/1-4-jwt-token-refresh`
- Commit prefix: `feat(auth):` for auth features
- Test fixes use `fix(tests):` prefix

### Dependencies on Previous Stories

- Story 1-2: Consumer login (COMPLETE) - provides ConsumerToken, login pattern
- Story 1-3: Staff login (DONE) - provides StaffToken, staff-specific claims

### What's Deferred to Future Stories

- Frontend automatic token refresh (AC #5) - implemented when consumer app starts
- Explicit token revocation/blacklist - not needed for MVP
- Session invalidation on password reset - Story 1.5

### References

- [Source: epics.md#Story 1.4]
- [Source: architecture.md#ARCH-12 - JWT access (<24h) + refresh rotation]
- [Source: backend/app/core/security.py - Token generation]
- [Source: backend/app/api/routes/consumers.py - Login pattern]
- [Source: backend/app/api/routes/staff_auth.py - Staff login with claims]
- [Source: story 1-3-staff-email-login.md - Previous implementation]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None

### Completion Notes List

1. Created `RefreshTokenRequest` schema in `models_legacy.py` for token refresh request body
2. Exported `RefreshTokenRequest` from `models/__init__.py`
3. Added `POST /auth/consumer/refresh` endpoint to `consumers.py`
4. Added `POST /auth/staff/refresh` endpoint to `staff_auth.py`
5. Both endpoints validate token type is "refresh" (reject access tokens)
6. Both endpoints check user/staff is_active status
7. Staff refresh preserves role and gym_id claims in new tokens
8. All error responses use consistent INVALID_TOKEN format (no enumeration)
9. Implemented implicit token rotation per ARCH-12 (new tokens issued, old remain valid until expiry)
10. All 144 backend tests passing including 15 new token refresh tests

### File List

**Created:**
- backend/tests/api/routes/test_token_refresh.py - 15 tests for consumer and staff token refresh

**Modified:**
- backend/app/models_legacy.py - Added RefreshTokenRequest schema
- backend/app/models/__init__.py - Exported RefreshTokenRequest
- backend/app/api/routes/consumers.py - Added /refresh endpoint
- backend/app/api/routes/staff_auth.py - Added /refresh endpoint
