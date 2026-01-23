# QA Checklist: Story 1.9 - Google Social Login

**Story:** Google Social Login
**Status:** Pending Testing
**Tester:** _______________
**Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] Backend is running locally (`uv run uvicorn app.main:app --reload`)
- [ ] Google OAuth credentials are configured in `.env`
- [ ] Redis is running (for OAuth state storage)
- [ ] Database migrations are applied

---

## Environment Setup

### 1. Configure Google OAuth Credentials

```bash
# Add to .env (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

- [ ] Credentials are set in `.env`
- [ ] Google Cloud Console has correct redirect URI: `http://localhost:8000/api/v1/auth/consumer/google/callback`

### 2. Start Backend Services

```bash
# Start backend
cd backend && uv run uvicorn app.main:app --reload
```

- [ ] Backend is running on port 8000
- [ ] No startup errors related to OAuth configuration

---

## Test Cases

### TC-1: OAuth Initiation Endpoint

**Acceptance Criterion:** #1 - Google login button initiates OAuth flow

**Steps:**
1. Open browser or use curl
   ```bash
   curl -v http://localhost:8000/api/v1/auth/consumer/google
   ```

2. Observe the response

**Expected Results:**
- [ ] Response is HTTP 302 redirect
- [ ] Location header contains `accounts.google.com`
- [ ] URL includes `state` parameter
- [ ] URL includes `scope` with `openid email profile`
- [ ] URL includes correct `redirect_uri`

**Actual Results:** _______________

---

### TC-2: New User Registration via Google

**Acceptance Criterion:** #1 - Account is created using Google email

**Steps:**
1. Start OAuth flow by visiting:
   ```
   http://localhost:8000/api/v1/auth/consumer/google
   ```

2. Complete Google sign-in with an email NOT in the database

3. Observe the callback response

**Expected Results:**
- [ ] New consumer record is created in database
- [ ] Consumer email matches Google account email
- [ ] `google_id` is set to Google's user ID (sub claim)
- [ ] `is_email_verified` is `true`
- [ ] `auth_provider` is `google`
- [ ] `hashed_password` is `null`
- [ ] JWT tokens are returned (access_token, refresh_token)

**Actual Results:** _______________

---

### TC-3: Profile Photo Import

**Acceptance Criterion:** #2 - Google profile photo is imported (optional)

**Steps:**
1. Register via Google with a Google account that has a profile photo

2. Check the consumer record in database:
   ```sql
   SELECT email, profile_photo_url FROM consumers WHERE google_id IS NOT NULL ORDER BY created_at DESC LIMIT 1;
   ```

**Expected Results:**
- [ ] `profile_photo_url` contains Google profile picture URL
- [ ] URL is accessible and returns an image
- [ ] If user has no Google profile photo, field is null (not error)

**Actual Results:** _______________

---

### TC-4: JWT Token Generation

**Acceptance Criterion:** #3 - Receive JWT tokens as with email login

**Steps:**
1. Complete Google OAuth flow
2. Capture the returned tokens
3. Test access token:
   ```bash
   curl -H "Authorization: Bearer <access_token>" \
        http://localhost:8000/api/v1/auth/consumer/me
   ```

**Expected Results:**
- [ ] Access token is valid JWT
- [ ] Token can be used to access protected endpoints
- [ ] `/auth/consumer/me` returns current user data
- [ ] Refresh token is also returned

**Actual Results:** _______________

---

### TC-5: Add Password for Social User

**Acceptance Criterion:** #4 - Can add password to enable email login

**Steps:**
1. Login via Google (new or existing user)
2. Use the access token to set a password:
   ```bash
   curl -X POST \
        -H "Authorization: Bearer <access_token>" \
        -H "Content-Type: application/json" \
        -d '{"new_password": "MySecurePassword123"}' \
        http://localhost:8000/api/v1/auth/consumer/set-password
   ```

3. Try logging in via email:
   ```bash
   curl -X POST \
        -H "Content-Type: application/json" \
        -d '{"email": "google-user@gmail.com", "password": "MySecurePassword123"}' \
        http://localhost:8000/api/v1/auth/consumer/login
   ```

**Expected Results:**
- [ ] Set password returns success message
- [ ] Email login works with new password
- [ ] Google login still works
- [ ] User now has both login options

**Actual Results:** _______________

---

### TC-6: Existing Email User Linking

**Acceptance Criterion:** #5 - Existing accounts with same email are linked

**Steps:**
1. Create a user via email registration:
   ```bash
   curl -X POST \
        -H "Content-Type: application/json" \
        -d '{"email": "linktest@gmail.com", "password": "TestPassword123", "first_name": "Link", "last_name": "Test"}' \
        http://localhost:8000/api/v1/auth/consumer/register
   ```

2. Verify email (or mark as verified in DB for testing)

3. Login via Google with the SAME email (linktest@gmail.com)

4. Check the database:
   ```sql
   SELECT id, email, google_id, hashed_password FROM consumers WHERE email = 'linktest@gmail.com';
   ```

**Expected Results:**
- [ ] Only ONE consumer record exists (not duplicated)
- [ ] `google_id` is now set on the existing record
- [ ] Original `hashed_password` is preserved
- [ ] User can login via both email and Google

**Actual Results:** _______________

---

## Edge Cases & Error Scenarios

### EC-1: Invalid OAuth State (CSRF Protection)

**Scenario:** Callback with manipulated state parameter

**Test:**
```bash
curl "http://localhost:8000/api/v1/auth/consumer/google/callback?state=invalid-state&code=some-code"
```

**Expected:** 400 Bad Request with `INVALID_OAUTH_STATE` error code

**Result:** _______________

---

### EC-2: Expired OAuth State

**Scenario:** User takes too long to complete Google sign-in (state expires)

**Test:**
1. Start OAuth flow to get state
2. Wait > 10 minutes (or manually delete state from Redis)
3. Complete Google sign-in

**Expected:** 400 Bad Request with `INVALID_OAUTH_STATE` error code

**Result:** _______________

---

### EC-3: Set Password When Already Set

**Scenario:** User with existing password tries to use set-password endpoint

**Test:**
```bash
# Login as email-registered user
curl -X POST \
     -H "Authorization: Bearer <email_user_token>" \
     -H "Content-Type: application/json" \
     -d '{"new_password": "AnotherPassword123"}' \
     http://localhost:8000/api/v1/auth/consumer/set-password
```

**Expected:** 400 Bad Request with `PASSWORD_ALREADY_SET` error code

**Result:** _______________

---

### EC-4: Google Returns No Email

**Scenario:** Google user with no email in their account (rare edge case)

**Test:** Mock scenario or manually test if possible

**Expected:** Handle gracefully with appropriate error

**Result:** _______________

---

### EC-5: Missing OAuth Code

**Scenario:** Callback without authorization code

**Test:**
```bash
curl "http://localhost:8000/api/v1/auth/consumer/google/callback?state=valid-state"
```

**Expected:** 400 or 422 error for missing code parameter

**Result:** _______________

---

## Rollback Steps

If testing fails or you need to reset:

### Full Rollback
```bash
# Revert migration (if created)
cd backend && uv run alembic downgrade -1

# Remove test consumers
psql -d studioloop -c "DELETE FROM consumers WHERE google_id IS NOT NULL;"
```

### Partial Rollback
```bash
# Just clear Google-linked accounts
psql -d studioloop -c "UPDATE consumers SET google_id = NULL WHERE google_id IS NOT NULL;"
```

### Environment Cleanup
```bash
# Clear OAuth states from Redis
redis-cli KEYS "oauth_state:*" | xargs redis-cli DEL
```

---

## Sign-Off

### Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-1: OAuth Initiation | [ ] Pass / [ ] Fail | |
| TC-2: New User Registration | [ ] Pass / [ ] Fail | |
| TC-3: Profile Photo Import | [ ] Pass / [ ] Fail | |
| TC-4: JWT Token Generation | [ ] Pass / [ ] Fail | |
| TC-5: Add Password | [ ] Pass / [ ] Fail | |
| TC-6: Email User Linking | [ ] Pass / [ ] Fail | |
| EC-1: Invalid State | [ ] Pass / [ ] Fail | |
| EC-2: Expired State | [ ] Pass / [ ] Fail | |
| EC-3: Password Already Set | [ ] Pass / [ ] Fail | |
| EC-4: No Email | [ ] Pass / [ ] Fail | |
| EC-5: Missing Code | [ ] Pass / [ ] Fail | |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready to proceed
- [ ] **FAIL** - Issues found, requires dev attention

**Blocking Issues:** _______________

**Non-Blocking Notes:** _______________

**Tested By:** _______________
**Date:** _______________
**Signature:** _______________

---

## Next Story

Once this story passes QA:
1. Update sprint-status.yaml: `1-9-google-social-login: done`
2. Update Story 1.7 (POPIA Account Deletion) to handle social-only users
3. Proceed to Story 1.10: Apple Social Login
