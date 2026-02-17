# Story 1.2: Consumer Email Login

Status: done

## Story

As a **consumer**,
I want to login with my email and password,
so that I can access my account.

## Acceptance Criteria

1. **Given** I have a verified consumer account
   **When** I enter correct email and password
   **Then** I receive a JWT access token (<24h expiry) and refresh token

2. **And** tokens are stored securely in MMKV (mobile) / memory (web)

3. **And** I am redirected to the home screen

4. **And** invalid credentials return 401 with error message (error code: `INVALID_CREDENTIALS`)

5. **And** unverified accounts cannot login (error code: `EMAIL_NOT_VERIFIED`)

## Tasks / Subtasks

- [x] Task 1: Create consumer login endpoint (AC: #1, #4, #5)
  - [x] 1.1 Add `POST /auth/consumer/login` route to `consumers.py`
  - [x] 1.2 Validate email exists and password matches (use `verify_password`)
  - [x] 1.3 Check `is_email_verified` flag - reject if false
  - [x] 1.4 Generate JWT access token with consumer ID as subject
  - [x] 1.5 Generate refresh token (longer expiry, stored in DB or stateless)
  - [x] 1.6 Return token response with `access_token`, `refresh_token`, `token_type`

- [x] Task 2: Add refresh token support (AC: #1)
  - [x] 2.1 Add `REFRESH_TOKEN_EXPIRE_DAYS` setting to config (default: 7 days)
  - [x] 2.2 Create `create_refresh_token()` function in security.py
  - [x] 2.3 Add token type claim to differentiate access vs refresh tokens

- [x] Task 3: Update token models and schemas (AC: #1)
  - [x] 3.1 Create `ConsumerToken` response schema (access_token, refresh_token, token_type)
  - [x] 3.2 Create `ConsumerLoginRequest` schema (email, password)

- [x] Task 4: Create web login screen (AC: #2, #3)
  - [x] 4.1 Create `apps/web/src/routes/auth/Login.tsx` component
  - [x] 4.2 Add form with email and password fields
  - [x] 4.3 Use generated API client mutation for login
  - [x] 4.4 Store tokens in memory/localStorage (web)
  - [x] 4.5 Redirect to home screen on success
  - [x] 4.6 Display error messages for invalid credentials / unverified

- [x] Task 5: Create mobile login screen (AC: #2, #3)
  - [x] 5.1 Create `apps/consumer-mobile/app/(auth)/login.tsx` screen
  - [x] 5.2 Add form with email and password fields
  - [x] 5.3 Store tokens in MMKV (NOT AsyncStorage per architecture)
  - [x] 5.4 Navigate to home screen on success
  - [x] 5.5 Display error messages

- [x] Task 6: Add routing for login (AC: #3)
  - [x] 6.1 Update `App.tsx` to add `/auth/login` route
  - [x] 6.2 Update default redirect to /auth/login
  - [x] 6.3 Update mobile index.tsx to redirect to login

- [x] Task 7: Add tests (AC: all)
  - [x] 7.1 Backend: Test successful login returns tokens
  - [x] 7.2 Backend: Test invalid credentials returns 401
  - [x] 7.3 Backend: Test unverified account returns 403
  - [x] 7.4 Backend: Test nonexistent email returns 401 (same as invalid)
  - [x] 7.5 Regenerate API client with new login endpoint

## Dev Notes

### Architecture Compliance

- **ARCH-10**: Custom JWT (FastAPI native) - already implemented
- **ARCH-11**: Password verification with Argon2 (backward compatible with bcrypt)
- **ARCH-12**: JWT access (<24h) + refresh rotation
- **ARCH-24**: All API/DB fields use `snake_case`
- **ARCH-28**: Standard error response format with code, message, details

### Current Codebase State

**Consumer routes EXIST at `backend/app/api/routes/consumers.py`:**
- `POST /auth/consumer/register` - Creates consumer with Argon2 password
- `GET /auth/consumer/verify-email` - Verifies email token
- `POST /auth/consumer/resend-verification` - Resends verification email
- **NEED TO ADD**: `POST /auth/consumer/login`

**Security module EXISTS at `backend/app/core/security.py`:**
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Supports both Argon2 (new) and bcrypt (legacy)
    if hashed_password.startswith("$argon2"):
        return password_hasher.verify(plain_password, hashed_password)
    if hashed_password.startswith("$2"):
        return _legacy_pwd_context.verify(plain_password, hashed_password)
    return False

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
```

**Config settings at `backend/app/core/config.py`:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # Currently 8 days - SHOULD reduce to <24h
```

**Frontend registration screens EXIST:**
- Web: `apps/web/src/routes/auth/Register.tsx`
- Mobile: `apps/consumer-mobile/app/(auth)/register.tsx`
- Both use TanStack Query mutations

### Critical Implementation Details

#### Token Configuration (ARCH-12)

**Update `config.py` settings:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours max per architecture
REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days for refresh tokens
```

#### Login Endpoint Implementation

**Add to `consumers.py`:**
```python
from app.core.security import verify_password, create_access_token, needs_rehash, get_password_hash

@router.post("/login", response_model=ConsumerToken)
def login_consumer(
    session: SessionDep,
    login_data: ConsumerLoginRequest,
) -> ConsumerToken:
    """Authenticate consumer and return tokens."""
    consumer = session.exec(
        select(Consumer).where(Consumer.email == login_data.email)
    ).first()

    # Always use same error to prevent email enumeration
    if not consumer or not verify_password(login_data.password, consumer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )

    # Check email verification
    if not consumer.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "EMAIL_NOT_VERIFIED",
                "message": "Please verify your email before logging in",
                "details": {"email": consumer.email},
            },
        )

    # Upgrade password hash if using legacy bcrypt
    if needs_rehash(consumer.hashed_password):
        consumer.hashed_password = get_password_hash(login_data.password)
        session.add(consumer)
        session.commit()

    # Generate tokens
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

#### Token Schemas

**Add to `consumer.py` models:**
```python
class ConsumerLoginRequest(SQLModel):
    """Consumer login request."""
    email: EmailStr
    password: str = Field(min_length=8)


class ConsumerToken(SQLModel):
    """Token response for consumer authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

#### Refresh Token Function

**Add to `security.py`:**
```python
def create_refresh_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create a JWT refresh token.

    Refresh tokens have longer expiry and include a type claim
    to differentiate from access tokens.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",  # Distinguish from access tokens
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
```

#### Web Login Screen

**Create `apps/web/src/routes/auth/Login.tsx`:**
```typescript
import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { useMutation } from '@tanstack/react-query';
import { consumerAuthLoginConsumer } from '@sl/api-client';

export function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState<string | null>(null);

  const loginMutation = useMutation({
    mutationFn: (data: { email: string; password: string }) =>
      consumerAuthLoginConsumer({ body: data }),
    onSuccess: (response) => {
      // Store tokens (for now in localStorage, will update in Token Refresh story)
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      navigate('/'); // Navigate to home
    },
    onError: (error) => {
      const err = error as { body?: { detail?: { code?: string; message?: string } } };
      if (err?.body?.detail?.code === 'EMAIL_NOT_VERIFIED') {
        setError('Please verify your email before logging in');
      } else {
        setError('Invalid email or password');
      }
    },
  });

  // Form implementation...
}
```

#### Mobile Login Screen with MMKV

**Critical: Use MMKV, NOT AsyncStorage (per architecture)**

**Install MMKV:**
```bash
cd frontend
pnpm --filter @sl/consumer-mobile add react-native-mmkv
```

**Create `apps/consumer-mobile/app/(auth)/login.tsx`:**
```typescript
import { useState } from 'react';
import { router } from 'expo-router';
import { useMutation } from '@tanstack/react-query';
import { MMKV } from 'react-native-mmkv';
import { consumerAuthLoginConsumer } from '@sl/api-client';

const storage = new MMKV();

export default function LoginScreen() {
  const loginMutation = useMutation({
    mutationFn: (data: { email: string; password: string }) =>
      consumerAuthLoginConsumer({ body: data }),
    onSuccess: (response) => {
      // Store tokens in MMKV (NOT AsyncStorage!)
      storage.set('access_token', response.data.access_token);
      storage.set('refresh_token', response.data.refresh_token);
      router.replace('/'); // Navigate to home
    },
  });
  // ... form implementation
}
```

### Project Structure Notes

Files to modify/create:
```
backend/
├── app/
│   ├── api/routes/
│   │   └── consumers.py           # ADD: login endpoint
│   ├── core/
│   │   ├── config.py              # ADD: REFRESH_TOKEN_EXPIRE_DAYS
│   │   └── security.py            # ADD: create_refresh_token
│   └── models/
│       └── consumer.py            # ADD: ConsumerLoginRequest, ConsumerToken
├── tests/
│   └── api/routes/
│       └── test_consumers.py      # ADD: login tests

frontend/
├── apps/
│   ├── web/src/routes/auth/
│   │   ├── Login.tsx              # NEW: Web login screen
│   │   └── Register.tsx           # UPDATE: Link to login
│   └── consumer-mobile/app/(auth)/
│       ├── login.tsx              # NEW: Mobile login screen
│       └── register.tsx           # UPDATE: Link to login
```

### Testing Requirements

**Backend tests (`tests/api/routes/test_consumers.py`):**
1. `test_login_success` - Valid credentials return tokens
2. `test_login_invalid_password` - Returns 401 INVALID_CREDENTIALS
3. `test_login_invalid_email` - Returns 401 INVALID_CREDENTIALS (same error)
4. `test_login_unverified` - Returns 403 EMAIL_NOT_VERIFIED
5. `test_login_rehashes_bcrypt` - Legacy bcrypt hashes upgraded to Argon2

### What NOT to Do

- **DO NOT** reveal whether email exists in login errors (security)
- **DO NOT** use AsyncStorage on mobile - use MMKV per architecture
- **DO NOT** set access token expiry > 24 hours (ARCH-12)
- **DO NOT** store tokens in Zustand - use MMKV/localStorage
- **DO NOT** use camelCase in API request/response - use `snake_case`

### Previous Story Intelligence

From Story 1.1 completion:
- Password verification with `verify_password()` supports both Argon2 and bcrypt
- `needs_rehash()` function exists to detect legacy bcrypt hashes
- Consumer model has `is_email_verified` field for verification check
- TanStack Query mutations pattern established for registration
- Error response format with `code`, `message`, `details` already implemented

### Git Intelligence

Recent commits show:
- Consumer registration fully implemented with email verification
- Password hashing migrated to Argon2 with bcrypt backward compatibility
- API client regeneration works with `pnpm --filter @sl/api-client generate`

### Dependencies on Previous Stories

- Story 1-1: Consumer registration and email verification (COMPLETE)
- Consumer model with `is_email_verified` field (EXISTS)
- Password verification with Argon2/bcrypt support (EXISTS)
- TanStack Query setup in frontend apps (EXISTS)

### References

- [Source: epics.md#Story 1.2]
- [Source: architecture.md#ARCH-10 (Auth Strategy)]
- [Source: architecture.md#ARCH-11 (Password Hashing)]
- [Source: architecture.md#ARCH-12 (Token Management)]
- [Source: project-context.md#Offline-First Patterns (MMKV)]
- [Source: backend/app/api/routes/consumers.py - Existing registration routes]
- [Source: backend/app/core/security.py - Password verification]
- [Source: story 1-1-consumer-email-registration.md - Previous implementation]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None - implementation proceeded without issues.

### Completion Notes List

1. **Backend Login Endpoint**: Added `POST /auth/consumer/login` with full validation, email enumeration prevention, and legacy bcrypt password rehashing support.

2. **Token Configuration**: Reduced `ACCESS_TOKEN_EXPIRE_MINUTES` from 8 days to 24 hours (ARCH-12 compliance). Added `REFRESH_TOKEN_EXPIRE_DAYS = 7`.

3. **Token Type Claims**: Both `create_access_token` and `create_refresh_token` now include a `type` claim ("access" or "refresh") to differentiate tokens.

4. **Mobile Storage**: Used `createMMKV()` from react-native-mmkv v4 (NOT AsyncStorage per architecture). Note: MMKV v4 exports `createMMKV()` function instead of `MMKV` class constructor.

5. **Web Storage**: Tokens stored in localStorage (will be moved to memory with auth context in future token refresh story).

6. **Tests**: 5 login tests added covering success, invalid password, nonexistent email, unverified account, and password validation.

7. **Default Route Changed**: App now defaults to login page (`/auth/login`) instead of registration.

### File List

**Backend (Modified):**
- `backend/app/core/config.py` - Added `REFRESH_TOKEN_EXPIRE_DAYS`, reduced access token expiry
- `backend/app/core/security.py` - Added `create_refresh_token()`, added type claims to tokens
- `backend/app/models/consumer.py` - Added `ConsumerLoginRequest`, `ConsumerToken` schemas
- `backend/app/api/routes/consumers.py` - Added `POST /auth/consumer/login` endpoint
- `backend/tests/api/routes/test_consumers.py` - Added `TestConsumerLogin` class with 5 tests

**Frontend (Modified/Created):**
- `frontend/apps/web/src/routes/auth/Login.tsx` - NEW: Web login screen
- `frontend/apps/web/src/App.tsx` - Added login route, changed default redirect
- `frontend/apps/web/src/App.test.tsx` - Updated tests for login as default
- `frontend/apps/consumer-mobile/app/(auth)/login.tsx` - NEW: Mobile login with MMKV
- `frontend/apps/consumer-mobile/app/index.tsx` - Changed redirect to login
- `frontend/packages/api-client/src/generated/` - Regenerated with login endpoint
