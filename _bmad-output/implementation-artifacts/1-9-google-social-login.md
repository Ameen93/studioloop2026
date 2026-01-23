# Story 1.9: Google Social Login

Status: review

## Story

As a **consumer**,
I want to register/login with my Google account,
So that I can use the platform without creating a new password.

## Acceptance Criteria

1. **Given** the Google login button on auth screens
   **When** I authenticate with Google
   **Then** a consumer account is created/linked using my Google email

2. **And** my Google profile photo is imported (optional)

3. **And** I receive JWT tokens as with email login

4. **And** I can later add a password to enable email login

5. **And** existing accounts with same email are linked (not duplicated)

## Tasks / Subtasks

- [x] Task 1: Add Authlib dependency and configure Google OAuth (AC: #1)
  - [x] 1.1 Add `authlib` and `httpx` to pyproject.toml dependencies
  - [x] 1.2 Add Google OAuth config to `core/config.py`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - [x] 1.3 Create `backend/app/core/oauth.py` with Google OAuth client setup using Authlib
  - [x] 1.4 Configure redirect URI for local dev: `http://localhost:8000/api/v1/auth/consumer/google/callback`

- [x] Task 2: Add social login fields to Consumer model (AC: #1, #2, #5)
  - [x] 2.1 Add `google_id: str | None` field to Consumer model (unique index, nullable)
  - [x] 2.2 Add `profile_photo_url: str | None` field to Consumer model (using existing avatar_url)
  - [x] 2.3 Add `auth_provider: str = "email"` field (enum: "email", "google", "apple")
  - [x] 2.4 Create Alembic migration for new fields
  - [x] 2.5 Update `ConsumerPublic` schema to include new fields

- [x] Task 3: Create Google OAuth initiation endpoint (AC: #1)
  - [x] 3.1 Create `GET /auth/consumer/google` endpoint in `consumers.py`
  - [x] 3.2 Generate OAuth state token via SessionMiddleware (CSRF protection)
  - [x] 3.3 Return redirect URL to Google's authorization endpoint
  - [x] 3.4 Include scopes: `openid`, `email`, `profile`

- [x] Task 4: Create Google OAuth callback endpoint (AC: #1, #2, #3, #5)
  - [x] 4.1 Create `GET /auth/consumer/google/callback` endpoint in `consumers.py`
  - [x] 4.2 Validate OAuth state token via SessionMiddleware (CSRF protection)
  - [x] 4.3 Exchange authorization code for access token
  - [x] 4.4 Fetch Google user info (email, name, picture, Google sub/id)
  - [x] 4.5 Check if consumer exists by `google_id` OR `email`:
    - If by `google_id`: Login existing user
    - If by `email` with no `google_id`: Link Google to existing account
    - If not found: Create new consumer
  - [x] 4.6 Update `avatar_url` if provided (optional, don't overwrite existing)
  - [x] 4.7 Generate JWT tokens (access + refresh) using existing `create_access_token`
  - [x] 4.8 Mark account as email verified (Google already verified email)
  - [x] 4.9 Return JSON with tokens (API-style auth)

- [x] Task 5: Create "add password" endpoint for social users (AC: #4)
  - [x] 5.1 Create `POST /auth/consumer/set-password` endpoint
  - [x] 5.2 Accept `new_password` in request body (min 8 chars)
  - [x] 5.3 Require authenticated user (CurrentConsumer)
  - [x] 5.4 Only allow if `hashed_password` is null (social-only user)
  - [x] 5.5 Set hashed_password with Argon2
  - [x] 5.6 Return success message

- [x] Task 6: Add backend tests for Google OAuth (AC: #1-5)
  - [x] 6.1 Test Google OAuth initiation returns redirect URL
  - [x] 6.2 Test OAuth callback creates new user for unknown Google ID
  - [x] 6.3 Test OAuth callback links to existing user with same email
  - [x] 6.4 Test OAuth callback logs in existing Google-linked user
  - [x] 6.5 Test OAuth callback returns valid JWT tokens
  - [x] 6.6 Test OAuth callback marks email as verified
  - [x] 6.7 Test set-password works for social-only user
  - [x] 6.8 Test set-password fails for user with existing password
  - [x] 6.9 Test OAuth state validation (CSRF protection)
  - [x] 6.10 Test invalid OAuth state returns error

## Dev Notes

### Architecture Compliance

- **ARCH-14**: Social Login uses Authlib for Google integration
- **ARCH-11**: Passwords hashed with Argon2 when added to social accounts
- **ARCH-12**: JWT tokens with <24h expiry, same as email login
- **ARCH-28**: Standard error response format with code, message, details
- **FR1**: Users can register using social login (Google)

### Authlib Setup Pattern

**OAuth Client Configuration (`backend/app/core/oauth.py`):**
```python
from authlib.integrations.starlette_client import OAuth
from app.core.config import settings

oauth = OAuth()

# Google OAuth client
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
)
```

### Config Values to Add

**Add to `backend/app/core/config.py`:**
```python
# Google OAuth (ARCH-14)
GOOGLE_CLIENT_ID: str = ""
GOOGLE_CLIENT_SECRET: str = ""
GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/consumer/google/callback"
```

**Add to `.env.example`:**
```
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Consumer Model Updates

**Add to `backend/app/models/consumer.py`:**
```python
class AuthProvider(str, Enum):
    """Authentication provider types."""
    EMAIL = "email"
    GOOGLE = "google"
    APPLE = "apple"

class Consumer(SQLModel, table=True):
    # ... existing fields ...

    # Social login fields (ARCH-14)
    google_id: str | None = Field(
        default=None,
        index=True,
        unique=True,
        description="Google OAuth sub/ID for social login",
    )
    apple_id: str | None = Field(
        default=None,
        index=True,
        unique=True,
        description="Apple Sign-In user identifier",
    )
    profile_photo_url: str | None = Field(
        default=None,
        description="URL to profile photo (from social provider or uploaded)",
    )
    auth_provider: AuthProvider = Field(
        default=AuthProvider.EMAIL,
        description="Primary authentication provider used to create account",
    )
```

### OAuth Flow Implementation

**Initiation Endpoint:**
```python
@router.get("/google")
async def google_login(request: Request) -> dict:
    """Initiate Google OAuth flow.

    Returns redirect URL to Google's authorization endpoint.
    Stores state token in Redis for CSRF protection.
    """
    from app.core.oauth import oauth

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in Redis with 10 minute expiry
    redis_client.setex(f"oauth_state:{state}", 600, "google")

    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)
```

**Callback Endpoint:**
```python
@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: SessionDep,
    state: str = Query(...),
    code: str = Query(...),
) -> ConsumerToken:
    """Handle Google OAuth callback.

    Validates state, exchanges code for tokens, and creates/links user.
    """
    from app.core.oauth import oauth

    # Validate CSRF state
    stored = redis_client.get(f"oauth_state:{state}")
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_OAUTH_STATE",
                "message": "Invalid or expired OAuth state",
                "details": {},
            },
        )
    redis_client.delete(f"oauth_state:{state}")

    # Exchange code for tokens
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    google_id = user_info["sub"]
    email = user_info["email"]
    name = user_info.get("name", "")
    picture = user_info.get("picture")

    # Parse name
    name_parts = name.split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Find or create consumer
    consumer = session.exec(
        select(Consumer).where(
            (Consumer.google_id == google_id) | (Consumer.email == email)
        )
    ).first()

    if consumer:
        # Existing user - link Google if not already linked
        if not consumer.google_id:
            consumer.google_id = google_id
        if not consumer.profile_photo_url and picture:
            consumer.profile_photo_url = picture
        if not consumer.is_email_verified:
            consumer.is_email_verified = True  # Google verified it
        session.add(consumer)
        session.commit()
        session.refresh(consumer)
    else:
        # New user - create account
        consumer = Consumer(
            email=email,
            first_name=first_name,
            last_name=last_name,
            google_id=google_id,
            profile_photo_url=picture,
            auth_provider=AuthProvider.GOOGLE,
            is_email_verified=True,  # Google verified it
            is_active=True,
            hashed_password=None,  # No password for social login
        )
        session.add(consumer)
        session.commit()
        session.refresh(consumer)

    # Generate tokens
    access_token = create_access_token(
        subject=str(consumer.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        subject=str(consumer.id),
        token_version=consumer.token_version,
    )

    return ConsumerToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
```

### Set Password Endpoint

```python
class SetPasswordRequest(SQLModel):
    """Request to set password for social-login-only user."""
    new_password: str = Field(min_length=8, max_length=128)


@router.post("/set-password")
def set_password(
    session: SessionDep,
    current_consumer: CurrentConsumer,
    request_data: SetPasswordRequest,
) -> Message:
    """Set password for a social-login-only user.

    Allows users who signed up via Google/Apple to add a password
    so they can also login via email.
    """
    if current_consumer.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "PASSWORD_ALREADY_SET",
                "message": "Password is already set. Use change password instead.",
                "details": {},
            },
        )

    current_consumer.hashed_password = get_password_hash(request_data.new_password)
    session.add(current_consumer)
    session.commit()

    return Message(message="Password has been set successfully")
```

### Testing Patterns

```python
class TestGoogleOAuth:
    """Tests for Google OAuth login (Story 1.9)."""

    def test_google_oauth_initiation_returns_redirect(self, client):
        """Test OAuth initiation returns Google auth URL."""
        response = client.get(f"{settings.API_V1_STR}/auth/consumer/google")

        # Should redirect to Google
        assert response.status_code == 302
        assert "accounts.google.com" in response.headers.get("location", "")

    def test_oauth_callback_creates_new_user(self, client, db, mocker):
        """Test callback creates new consumer for unknown Google ID."""
        # Mock Authlib response
        mock_token = {
            "userinfo": {
                "sub": "google-user-id-123",
                "email": "newuser@gmail.com",
                "name": "Test User",
                "picture": "https://example.com/photo.jpg",
            }
        }
        # ... test implementation

    def test_oauth_callback_links_existing_email_user(self, client, db, mocker):
        """Test callback links Google to existing email-registered user."""
        # Create existing user
        existing = Consumer(
            email="existing@gmail.com",
            first_name="Existing",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            is_email_verified=True,
            is_active=True,
        )
        db.add(existing)
        db.commit()

        # Mock Google returning same email
        # ... test that google_id is linked to existing account
```

### Error Response Format

All errors use standard format (ARCH-28):
```json
{
  "detail": {
    "code": "INVALID_OAUTH_STATE",
    "message": "Invalid or expired OAuth state",
    "details": {}
  }
}
```

### What NOT to Do

- **DO NOT** duplicate accounts when Google email matches existing email user
- **DO NOT** skip CSRF state validation (OAuth security requirement)
- **DO NOT** store Google access tokens long-term (only use for initial user info)
- **DO NOT** overwrite existing profile photos without user consent
- **DO NOT** allow password reset for social-only users (they have no password)
- **DO NOT** require email verification for Google users (Google verified it)
- **DO NOT** expose Google client secret in frontend code

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # UPDATE: Add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
│   │   └── oauth.py           # NEW: Authlib OAuth client configuration
│   ├── api/routes/
│   │   └── consumers.py       # UPDATE: Add /google, /google/callback, /set-password
│   └── models/
│       └── consumer.py        # UPDATE: Add google_id, apple_id, profile_photo_url, auth_provider
├── alembic/versions/
│   └── xxx_add_social_login_fields.py  # NEW: Migration for social fields
└── tests/api/routes/
    └── test_google_oauth.py   # NEW: Google OAuth tests
pyproject.toml                 # UPDATE: Add authlib, httpx dependencies
```

### Dependencies on Previous Stories

- Story 1-1: Consumer registration (DONE) - Consumer model exists
- Story 1-2: Consumer login (REVIEW) - JWT token generation pattern
- Story 1-4: Token refresh (REVIEW) - token_version for session management
- Story 1-5: Password reset (REVIEW) - Update to handle social-only users

### Impact on Story 1.7 (POPIA Account Deletion)

Story 1.7 has an assertion that consumer must have password set:
```python
assert current_consumer.hashed_password, "Consumer must have password set"
```

This will need to be updated for social-login users. Options:
1. Require social users to set password before deletion (not ideal)
2. Skip password verification for social-only users
3. Use alternative verification (re-auth via Google)

**Recommendation**: Update Story 1.7 after this story is complete to handle social-only users gracefully.

### Google Developer Console Setup

To test locally, create a project in Google Cloud Console:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable "Google+ API" or "Google Identity API"
4. Go to "Credentials" > "Create Credentials" > "OAuth 2.0 Client IDs"
5. Set application type to "Web application"
6. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/consumer/google/callback`
7. Copy Client ID and Client Secret to `.env`

### Frontend Integration Notes

The frontend will need to:
1. Show "Sign in with Google" button
2. Handle redirect to backend `/auth/consumer/google`
3. Handle callback redirect with tokens
4. Store tokens in MMKV (same as email login)

### References

- [Source: epics.md#Story 1.9 - Google Social Login]
- [Source: architecture.md - ARCH-14 Social Login with Authlib]
- [Source: Authlib Documentation - https://docs.authlib.org/]
- [Source: Google OAuth 2.0 - https://developers.google.com/identity/protocols/oauth2]
- [Source: backend/app/api/routes/consumers.py - Existing consumer routes]
- [Source: backend/app/models/consumer.py - Consumer model]

---

## QA Checklist

### Google OAuth Flow

- [ ] **OAuth Initiation**
  - [ ] GET /auth/consumer/google redirects to Google
  - [ ] State parameter is included for CSRF protection
  - [ ] Correct scopes are requested (openid, email, profile)

- [ ] **OAuth Callback**
  - [ ] Valid state returns user tokens
  - [ ] Invalid/expired state returns 400 INVALID_OAUTH_STATE
  - [ ] Missing code parameter returns error

### Account Creation/Linking

- [ ] **New User**
  - [ ] Unknown Google ID creates new consumer
  - [ ] Email is set from Google profile
  - [ ] Name is parsed from Google profile
  - [ ] is_email_verified is set to true
  - [ ] auth_provider is set to "google"
  - [ ] hashed_password is null

- [ ] **Existing Email User**
  - [ ] Google ID is linked to existing account
  - [ ] Existing password is preserved
  - [ ] No duplicate account created

- [ ] **Existing Google User**
  - [ ] Returns tokens for existing account
  - [ ] No changes to account data

### Token Generation

- [ ] **JWT Tokens**
  - [ ] Access token is valid and includes user ID
  - [ ] Refresh token is valid
  - [ ] Tokens work with other authenticated endpoints

### Set Password

- [ ] **Social-only User**
  - [ ] Can set password successfully
  - [ ] Can then login via email
  - [ ] Password meets minimum requirements

- [ ] **User with Existing Password**
  - [ ] Returns 400 PASSWORD_ALREADY_SET

---

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None - all tests pass

### Completion Notes List

- Implemented full Google OAuth flow using Authlib (ARCH-14)
- Added SessionMiddleware for OAuth state management (CSRF protection)
- Created migration with proper ENUM type handling for PostgreSQL
- All 16 Google OAuth tests pass (15 executed, 1 skipped for missing credentials)
- Full test suite: 253 passed, 1 skipped

### File List

- `backend/pyproject.toml` - Added authlib>=1.3.0, itsdangerous>=2.0.0
- `backend/app/core/config.py` - Added GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
- `backend/app/core/oauth.py` - NEW: Authlib OAuth client configuration
- `backend/app/main.py` - Added SessionMiddleware for OAuth state
- `backend/app/models/consumer.py` - Added AuthProvider enum, google_id, apple_id, auth_provider fields
- `backend/app/models/__init__.py` - Exported AuthProvider
- `backend/app/api/routes/consumers.py` - Added /google, /google/callback, /set-password endpoints
- `backend/app/alembic/versions/3b27541620fc_add_social_login_fields_to_consumer.py` - Migration for social fields
- `backend/tests/api/routes/test_google_oauth.py` - NEW: 16 tests for Google OAuth

