# QA Checklist: Story 1.8 - Role-Based Access Control

**Story ID:** 1.8
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

- [ ] Backend server running locally (`uv run uvicorn app.main:app --reload`)
- [ ] PostgreSQL database running with migrations applied
- [ ] At least one gym created with seed data
- [ ] Staff accounts for different roles (owner, manager, front_desk, instructor)
- [ ] Consumer account for cross-role testing
- [ ] API testing tool (curl, HTTPie, or Postman)

---

## Environment Setup

```bash
# Terminal 1: Start the backend server
cd /home/ameen/studioloop/backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Verify server is running
curl http://localhost:8000/api/v1/utils/health-check/
# Expected: {"status": "healthy"}
```

### Get Test Tokens

```bash
# Login as staff OWNER
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@testgym.com", "password": "testpassword123"}'
# Save the access_token as OWNER_TOKEN

# Login as staff MANAGER
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@testgym.com", "password": "testpassword123"}'
# Save the access_token as MANAGER_TOKEN

# Login as staff FRONT_DESK
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "frontdesk@testgym.com", "password": "testpassword123"}'
# Save the access_token as FRONTDESK_TOKEN

# Login as CONSUMER
curl -X POST http://localhost:8000/api/v1/auth/consumer/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@studioloop.com", "password": "testpassword123"}'
# Save the access_token as CONSUMER_TOKEN
```

---

## Test Cases

### TC-1: Owner Can Access Owner-Only Routes
**Acceptance Criterion:** #1, #2

**Steps:**
1. Use OWNER_TOKEN to access an owner-only protected route
2. Observe the response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/owner-only" \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 200
- [ ] Response body confirms access granted
- [ ] No error in response

**Actual Results:** _______________

---

### TC-2: Manager Can Access Manager-Or-Above Routes
**Acceptance Criterion:** #1, #2

**Steps:**
1. Use MANAGER_TOKEN to access a manager-or-above protected route
2. Observe the response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/manager-or-above" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 200
- [ ] Response body confirms access granted

**Actual Results:** _______________

---

### TC-3: Front Desk Cannot Access Owner-Only Routes
**Acceptance Criterion:** #2, #5

**Steps:**
1. Use FRONTDESK_TOKEN to access an owner-only protected route
2. Observe the error response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/owner-only" \
  -H "Authorization: Bearer $FRONTDESK_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 403
- [ ] Error code is "FORBIDDEN"
- [ ] Error message indicates insufficient permissions
- [ ] Response includes `required_roles` in details

**Actual Results:** _______________

---

### TC-4: Front Desk Cannot Access Manager Routes
**Acceptance Criterion:** #2, #5

**Steps:**
1. Use FRONTDESK_TOKEN to access a manager-or-above protected route
2. Observe the error response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/manager-or-above" \
  -H "Authorization: Bearer $FRONTDESK_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 403
- [ ] Error code is "FORBIDDEN"

**Actual Results:** _______________

---

### TC-5: Staff Can Access Own Gym Routes
**Acceptance Criterion:** #3

**Steps:**
1. Get the gym_id from the staff's token or profile
2. Use staff token to access gym-scoped route with matching gym_id

```bash
# First get staff profile to see gym_id
curl -X GET "http://localhost:8000/api/v1/auth/staff/me" \
  -H "Authorization: Bearer $OWNER_TOKEN"
# Note the gym_id

# Access gym-scoped route with matching gym_id
curl -X GET "http://localhost:8000/api/v1/rbac/gyms/{GYM_ID}/staff-area" \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 200
- [ ] Access granted to own gym

**Actual Results:** _______________

---

### TC-6: Staff Cannot Access Other Gym Routes
**Acceptance Criterion:** #3

**Steps:**
1. Get a different gym_id (or use a random UUID)
2. Use staff token to access gym-scoped route with mismatched gym_id

```bash
# Use a different gym_id than the staff belongs to
curl -X GET "http://localhost:8000/api/v1/rbac/gyms/00000000-0000-0000-0000-000000000000/staff-area" \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 403
- [ ] Error code is "FORBIDDEN"
- [ ] Message indicates "Access denied to this gym"
- [ ] Error does not leak gym details

**Actual Results:** _______________

---

### TC-7: Consumer Cannot Access Staff Routes
**Acceptance Criterion:** #4

**Steps:**
1. Use CONSUMER_TOKEN to access a staff-protected route
2. Observe the error response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/staff-only" \
  -H "Authorization: Bearer $CONSUMER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 401 (not 403)
- [ ] Error indicates invalid token (consumer is not staff)
- [ ] No staff data leaked

**Actual Results:** _______________

---

### TC-8: Owner Inherits Manager Permissions
**Acceptance Criterion:** #1

**Steps:**
1. Use OWNER_TOKEN to access manager-level route
2. Observe the response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/manager-or-above" \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 200
- [ ] Owner can access manager-level features

**Actual Results:** _______________

---

### TC-9: Manager Inherits Front Desk Permissions
**Acceptance Criterion:** #1

**Steps:**
1. Use MANAGER_TOKEN to access front_desk-level route
2. Observe the response

```bash
curl -X GET "http://localhost:8000/api/v1/rbac/any-staff" \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

**Expected Results:**
- [ ] Response status code is 200
- [ ] Manager can access front_desk-level features

**Actual Results:** _______________

---

## Edge Cases and Error Scenarios

### EC-1: No Authorization Header
```bash
curl -X GET "http://localhost:8000/api/v1/rbac/owner-only"
```

**Expected:**
- [ ] Response status code is 401
- [ ] Error indicates missing credentials

---

### EC-2: Invalid Token Format
```bash
curl -X GET "http://localhost:8000/api/v1/rbac/owner-only" \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected:**
- [ ] Response status code is 401
- [ ] Error indicates invalid token

---

### EC-3: Expired Token
**Steps:** Use a token that has expired (wait for expiry or use test expired token)

**Expected:**
- [ ] Response status code is 401
- [ ] Error indicates token expired or invalid

---

## Rollback Steps

### Full Rollback
If RBAC implementation needs to be reverted:

```bash
# Revert to previous commit (before RBAC changes)
git checkout HEAD~1 -- backend/app/api/deps.py

# Remove new files
rm backend/app/api/routes/rbac_examples.py
rm backend/tests/api/test_rbac.py

# Restart server
```

### Partial Rollback
To disable RBAC on specific routes:
- Remove `dependencies=[RequireOwner]` from route decorators
- Remove `_role_check` parameter dependencies

### Environment Cleanup
```bash
# No database changes to rollback for this story
# Just code changes
```

---

## Sign-Off Section

### Test Summary

| Test Case | Status |
|-----------|--------|
| TC-1: Owner access owner route | Pass / Fail |
| TC-2: Manager access manager route | Pass / Fail |
| TC-3: Front desk blocked from owner route | Pass / Fail |
| TC-4: Front desk blocked from manager route | Pass / Fail |
| TC-5: Staff access own gym | Pass / Fail |
| TC-6: Staff blocked from other gym | Pass / Fail |
| TC-7: Consumer blocked from staff route | Pass / Fail |
| TC-8: Owner inherits manager permissions | Pass / Fail |
| TC-9: Manager inherits front desk permissions | Pass / Fail |
| EC-1: No auth header | Pass / Fail |
| EC-2: Invalid token | Pass / Fail |
| EC-3: Expired token | Pass / Fail |

### Final Verdict

- [ ] **PASS** - All test cases passed, story accepted
- [ ] **FAIL** - One or more test cases failed

### Blocking Issues
_List any issues that prevent acceptance:_

### Non-Blocking Notes
_List any observations or minor issues:_

### Sign-Off

**Tester Signature:** _______________
**Date:** _______________

**Next Story:** 1-9-google-social-login
