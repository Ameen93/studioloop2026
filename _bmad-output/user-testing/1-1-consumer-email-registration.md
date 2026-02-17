# QA Checklist: Story 1.1 - Consumer Email Registration

**Story ID:** 1.1
**Story Title:** Consumer Email Registration
**Status:** Pending Testing
**Tester:** Ameen
**Test Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] Docker Desktop running (for local PostgreSQL + Redis)
- [ ] Backend server running at `http://localhost:8000`
- [ ] Frontend dev server running at `http://localhost:5173`
- [ ] Database migrated with latest schema (`uv run alembic upgrade head`)
- [ ] Seed data populated (`uv run python scripts/seed.py`)
- [ ] Email configuration set up (or using console output for dev)
- [ ] API documentation accessible at `http://localhost:8000/docs`

---

## Environment Setup

```bash
# Terminal 1: Start Docker services
cd /home/ameen/studioloop
docker compose -f docker-compose.local.yml up -d

# Terminal 2: Start backend
cd backend
uv run alembic upgrade head  # Ensure migrations are applied
uv run uvicorn app.main:app --reload

# Terminal 3: Start frontend web app
cd frontend
pnpm --filter @sl/web dev

# Verify services are running
curl http://localhost:8000/health  # Should return {"status": "ok"}
```

---

## Test Cases

### TC-1: Successful Consumer Registration

**Acceptance Criterion:** #1, #2, #6

**Steps:**
1. Open `http://localhost:5173/register` in browser
2. Enter the following test data:
   - Email: `newuser@example.com`
   - Password: `SecurePass123`
   - First Name: `Test`
   - Last Name: `User`
3. Click "Register" button
4. Observe the response

**Expected Results:**
- [ ] Form submits without client-side errors
- [ ] User is redirected to "Verify your email" screen
- [ ] No error toast/message is displayed
- [ ] Backend console shows email being sent (or email received if SMTP configured)

**Actual Results:**
_____________________________________________________

---

### TC-2: Password Hashed with Argon2

**Acceptance Criterion:** #2

**Steps:**
1. After TC-1 completes, open Adminer at `http://localhost:8080`
2. Login: Server=`postgres`, Username=`postgres`, Password=`postgres`, Database=`app`
3. Navigate to `consumers` table
4. Find the newly registered user
5. Inspect the `hashed_password` column

**Expected Results:**
- [ ] Password hash starts with `$argon2id$` (Argon2 identifier)
- [ ] Password is NOT stored in plaintext
- [ ] Password hash is different from the input password

**Actual Results:**
_____________________________________________________

---

### TC-3: Email Verification Received

**Acceptance Criterion:** #3

**Steps:**
1. Check backend console logs for email content (if using console output)
2. OR check email inbox for `newuser@example.com`
3. Locate the verification email
4. Note the verification link/token

**Expected Results:**
- [ ] Email was sent to the registered email address
- [ ] Email contains a verification link
- [ ] Link format: `http://localhost:5173/verify-email?token=xxx`
- [ ] Token is a valid JWT string

**Actual Results:**
_____________________________________________________

---

### TC-4: Email Verification Successful

**Acceptance Criterion:** #4

**Steps:**
1. Copy the verification link from TC-3
2. Open the verification link in browser
3. OR call the API directly:
   ```bash
   curl "http://localhost:8000/auth/verify-email?token=YOUR_TOKEN_HERE"
   ```
4. Check the database for `is_email_verified` status

**Expected Results:**
- [ ] Verification endpoint returns success response
- [ ] User is redirected to login page (if using web)
- [ ] Database shows `is_email_verified = true` for the user
- [ ] User can now proceed to login

**Actual Results:**
_____________________________________________________

---

### TC-5: Duplicate Email Rejection

**Acceptance Criterion:** #5

**Steps:**
1. Open `http://localhost:5173/register`
2. Enter the same email used in TC-1: `newuser@example.com`
3. Fill in password and name fields
4. Click "Register"

**Expected Results:**
- [ ] Registration fails
- [ ] Error message displays: "An account with this email already exists"
- [ ] Error response code is `EMAIL_ALREADY_EXISTS`
- [ ] No duplicate record created in database

**API Verification:**
```bash
curl -X POST http://localhost:8000/auth/consumer/register \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "password": "AnotherPass123", "first_name": "Dup", "last_name": "User"}'
```

**Expected API Response:**
```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "An account with this email already exists",
    "details": { "field": "email" }
  }
}
```

**Actual Results:**
_____________________________________________________

---

### TC-6: Invalid Email Format Validation

**Acceptance Criterion:** #1 (input validation)

**Steps:**
1. Open registration page
2. Enter invalid email: `not-an-email`
3. Fill other fields correctly
4. Attempt to submit

**Expected Results:**
- [ ] Client-side validation shows email format error
- [ ] Form does not submit to backend
- [ ] Error message indicates invalid email format

**API Verification:**
```bash
curl -X POST http://localhost:8000/auth/consumer/register \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "password": "SecurePass123", "first_name": "Test", "last_name": "User"}'
```

**Expected:** 422 Validation Error

**Actual Results:**
_____________________________________________________

---

### TC-7: Password Too Short Validation

**Acceptance Criterion:** #1 (password min 8 chars)

**Steps:**
1. Open registration page
2. Enter valid email: `shortpwd@example.com`
3. Enter short password: `abc123` (6 chars)
4. Fill name fields
5. Attempt to submit

**Expected Results:**
- [ ] Client-side validation shows password length error
- [ ] Form does not submit with password < 8 characters
- [ ] Error message indicates minimum password length

**API Verification:**
```bash
curl -X POST http://localhost:8000/auth/consumer/register \
  -H "Content-Type: application/json" \
  -d '{"email": "shortpwd@example.com", "password": "abc123", "first_name": "Test", "last_name": "User"}'
```

**Expected:** 422 Validation Error with password length message

**Actual Results:**
_____________________________________________________

---

### TC-8: Cannot Login Without Verification

**Acceptance Criterion:** #4

**Steps:**
1. Register a new user: `unverified@example.com`
2. Do NOT click the verification link
3. Attempt to login with the new credentials

**Expected Results:**
- [ ] Login is rejected
- [ ] Error message indicates email not verified
- [ ] User is prompted to check email for verification

**Actual Results:**
_____________________________________________________

---

## Edge Cases and Error Scenarios

### EC-1: Empty Form Submission

**Steps:**
1. Open registration page
2. Click Register without filling any fields

**Expected Results:**
- [ ] All required fields show validation errors
- [ ] Form does not submit
- [ ] Clear indication of which fields are required

**Actual Results:**
_____________________________________________________

---

### EC-2: SQL Injection Attempt

**Steps:**
```bash
curl -X POST http://localhost:8000/auth/consumer/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123", "first_name": "Robert'\''); DROP TABLE consumers;--", "last_name": "User"}'
```

**Expected Results:**
- [ ] Request is handled safely (no SQL injection)
- [ ] Either validation error OR user created with escaped name
- [ ] Database table is NOT affected

**Actual Results:**
_____________________________________________________

---

### EC-3: Very Long Input Handling

**Steps:**
```bash
curl -X POST http://localhost:8000/auth/consumer/register \
  -H "Content-Type: application/json" \
  -d '{"email": "longname@example.com", "password": "SecurePass123", "first_name": "'$(python3 -c "print('A'*500))"'", "last_name": "User"}'
```

**Expected Results:**
- [ ] Validation error for exceeding max length
- [ ] No database corruption
- [ ] Clear error message about field length

**Actual Results:**
_____________________________________________________

---

## Rollback Steps

### Full Rollback: Remove All Story 1.1 Changes

If testing reveals critical issues requiring full rollback:

```bash
# 1. Stop services
docker compose -f docker-compose.local.yml down

# 2. Revert database migration (if migration was created)
cd backend
uv run alembic downgrade -1

# 3. Restore previous code state
git checkout HEAD -- backend/app/core/security.py
git checkout HEAD -- backend/app/models/consumer.py
git checkout HEAD -- backend/app/api/routes/consumers.py
git checkout HEAD -- frontend/apps/web/src/routes/auth/

# 4. Restart services
docker compose -f docker-compose.local.yml up -d
```

### Partial Rollback: Reset Test Data Only

```bash
cd backend
uv run python scripts/seed.py --reset
```

### Environment Cleanup

```bash
# Remove test users from database
docker exec -it studioloop-postgres-1 psql -U postgres -d app -c "DELETE FROM consumers WHERE email LIKE '%@example.com';"

# Clear Redis cache
docker exec -it studioloop-redis-1 redis-cli FLUSHALL
```

---

## Sign-Off Section

### Test Summary

| Test Case | Status |
|-----------|--------|
| TC-1: Successful Registration | [ ] PASS / [ ] FAIL |
| TC-2: Argon2 Password Hash | [ ] PASS / [ ] FAIL |
| TC-3: Email Verification Sent | [ ] PASS / [ ] FAIL |
| TC-4: Email Verification Works | [ ] PASS / [ ] FAIL |
| TC-5: Duplicate Email Rejected | [ ] PASS / [ ] FAIL |
| TC-6: Invalid Email Validation | [ ] PASS / [ ] FAIL |
| TC-7: Password Length Validation | [ ] PASS / [ ] FAIL |
| TC-8: Cannot Login Unverified | [ ] PASS / [ ] FAIL |
| EC-1: Empty Form | [ ] PASS / [ ] FAIL |
| EC-2: SQL Injection | [ ] PASS / [ ] FAIL |
| EC-3: Long Input | [ ] PASS / [ ] FAIL |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready for next story
- [ ] **FAIL** - Blocking issues found, requires fixes

### Blocking Issues

_List any issues that prevent story acceptance:_

1. _______________________________________________
2. _______________________________________________

### Non-Blocking Notes

_Minor issues or suggestions for improvement:_

1. _______________________________________________
2. _______________________________________________

### Sign-Off

**Tester Signature:** ________________________
**Date:** ________________________

### Next Story

Upon successful completion, proceed to: **Story 1.2 - Consumer Email Login**

---

_Generated by BMad Method create-story workflow - 2026-01-23_
