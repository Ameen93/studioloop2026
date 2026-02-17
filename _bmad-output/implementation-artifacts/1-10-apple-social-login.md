# Story 1.10: Apple Social Login

Status: done

## Story

As an **iOS consumer**,
I want to register/login with my Apple ID,
So that I can use Sign in with Apple for privacy.

## Acceptance Criteria

1. **Given** the Apple login button on iOS auth screens
   **When** I authenticate with Apple
   **Then** a consumer account is created using Apple-provided email (real or relay)

2. **And** I receive JWT tokens (same as email/Google login)

3. **And** Hide My Email relay addresses are supported

4. **And** Apple login meets App Store requirements

5. **And** existing accounts with same email are linked (not duplicated)

## Tasks / Subtasks

- [x] Task 1: Add Apple Sign In configuration (AC: #1, #4)
  - [x] 1.1 Add Apple config to `core/config.py`: `APPLE_CLIENT_ID`, `APPLE_TEAM_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY`
  - [x] 1.2 Add `APPLE_REDIRECT_URI` for callback URL
  - [x] 1.3 Register Apple OAuth client in `backend/app/core/oauth.py`
  - [x] 1.4 Update `.env.example` with Apple Sign In environment variables (N/A - no .env.example in project)

- [x] Task 2: Create Apple OAuth initiation endpoint (AC: #1, #4)
  - [x] 2.1 Create `GET /auth/consumer/apple` endpoint in `consumers.py`
  - [x] 2.2 Generate OAuth state token via SessionMiddleware (CSRF protection)
  - [x] 2.3 Return redirect URL to Apple's authorization endpoint
  - [x] 2.4 Include scopes: `name`, `email`
  - [x] 2.5 Include `response_mode=form_post` (Apple requirement)

- [x] Task 3: Create Apple OAuth callback endpoint (AC: #1, #2, #3, #5)
  - [x] 3.1 Create `POST /auth/consumer/apple/callback` endpoint (Apple uses POST for form_post)
  - [x] 3.2 Validate OAuth state token via SessionMiddleware (CSRF protection)
  - [x] 3.3 Exchange authorization code for tokens using client secret JWT
  - [x] 3.4 Decode and verify Apple ID token to extract user info (sub, email)
  - [x] 3.5 Handle Apple's "Hide My Email" relay addresses (AC #3)
  - [x] 3.6 Check if consumer exists by `apple_id` OR `email`:
    - If by `apple_id`: Login existing user
    - If by `email` with no `apple_id`: Link Apple to existing account
    - If not found: Create new consumer
  - [x] 3.7 Handle first-login name extraction (Apple only sends name on first auth)
  - [x] 3.8 Generate JWT tokens (access + refresh) using existing `create_access_token`
  - [x] 3.9 Mark account as email verified (Apple verified it)
  - [x] 3.10 Return JSON with tokens (API-style auth)
  - [x] 3.11 Block inactive/deactivated consumers (same as Google flow)

- [x] Task 4: Add backend tests for Apple OAuth (AC: #1-5)
  - [x] 4.1 Test Apple OAuth initiation returns redirect URL
  - [x] 4.2 Test OAuth callback creates new user for unknown Apple ID
  - [x] 4.3 Test OAuth callback links to existing user with same email
  - [x] 4.4 Test OAuth callback logs in existing Apple-linked user
  - [x] 4.5 Test OAuth callback returns valid JWT tokens
  - [x] 4.6 Test OAuth callback marks email as verified
  - [x] 4.7 Test Hide My Email relay addresses are accepted
  - [x] 4.8 Test invalid OAuth state returns error
  - [x] 4.9 Test inactive consumer is blocked from Apple login

## Dev Notes

### Architecture Compliance

- **ARCH-14**: Social Login uses Authlib for Apple integration (same as Google)
- **ARCH-11**: Passwords hashed with Argon2 when added to social accounts
- **ARCH-12**: JWT tokens with <24h expiry, same as email/Google login
- **ARCH-28**: Standard error response format with code, message, details
- **FR1**: Users can register using social login (Apple)

### Apple Sign In vs Google OAuth - Key Differences

| Aspect | Google | Apple |
|--------|--------|-------|
| **Response Mode** | Query params (GET callback) | Form POST (POST callback) |
| **Client Secret** | Static secret | JWT signed with private key |
| **User Info** | Always in token response | Name only on FIRST auth |
| **Email** | Always real email | May be relay address (@privaterelay.appleid.com) |
| **Server Metadata** | OpenID Connect discovery | Manual configuration needed |

### Apple Sign In Client Secret Generation

Apple requires a JWT client secret signed with your private key:

```python
import jwt
import time

def generate_apple_client_secret() -> str:
    """Generate Apple client secret JWT.

    Apple requires a JWT signed with ES256 algorithm using your private key.
    The JWT expires after 6 months maximum (Apple requirement).
    """
    headers = {
        "kid": settings.APPLE_KEY_ID,
        "alg": "ES256",
    }

    payload = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + (86400 * 180),  # 180 days max
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID,
    }

    return jwt.encode(
        payload,
        settings.APPLE_PRIVATE_KEY,
        algorithm="ES256",
        headers=headers,
    )
```

### Apple OAuth Registration in oauth.py

```python
# Register Apple OAuth client
# Apple requires manual configuration (no OpenID discovery)
if settings.APPLE_CLIENT_ID and settings.APPLE_PRIVATE_KEY:
    oauth.register(
        name="apple",
        client_id=settings.APPLE_CLIENT_ID,
        client_secret="",  # Generated dynamically
        authorize_url="https://appleid.apple.com/auth/authorize",
        access_token_url="https://appleid.apple.com/auth/token",
        client_kwargs={
            "scope": "name email",
            "response_mode": "form_post",  # Apple requires POST callback
        },
    )
```

### Config Values to Add

**Add to `backend/app/core/config.py`:**
```python
# Apple Sign In (ARCH-14)
APPLE_CLIENT_ID: str = ""  # Service ID (e.g., com.studioloop.app)
APPLE_TEAM_ID: str = ""  # Team ID from Apple Developer account
APPLE_KEY_ID: str = ""  # Key ID for private key
APPLE_PRIVATE_KEY: str = ""  # Contents of .p8 private key file
APPLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/consumer/apple/callback"
```

**Add to `.env.example`:**
```
# Apple Sign In
APPLE_CLIENT_ID=com.studioloop.app
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
APPLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/consumer/apple/callback
```

### Apple ID Token Decoding

Apple returns an ID token that must be decoded to get user info:

```python
# Decode Apple ID token (signature verification optional for server-to-server)
decoded = jwt.decode(
    id_token,
    options={"verify_signature": False},  # Apple's public keys rotate
)

apple_id = decoded.get("sub")  # Unique Apple user identifier
email = decoded.get("email")  # May be relay address
email_verified = decoded.get("email_verified", "false") == "true"
is_private_email = decoded.get("is_private_email", "false") == "true"
```

### Handling Hide My Email (AC #3)

Apple's Hide My Email feature provides relay addresses like:
`abc123def@privaterelay.appleid.com`

These addresses:
- Forward to the user's real email
- Are unique per app/service
- Must be supported (don't reject them)
- Can be detected via `is_private_email` claim

```python
# Check if email is a relay address
is_relay = email.endswith("@privaterelay.appleid.com") or is_private_email

# Always accept relay emails - they work for sending notifications
# Store is_private_email flag if needed for analytics
```

### First-Login Name Handling

Apple only provides the user's name on the FIRST authorization:

```python
# User data from Apple callback (POST body)
user_data = request.form.get("user")  # JSON string, only on first auth

if user_data:
    import json
    user = json.loads(user_data)
    first_name = user.get("name", {}).get("firstName", "")
    last_name = user.get("name", {}).get("lastName", "")
else:
    # Subsequent logins - no name provided
    first_name = "Apple"
    last_name = "User"
```

### POST Callback Implementation

Apple uses `response_mode=form_post`, so callback is a POST:

```python
@router.post("/apple/callback", response_model=ConsumerToken)
async def apple_callback(
    request: Request,
    session: SessionDep,
) -> ConsumerToken:
    """Handle Apple OAuth callback (POST with form data)."""
    form_data = await request.form()

    code = form_data.get("code")
    state = form_data.get("state")
    id_token = form_data.get("id_token")  # May be included directly
    user_data = form_data.get("user")  # JSON, only on first auth

    # ... rest of implementation
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

Error codes specific to Apple:
- `OAUTH_NOT_CONFIGURED`: Apple Sign In not configured
- `INVALID_OAUTH_STATE`: Invalid or expired state token
- `OAUTH_TOKEN_FAILED`: Failed to exchange code for tokens
- `OAUTH_USER_INFO_FAILED`: Failed to decode Apple ID token
- `OAUTH_NO_EMAIL`: Apple account has no email (shouldn't happen)
- `ACCOUNT_DEACTIVATED`: Consumer account is deactivated

### What NOT to Do

- **DO NOT** reject `@privaterelay.appleid.com` emails (AC #3)
- **DO NOT** expect user name on every login (only first auth)
- **DO NOT** use GET for callback (Apple uses form_post)
- **DO NOT** hardcode client secret (must be generated JWT)
- **DO NOT** skip state validation (CSRF protection required)
- **DO NOT** allow inactive consumers to login (block like Google flow)
- **DO NOT** store Apple's access token long-term (only use for initial auth)
- **DO NOT** expose Apple private key in frontend code

### Previous Story Learnings (from Story 1.9)

From the Google OAuth implementation:
1. **Enum handling**: Use `native_enum=False` with SQLAlchemy to avoid PostgreSQL enum mismatches
2. **Import location**: Import `oauth` inside the endpoint functions from `app.core.oauth`
3. **Inactive users**: Always check `is_active` before generating tokens
4. **Test mocking**: Mock at `app.core.oauth.oauth` not at the consumer routes module
5. **SessionMiddleware**: Already added for Google OAuth, reuse for Apple

### Project Structure Notes

Files to create/modify:
```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # UPDATE: Add APPLE_* config values
│   │   └── oauth.py           # UPDATE: Add Apple OAuth client registration
│   └── api/routes/
│       └── consumers.py       # UPDATE: Add /apple, /apple/callback endpoints
└── tests/api/routes/
    └── test_apple_oauth.py    # NEW: Apple OAuth tests
```

Note: Consumer model already has `apple_id` field from Story 1.9 migration.

### Dependencies

- PyJWT is already installed (used for general JWT operations)
- Authlib is already installed from Story 1.9
- SessionMiddleware already configured in main.py

### Apple Developer Console Setup

To test locally, configure in Apple Developer account:
1. Go to https://developer.apple.com/account/
2. Go to "Certificates, Identifiers & Profiles"
3. Create an App ID (if not exists)
4. Create a Services ID (this is your `APPLE_CLIENT_ID`)
5. Enable "Sign in with Apple" for the Services ID
6. Configure redirect URLs: `http://localhost:8000/api/v1/auth/consumer/apple/callback`
7. Create a Key for Sign in with Apple
8. Download the `.p8` private key file
9. Copy Team ID, Key ID, and private key contents to `.env`

### Testing Notes

Since Apple Sign In requires:
- Valid Apple Developer account
- Configured Services ID
- Valid private key

Tests should mock the Authlib responses similar to Google OAuth tests.

### References

- [Source: epics.md#Story 1.10 - Apple Social Login]
- [Source: architecture.md - ARCH-14 Social Login with Authlib]
- [Source: 1-9-google-social-login.md - Previous OAuth implementation]
- [Source: Apple Sign In Documentation - https://developer.apple.com/sign-in-with-apple/]
- [Source: Authlib Documentation - https://docs.authlib.org/]
- [Source: Apple Sign In Gist - https://gist.github.com/aamishbaloch/2f0e5d94055e1c29c0585d2f79a8634e]

---

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

- All 4 tasks completed successfully
- 16 Apple OAuth tests created (15 passed, 1 skipped when Apple OAuth not configured)
- Implementation follows same patterns as Google OAuth (Story 1.9)
- Key Apple-specific features: POST callback, JWT client secret, Hide My Email support, first-login name extraction

### File List

- `backend/app/core/config.py` - Added APPLE_* config values (APPLE_CLIENT_ID, APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_PRIVATE_KEY, APPLE_REDIRECT_URI)
- `backend/app/core/oauth.py` - Added Apple OAuth client registration and generate_apple_client_secret() function
- `backend/app/api/routes/consumers.py` - Added GET /apple and POST /apple/callback endpoints
- `backend/tests/api/routes/test_apple_oauth.py` - NEW: 16 tests for Apple OAuth flow

