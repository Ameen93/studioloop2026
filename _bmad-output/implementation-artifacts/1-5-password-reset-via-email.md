# Story 1.5: Password Reset via Email

Status: ready-for-dev

## Story

As a **user**,
I want to reset my password via email,
So that I can recover my account if I forget my password.

## Acceptance Criteria

1. **Given** I request a password reset with my registered email
   **When** I submit the request
   **Then** a reset link is sent to my email (valid for 1 hour per AC, but config has 48h - use config)

2. **And** clicking the link opens a password reset screen

3. **And** I can set a new password (min 8 chars)

4. **And** all existing sessions are invalidated after reset

5. **And** unregistered emails do not reveal account existence (security - no enumeration)

## Tasks / Subtasks

- [ ] Task 1: Create consumer password reset request endpoint (AC: #1, #5)
  - [ ] 1.1 Create `POST /auth/consumer/forgot-password` endpoint in `consumers.py`
  - [ ] 1.2 Accept email in request body (use existing EmailStr validation)
  - [ ] 1.3 Look up consumer by email
  - [ ] 1.4 If found AND email verified, generate password reset token using `generate_password_reset_token()`
  - [ ] 1.5 Send reset email using `generate_reset_password_email()` and `send_email()`
  - [ ] 1.6 ALWAYS return success message (no enumeration - same response for found/not found)
  - [ ] 1.7 Do NOT send email if consumer doesn't exist or email not verified (but still return success)

- [ ] Task 2: Create consumer password reset confirmation endpoint (AC: #2, #3, #4)
  - [ ] 2.1 Create `POST /auth/consumer/reset-password` endpoint in `consumers.py`
  - [ ] 2.2 Accept token and new_password in request body (NewPassword schema or similar)
  - [ ] 2.3 Verify token using `verify_password_reset_token()`
  - [ ] 2.4 If invalid/expired token, return 400 INVALID_TOKEN
  - [ ] 2.5 Look up consumer by email from token
  - [ ] 2.6 Hash new password using `get_password_hash()` (Argon2)
  - [ ] 2.7 Update consumer.hashed_password
  - [ ] 2.8 **CRITICAL**: Increment `consumer.token_version` to invalidate all existing sessions
  - [ ] 2.9 Commit changes and return success message

- [ ] Task 3: Create staff password reset request endpoint (AC: #1, #5)
  - [ ] 3.1 Create `POST /auth/staff/forgot-password` endpoint in `staff_auth.py`
  - [ ] 3.2 Accept email in request body
  - [ ] 3.3 Look up staff by email
  - [ ] 3.4 If found AND is_active, generate password reset token
  - [ ] 3.5 Send reset email
  - [ ] 3.6 ALWAYS return success message (no enumeration)

- [ ] Task 4: Create staff password reset confirmation endpoint (AC: #2, #3, #4)
  - [ ] 4.1 Create `POST /auth/staff/reset-password` endpoint in `staff_auth.py`
  - [ ] 4.2 Accept token and new_password in request body
  - [ ] 4.3 Verify token
  - [ ] 4.4 Look up staff by email from token
  - [ ] 4.5 Hash new password and update
  - [ ] 4.6 **CRITICAL**: Increment `staff.token_version` to invalidate all existing sessions
  - [ ] 4.7 Commit and return success

- [ ] Task 5: Create request/response schemas
  - [ ] 5.1 Create `ForgotPasswordRequest` schema (email: EmailStr)
  - [ ] 5.2 Create `ResetPasswordRequest` schema (token: str, new_password: str min 8 chars)
  - [ ] 5.3 Add to `models/__init__.py` exports

- [ ] Task 6: Add backend tests for password reset
  - [ ] 6.1 Test consumer forgot-password returns success for valid email
  - [ ] 6.2 Test consumer forgot-password returns success for invalid email (no enumeration)
  - [ ] 6.3 Test consumer forgot-password doesn't send email for unverified account
  - [ ] 6.4 Test consumer reset-password success updates password
  - [ ] 6.5 Test consumer reset-password invalidates existing sessions (token_version incremented)
  - [ ] 6.6 Test consumer reset-password with expired token returns 400
  - [ ] 6.7 Test consumer reset-password with invalid token returns 400
  - [ ] 6.8 Test consumer can login with new password after reset
  - [ ] 6.9 Test consumer old refresh tokens fail after password reset
  - [ ] 6.10 Test staff forgot-password returns success for valid/invalid email
  - [ ] 6.11 Test staff reset-password success updates password and invalidates sessions
  - [ ] 6.12 Test staff reset-password preserves role after re-login

## Dev Notes

### Architecture Compliance

- **ARCH-11**: Password hashing uses Argon2 via `get_password_hash()` - already implemented
- **ARCH-12**: Token rotation via `token_version` - increment on password reset to invalidate all sessions
- **ARCH-28**: Standard error response format with code, message, details
- **FR3**: Users can reset their password via email

### Existing Utilities (REUSE THESE!)

**`backend/app/utils.py` already has:**
```python
def generate_password_reset_token(email: str) -> str:
    """Generate JWT token with email as subject, expires in EMAIL_RESET_TOKEN_EXPIRE_HOURS (48h)"""

def verify_password_reset_token(token: str) -> str | None:
    """Verify token and return email, or None if invalid/expired"""

def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """Generate email HTML with reset link: {FRONTEND_HOST}/reset-password?token={token}"""
```

**Config at `backend/app/core/config.py`:**
```python
EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48  # Note: AC says 1 hour, config says 48h - use config
FRONTEND_HOST: str = "http://localhost:5173"
```

### Token Version for Session Invalidation

The `token_version` field exists on both Consumer and Staff models:
```python
# Token rotation (ARCH-12)
token_version: int = Field(
    default=1,
    description="Incremented on token refresh to invalidate old refresh tokens",
)
```

**CRITICAL**: On password reset, you MUST increment `token_version`. This invalidates:
1. All existing refresh tokens (they have old token_version embedded)
2. Prevents token refresh for any active sessions
3. Forces users to re-login on all devices

### Schema Patterns

**ForgotPasswordRequest:**
```python
class ForgotPasswordRequest(SQLModel):
    """Request body for password reset request."""
    email: EmailStr
```

**ResetPasswordRequest:**
```python
class ResetPasswordRequest(SQLModel):
    """Request body for password reset confirmation."""
    token: str
    new_password: str = Field(min_length=8, max_length=128)
```

### Endpoint Implementation Patterns

**Consumer Forgot Password:**
```python
@router.post("/forgot-password")
def forgot_password(
    session: SessionDep,
    request_data: ForgotPasswordRequest,
) -> Message:
    """Request password reset email (no enumeration).

    Always returns success, regardless of whether email exists.
    Only sends email if consumer exists AND email is verified.
    """
    consumer = session.exec(
        select(Consumer).where(Consumer.email == request_data.email)
    ).first()

    # Only send email if consumer exists, is active, and email verified
    # But ALWAYS return success to prevent enumeration
    if consumer and consumer.is_active and consumer.is_email_verified:
        if settings.emails_enabled:
            token = generate_password_reset_token(request_data.email)
            email_data = generate_reset_password_email(
                email_to=consumer.email,
                email=request_data.email,
                token=token,
            )
            send_email(
                email_to=consumer.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

    return Message(message="If the email exists, a password reset link has been sent")
```

**Consumer Reset Password:**
```python
@router.post("/reset-password")
def reset_password(
    session: SessionDep,
    request_data: ResetPasswordRequest,
) -> Message:
    """Reset password using token from email.

    Validates token, updates password, and invalidates all existing sessions.
    """
    email = verify_password_reset_token(request_data.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired reset token",
                "details": {},
            },
        )

    consumer = session.exec(
        select(Consumer).where(Consumer.email == email)
    ).first()

    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired reset token",
                "details": {},
            },
        )

    if not consumer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired reset token",
                "details": {},
            },
        )

    # Update password
    consumer.hashed_password = get_password_hash(request_data.new_password)

    # CRITICAL: Invalidate all existing sessions
    consumer.token_version += 1

    session.add(consumer)
    session.commit()

    return Message(message="Password has been reset successfully")
```

### Error Response Format

All errors use standard format (ARCH-28):
```json
{
  "detail": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired reset token",
    "details": {}
  }
}
```

Use 400 Bad Request for token validation errors.
Use same error for all failure modes to prevent enumeration.

### Testing Requirements

**Test file: `tests/api/routes/test_password_reset.py`**

Key test scenarios:
1. Forgot password - success response for valid email
2. Forgot password - success response for invalid email (no enumeration!)
3. Forgot password - no email sent for unverified consumer
4. Reset password - success updates hashed_password
5. Reset password - token_version is incremented
6. Reset password - old refresh tokens no longer work
7. Reset password - can login with new password
8. Reset password - expired token returns 400
9. Reset password - malformed token returns 400
10. Staff versions of all above

### Previous Story Intelligence

From Story 1.4 (JWT Token Refresh):
- `token_version` was added to Consumer and Staff models
- Refresh endpoints validate `token_data.token_version != user.token_version`
- Incrementing `token_version` will immediately invalidate all refresh tokens
- Migration `651efb3bdc08_add_token_version_to_consumer_and_staff.py` already applied

From Story 1.1 (Consumer Registration):
- Email verification flow exists
- `is_email_verified` field used to gate login
- Pattern: don't reveal account existence for security

### What NOT to Do

- **DO NOT** return different responses for found/not found emails (enumeration attack)
- **DO NOT** send reset email to unverified accounts
- **DO NOT** forget to increment `token_version` (session invalidation is critical!)
- **DO NOT** use 401 for token errors (use 400 - token is not auth, it's validation)
- **DO NOT** reveal user info in error messages
- **DO NOT** create new email templates - use existing `reset_password.html`

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── api/routes/
│   │   ├── consumers.py        # UPDATE: Add /forgot-password, /reset-password
│   │   └── staff_auth.py       # UPDATE: Add /forgot-password, /reset-password
│   └── models_legacy.py        # UPDATE: Add ForgotPasswordRequest, ResetPasswordRequest
├── tests/
│   └── api/routes/
│       └── test_password_reset.py  # NEW: Password reset tests
```

### Dependencies on Previous Stories

- Story 1-1: Consumer registration (COMPLETE) - Consumer model, email verification
- Story 1-2: Consumer login (REVIEW) - Login flow to test after reset
- Story 1-3: Staff login (DONE) - Staff model and login flow
- Story 1-4: Token refresh (REVIEW) - token_version for session invalidation

### Email Template

Existing template at `backend/app/email-templates/build/reset_password.html`
Uses link format: `{FRONTEND_HOST}/reset-password?token={token}`

### Config Values

- `EMAIL_RESET_TOKEN_EXPIRE_HOURS = 48` (use this, not the 1 hour from AC)
- `FRONTEND_HOST = "http://localhost:5173"` (for reset link)
- Check `emails_enabled` before attempting to send

### References

- [Source: epics.md#Story 1.5 - Password Reset via Email]
- [Source: architecture.md - Auth Service owns password reset]
- [Source: backend/app/utils.py - Existing token/email utilities]
- [Source: backend/app/api/routes/login.py - Existing admin password reset pattern]
- [Source: backend/app/models/consumer.py - token_version field]
- [Source: backend/app/models/staff.py - token_version field]
- [Source: story 1-4-jwt-token-refresh.md - token_version implementation]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
