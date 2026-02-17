# QA Checklist: Story 1.5 - Password Reset via Email

**Story:** Password Reset via Email
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] Backend server is running (`uv run uvicorn app.main:app --reload`)
- [ ] PostgreSQL database is running with migrations applied
- [ ] Email service is configured (or `emails_enabled` is false for local testing)
- [ ] A verified consumer account exists for testing
- [ ] A staff account exists at a seeded gym for testing
- [ ] Access to test email inbox (or check logs if emails disabled)

---

## Environment Setup

### 1. Start Backend Server

```bash
cd /home/ameen/studioloop/backend
uv run uvicorn app.main:app --reload --port 8000
```

- [ ] Server starts without errors
- [ ] API docs available at http://localhost:8000/docs

### 2. Verify Test Data Exists

```bash
# Check for test consumer
curl -s http://localhost:8000/api/v1/auth/consumer/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testconsumer@example.com", "password": "testpassword123"}' | jq
```

- [ ] Test consumer can login (or create one via registration endpoint)

### 3. Note Initial Token Version

```bash
# Login and note the token_version in database for comparison after reset
```

- [ ] Noted initial token_version value: _______

---

## Test Cases

### TC-1: Consumer Forgot Password - Valid Email

**Acceptance Criterion:** #1 - Reset link sent to email

**Steps:**
1. Send forgot password request with valid registered email:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/forgot-password \
     -H "Content-Type: application/json" \
     -d '{"email": "testconsumer@example.com"}'
   ```

2. Check response

3. Check email inbox or server logs for reset email (if emails enabled)

**Expected Results:**
- [ ] Response status is 200 OK
- [ ] Response body contains success message like "If the email exists, a password reset link has been sent"
- [ ] Email is sent (or logged) with reset link containing token

**Actual Results:** _______________

---

### TC-2: Consumer Forgot Password - Invalid Email (No Enumeration)

**Acceptance Criterion:** #5 - Unregistered emails do not reveal account existence

**Steps:**
1. Send forgot password request with non-existent email:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/forgot-password \
     -H "Content-Type: application/json" \
     -d '{"email": "nonexistent@example.com"}'
   ```

2. Compare response with TC-1

**Expected Results:**
- [ ] Response status is 200 OK (same as valid email)
- [ ] Response body is identical to TC-1 (no enumeration)
- [ ] No email is sent for non-existent address

**Actual Results:** _______________

---

### TC-3: Consumer Reset Password - Valid Token

**Acceptance Criterion:** #2, #3 - Can set new password via reset link

**Steps:**
1. Get a valid reset token (from TC-1 email or generate manually for testing)
   ```bash
   # If manually generating for test:
   # TOKEN=$(python -c "from app.utils import generate_password_reset_token; print(generate_password_reset_token('testconsumer@example.com'))")
   ```

2. Reset password with valid token:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/reset-password \
     -H "Content-Type: application/json" \
     -d '{"token": "YOUR_TOKEN_HERE", "new_password": "newpassword123"}'
   ```

3. Verify response

**Expected Results:**
- [ ] Response status is 200 OK
- [ ] Response body contains success message
- [ ] Password is updated in database (hashed with Argon2)

**Actual Results:** _______________

---

### TC-4: Consumer Login with New Password

**Acceptance Criterion:** #3 - New password works for login

**Steps:**
1. Login with the NEW password:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/login \
     -H "Content-Type: application/json" \
     -d '{"email": "testconsumer@example.com", "password": "newpassword123"}'
   ```

2. Verify login succeeds

**Expected Results:**
- [ ] Response status is 200 OK
- [ ] Response contains access_token and refresh_token
- [ ] Can use new password for all future logins

**Actual Results:** _______________

---

### TC-5: Old Sessions Invalidated After Reset

**Acceptance Criterion:** #4 - All existing sessions invalidated

**Steps:**
1. Before reset, save a valid refresh token (from login)

2. Reset password (TC-3)

3. Try to use the OLD refresh token:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "OLD_REFRESH_TOKEN_HERE"}'
   ```

4. Verify token_version was incremented in database

**Expected Results:**
- [ ] Old refresh token returns 401 INVALID_TOKEN
- [ ] token_version in database is incremented (old value + 1)
- [ ] User must login again on all devices

**Actual Results:** _______________

---

### TC-6: Consumer Reset Password - Expired Token

**Acceptance Criterion:** Token validation

**Steps:**
1. Use an expired token (or create one with past expiry for testing)
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/reset-password \
     -H "Content-Type: application/json" \
     -d '{"token": "EXPIRED_TOKEN", "new_password": "newpassword123"}'
   ```

**Expected Results:**
- [ ] Response status is 400 Bad Request
- [ ] Response body contains `code: "INVALID_TOKEN"`
- [ ] Response message is "Invalid or expired reset token"

**Actual Results:** _______________

---

### TC-7: Consumer Reset Password - Invalid Token

**Acceptance Criterion:** Token validation

**Steps:**
1. Use a malformed/random token:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/consumer/reset-password \
     -H "Content-Type: application/json" \
     -d '{"token": "invalid-random-string", "new_password": "newpassword123"}'
   ```

**Expected Results:**
- [ ] Response status is 400 Bad Request
- [ ] Response body contains `code: "INVALID_TOKEN"`
- [ ] Same error message as expired token (no enumeration)

**Actual Results:** _______________

---

### TC-8: Staff Forgot Password - Valid Email

**Acceptance Criterion:** #1 - Staff can also reset password

**Steps:**
1. Send staff forgot password request:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/staff/forgot-password \
     -H "Content-Type: application/json" \
     -d '{"email": "owner@testgym.com"}'
   ```

**Expected Results:**
- [ ] Response status is 200 OK
- [ ] Same response pattern as consumer
- [ ] Email sent to staff address

**Actual Results:** _______________

---

### TC-9: Staff Reset Password - Session Invalidation

**Acceptance Criterion:** #4 - Staff sessions also invalidated

**Steps:**
1. Login as staff, save refresh token
2. Reset staff password via token
3. Verify old refresh token fails
4. Login with new password
5. Verify role is preserved in new tokens

**Expected Results:**
- [ ] Old refresh token fails with 401
- [ ] Can login with new password
- [ ] New tokens contain correct role and gym_id

**Actual Results:** _______________

---

## Edge Cases & Error Scenarios

### EC-1: Password Too Short

**Scenario:** User tries to set password with less than 8 characters

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/consumer/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "VALID_TOKEN", "new_password": "short"}'
```

**Expected:** Validation error (422) for password length

**Result:** _______________

---

### EC-2: Unverified Consumer Forgot Password

**Scenario:** Consumer with unverified email requests password reset

**Test:**
1. Create consumer without verifying email
2. Request password reset for that email

**Expected:** Returns success (no enumeration) but NO email sent

**Result:** _______________

---

### EC-3: Inactive Staff Forgot Password

**Scenario:** Deactivated staff member requests password reset

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "inactive-staff@testgym.com"}'
```

**Expected:** Returns success (no enumeration) but NO email sent

**Result:** _______________

---

## Rollback Steps

If testing fails or you need to reset:

### Full Rollback
```bash
# Reset test user password directly in database (for testing only)
cd /home/ameen/studioloop/backend
uv run python -c "
from app.core.db import engine
from sqlmodel import Session, select
from app.models.consumer import Consumer
from app.core.security import get_password_hash

with Session(engine) as session:
    consumer = session.exec(select(Consumer).where(Consumer.email == 'testconsumer@example.com')).first()
    if consumer:
        consumer.hashed_password = get_password_hash('testpassword123')
        consumer.token_version = 1  # Reset token version
        session.add(consumer)
        session.commit()
        print('Password reset to original')
"
```

### Partial Rollback
```bash
# Just reset token_version to allow old sessions
# (Use database GUI or psql to update token_version = 1)
```

### Environment Cleanup
```bash
# Stop server
# Clear any test data created during testing
```

---

## Sign-Off

### Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-1: Consumer Forgot Password - Valid Email | [ ] Pass / [ ] Fail | |
| TC-2: Consumer Forgot Password - No Enumeration | [ ] Pass / [ ] Fail | |
| TC-3: Consumer Reset Password - Valid Token | [ ] Pass / [ ] Fail | |
| TC-4: Consumer Login with New Password | [ ] Pass / [ ] Fail | |
| TC-5: Old Sessions Invalidated | [ ] Pass / [ ] Fail | |
| TC-6: Consumer Reset - Expired Token | [ ] Pass / [ ] Fail | |
| TC-7: Consumer Reset - Invalid Token | [ ] Pass / [ ] Fail | |
| TC-8: Staff Forgot Password | [ ] Pass / [ ] Fail | |
| TC-9: Staff Reset - Session Invalidation | [ ] Pass / [ ] Fail | |
| EC-1: Password Too Short | [ ] Pass / [ ] Fail | |
| EC-2: Unverified Consumer | [ ] Pass / [ ] Fail | |
| EC-3: Inactive Staff | [ ] Pass / [ ] Fail | |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready to proceed
- [ ] **FAIL** - Issues found, requires dev attention

**Blocking Issues:** _______________

**Non-Blocking Notes:** _______________

**Tested By:** Ameen
**Date:** _______________
**Signature:** _______________

---

## Next Story

Once this story passes QA:
1. Update sprint-status.yaml: `1-5-password-reset-via-email: done`
2. Proceed to Story 1.6: User Profile Management
