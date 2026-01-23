# QA Checklist: Story 1.7 - POPIA Account Deletion

**Story ID:** 1.7
**Story Title:** POPIA Account Deletion
**Status:** Pending Testing
**Tester:** Ameen
**Test Date:** _______________

---

## Prerequisites

Before starting testing, ensure the following are in place:

- [ ] Backend server is running (`uv run uvicorn app.main:app --reload`)
- [ ] PostgreSQL database is running and migrated
- [ ] Test consumer account exists with verified email
- [ ] Email service is configured (or SMTP_HOST set for testing)
- [ ] API client available (curl, httpie, or Postman)

---

## Environment Setup

### 1. Start the Backend Server

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verification:** Server responds at http://localhost:8000/docs

- [ ] OpenAPI docs accessible
- [ ] DELETE /api/v1/auth/consumer/me endpoint visible in docs

### 2. Create Test Consumer (if not exists)

```bash
# Register a new consumer
curl -X POST "http://localhost:8000/api/v1/auth/consumer/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "deletion-test@example.com",
    "password": "testpassword123",
    "first_name": "Delete",
    "last_name": "TestUser"
  }'
```

**Verification:**
- [ ] Response status 201 Created
- [ ] Consumer created with `is_email_verified: false`

### 3. Verify Consumer Email (for testing)

```bash
# Direct database update for testing (or use verification endpoint if available)
# In psql:
UPDATE consumers SET is_email_verified = true WHERE email = 'deletion-test@example.com';
```

### 4. Login to Get Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/consumer/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "deletion-test@example.com",
    "password": "testpassword123"
  }'
```

**Store the access_token:** `export TOKEN="<access_token_from_response>"`

- [ ] Login successful (200 OK)
- [ ] Access token received

---

## Test Cases

### TC-1: Successful Account Deletion

**Acceptance Criterion:** #1 - Account is marked for deletion when confirmed

**Steps:**

1. Ensure you have a valid access token
2. Execute deletion request:

```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/consumer/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "testpassword123"}'
```

**Expected Results:**

- [ ] Response status: 200 OK
- [ ] Response body contains success message about deletion scheduled
- [ ] Message mentions 30-day timeline

**Actual Results:** _______________________

---

### TC-2: Consumer Record Soft-Deleted

**Acceptance Criterion:** #1 - Account marked for deletion

**Steps:**

1. After TC-1, check database directly:

```sql
SELECT id, email, is_active, deleted_at, deletion_requested_at, token_version
FROM consumers
WHERE email = 'deletion-test@example.com';
```

**Expected Results:**

- [ ] `is_active` = false
- [ ] `deleted_at` is NOT NULL (has timestamp)
- [ ] `deletion_requested_at` is NOT NULL (has timestamp)
- [ ] `token_version` incremented from original value

**Actual Results:** _______________________

---

### TC-3: Confirmation Email Sent

**Acceptance Criterion:** #2 - Receive confirmation email

**Steps:**

1. Check email inbox for deletion-test@example.com
2. OR check email logs/mailhog if using test SMTP

**Expected Results:**

- [ ] Email received with subject containing "Account Deletion"
- [ ] Email body mentions 30-day data removal timeline
- [ ] Email includes contact info for reversal request

**Actual Results:** _______________________

---

### TC-4: Deleted Consumer Cannot Login

**Acceptance Criterion:** #6 - Cannot login again

**Steps:**

1. Attempt to login with deleted account:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/consumer/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "deletion-test@example.com",
    "password": "testpassword123"
  }'
```

**Expected Results:**

- [ ] Response status: 401 Unauthorized
- [ ] Error code: "INVALID_CREDENTIALS"
- [ ] Error message is generic (does NOT reveal account was deleted)

**Actual Results:** _______________________

---

### TC-5: Existing Tokens Invalidated

**Acceptance Criterion:** #6 - Logged out

**Steps:**

1. Use the old access token (from before deletion):

```bash
curl -X GET "http://localhost:8000/api/v1/auth/consumer/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Results:**

- [ ] Response status: 401 Unauthorized
- [ ] Token no longer works after deletion

**Actual Results:** _______________________

---

### TC-6: Deletion with Wrong Password Fails

**Acceptance Criterion:** Security requirement

**Steps:**

1. Create another test consumer and login
2. Attempt deletion with wrong password:

```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/consumer/me" \
  -H "Authorization: Bearer $NEW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "wrongpassword"}'
```

**Expected Results:**

- [ ] Response status: 401 Unauthorized
- [ ] Error code: "INVALID_CREDENTIALS"
- [ ] Account is NOT deleted (verify in database)

**Actual Results:** _______________________

---

### TC-7: Deletion Without Authentication Fails

**Acceptance Criterion:** Security requirement

**Steps:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/consumer/me" \
  -H "Content-Type: application/json" \
  -d '{"password": "testpassword123"}'
```

**Expected Results:**

- [ ] Response status: 401 Unauthorized
- [ ] Request rejected without valid token

**Actual Results:** _______________________

---

## Edge Cases and Error Scenarios

### EC-1: Deletion with Empty Password

```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/consumer/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": ""}'
```

**Expected:** 422 Validation Error (password too short)

- [ ] Passes

---

### EC-2: Deletion Without Password Field

```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/consumer/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected:** 422 Validation Error (password required)

- [ ] Passes

---

### EC-3: Double Deletion Attempt

1. Delete account successfully
2. Try to delete again with same token

**Expected:** 401 Unauthorized (token invalidated)

- [ ] Passes

---

## Rollback Steps

### Full Rollback: Restore Deleted Account

```sql
-- In PostgreSQL
UPDATE consumers
SET
  is_active = true,
  deleted_at = NULL,
  deletion_requested_at = NULL
WHERE email = 'deletion-test@example.com';
```

### Partial Rollback: Reset Token Version

```sql
UPDATE consumers
SET token_version = 1
WHERE email = 'deletion-test@example.com';
```

### Environment Cleanup

```sql
-- Remove test consumers
DELETE FROM consumers WHERE email LIKE '%deletion-test%';
```

---

## Sign-Off

### Test Results Summary

| Test Case | Pass/Fail |
|-----------|-----------|
| TC-1: Successful Deletion | |
| TC-2: Record Soft-Deleted | |
| TC-3: Confirmation Email | |
| TC-4: Cannot Login | |
| TC-5: Tokens Invalidated | |
| TC-6: Wrong Password Fails | |
| TC-7: No Auth Fails | |
| EC-1: Empty Password | |
| EC-2: Missing Password | |
| EC-3: Double Deletion | |

### Final Verdict

- [ ] **PASS** - All test cases pass, story meets acceptance criteria
- [ ] **FAIL** - One or more blocking issues found

### Blocking Issues

_______________________
_______________________

### Non-Blocking Notes

_______________________
_______________________

### Sign-Off

**Tester Signature:** _______________________
**Date:** _______________________

---

**Next Story:** 1-8-role-based-access-control
