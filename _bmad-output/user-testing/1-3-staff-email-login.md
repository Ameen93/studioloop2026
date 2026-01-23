# QA Checklist: Story 1.3 - Staff Email Login

## Header

| Field | Value |
|-------|-------|
| **Story ID** | 1.3 |
| **Story Title** | Staff Email Login |
| **Status** | Pending Testing |
| **Tester** | Ameen |
| **Test Date** | ________________ |

---

## Prerequisites

- [ ] Docker is running (for local PostgreSQL)
- [ ] Backend virtual environment activated
- [ ] Database migrations applied (`uv run alembic upgrade head`)
- [ ] At least one gym exists in the database (from seed data)
- [ ] At least one staff member exists with known credentials
- [ ] API client regenerated after implementation

---

## Environment Setup

### 1. Start Local Services
```bash
cd /home/ameen/studioloop
docker compose -f docker-compose.local.yml up -d
```

**Verification:**
- [ ] PostgreSQL running on port 5432
- [ ] Redis running on port 6379

### 2. Apply Migrations
```bash
cd backend
uv run alembic upgrade head
```

**Verification:**
- [ ] `staff` table exists in database
- [ ] No migration errors

### 3. Seed Test Data (if needed)
```bash
cd backend
uv run python -m scripts.seed
```

**Verification:**
- [ ] Staff members created for test gyms
- [ ] At least one owner, manager, front_desk, instructor exists

### 4. Start Backend Server
```bash
cd backend
uv run fastapi dev app/main.py
```

**Verification:**
- [ ] Server running on http://localhost:8000
- [ ] OpenAPI docs available at http://localhost:8000/docs

---

## Test Cases

### TC-1: Successful Staff Login with Owner Role

**Acceptance Criterion:** #1 - Staff receives JWT with role claims

**Steps:**
1. Get a staff member email/password with `owner` role from seed data
2. Send login request:
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@testgym.com", "password": "testpassword123"}'
```

**Expected Results:**
- [ ] Response status: 200 OK
- [ ] Response contains `access_token` (non-empty string)
- [ ] Response contains `refresh_token` (non-empty string)
- [ ] Response contains `token_type: "bearer"`
- [ ] Response contains `role: "owner"`
- [ ] Response contains `gym_id` (valid UUID)

**Actual Results:** ________________

---

### TC-2: JWT Contains Role and Gym ID Claims

**Acceptance Criterion:** #1, #2 - Token includes role and gym_id

**Steps:**
1. Use the access token from TC-1
2. Decode the JWT (use jwt.io or similar):
```bash
# Extract the token payload (middle part of JWT)
echo "YOUR_ACCESS_TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null
```

**Expected Results:**
- [ ] Payload contains `sub` (staff ID)
- [ ] Payload contains `type: "access"`
- [ ] Payload contains `role` matching the staff's role
- [ ] Payload contains `gym_id` matching the staff's gym

**Actual Results:** ________________

---

### TC-3: Login with Different Staff Roles

**Acceptance Criterion:** #1 - Different roles receive correct claims

**Steps:**
Test login for each role type:

**Manager:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@testgym.com", "password": "testpassword123"}'
```
- [ ] Returns `role: "manager"`

**Front Desk:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "frontdesk@testgym.com", "password": "testpassword123"}'
```
- [ ] Returns `role: "front_desk"`

**Instructor:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "instructor@testgym.com", "password": "testpassword123"}'
```
- [ ] Returns `role: "instructor"`

**Actual Results:** ________________

---

### TC-4: Invalid Credentials - Wrong Password

**Acceptance Criterion:** #1 - Invalid credentials return 401

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@testgym.com", "password": "wrongpassword"}'
```

**Expected Results:**
- [ ] Response status: 401 Unauthorized
- [ ] Response body contains `code: "INVALID_CREDENTIALS"`
- [ ] Response body contains `message: "Invalid email or password"`
- [ ] No token returned

**Actual Results:** ________________

---

### TC-5: Invalid Credentials - Nonexistent Email

**Acceptance Criterion:** #1 - Same error for nonexistent email (no enumeration)

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "doesnotexist@testgym.com", "password": "anypassword123"}'
```

**Expected Results:**
- [ ] Response status: 401 Unauthorized
- [ ] Response body contains `code: "INVALID_CREDENTIALS"`
- [ ] Same error message as wrong password (no email enumeration)

**Actual Results:** ________________

---

### TC-6: Inactive Staff Cannot Login

**Acceptance Criterion:** #5 - Inactive staff accounts cannot login

**Prerequisites:**
- Set a staff member's `is_active` to `false` in database

**Steps:**
1. Deactivate a staff member:
```sql
UPDATE staff SET is_active = false WHERE email = 'test_inactive@testgym.com';
```

2. Attempt login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test_inactive@testgym.com", "password": "testpassword123"}'
```

**Expected Results:**
- [ ] Response status: 401 Unauthorized
- [ ] Response body contains `code: "INVALID_CREDENTIALS"`
- [ ] Same error as invalid password (no status enumeration)

**Actual Results:** ________________

---

### TC-7: Staff Table Structure

**Acceptance Criterion:** #4 - staff table created with gym_id FK

**Steps:**
Check database schema:
```sql
\d staff
```
Or via Adminer at http://localhost:8080

**Expected Results:**
- [ ] Table `staff` exists
- [ ] Column `id` (UUID, primary key)
- [ ] Column `gym_id` (UUID, foreign key to gyms)
- [ ] Column `email` (varchar, indexed)
- [ ] Column `hashed_password` (varchar)
- [ ] Column `first_name` (varchar)
- [ ] Column `last_name` (varchar)
- [ ] Column `role` (enum: owner, manager, front_desk, instructor)
- [ ] Column `phone` (varchar, nullable)
- [ ] Column `is_active` (boolean, default true)
- [ ] Column `is_email_verified` (boolean, default false)
- [ ] Column `created_at` (timestamptz)
- [ ] Column `updated_at` (timestamptz)
- [ ] Foreign key constraint on `gym_id` referencing `gyms.id`

**Actual Results:** ________________

---

### TC-8: Validation - Short Password

**Acceptance Criterion:** Input validation

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@testgym.com", "password": "short"}'
```

**Expected Results:**
- [ ] Response status: 422 Unprocessable Entity
- [ ] Validation error for password length

**Actual Results:** ________________

---

### TC-9: Validation - Invalid Email Format

**Acceptance Criterion:** Input validation

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "not-an-email", "password": "testpassword123"}'
```

**Expected Results:**
- [ ] Response status: 422 Unprocessable Entity
- [ ] Validation error for email format

**Actual Results:** ________________

---

## Edge Cases and Error Scenarios

### EC-1: Consumer Email Used for Staff Login

**Scenario:** User tries to login as staff using consumer email

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email": "consumer@example.com", "password": "consumerpassword"}'
```

**Expected:**
- [ ] Returns 401 (staff table doesn't have consumer emails)

---

### EC-2: Staff Token Used as Bearer

**Scenario:** Verify staff token works as bearer for authenticated endpoints

**Steps:**
1. Login as staff and get access token
2. Use token on an authenticated endpoint:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_STAFF_TOKEN"
```

**Expected:**
- [ ] Token is accepted as valid bearer token
- [ ] OR returns appropriate error if endpoint is consumer-only

---

### EC-3: Refresh Token Cannot Be Used as Bearer

**Scenario:** Verify refresh token is rejected as bearer

**Steps:**
1. Login as staff and get refresh token
2. Try to use refresh token as bearer:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

**Expected:**
- [ ] Returns 403 Forbidden (token type validation)

---

## Rollback Steps

### Full Rollback
```bash
# Revert migration
cd backend
uv run alembic downgrade -1

# Remove staff_auth router from api/main.py (manual)

# Revert security.py changes (git checkout)
git checkout -- app/core/security.py

# Remove staff model
rm app/models/staff.py
```

### Partial Rollback - Just Routes
```bash
# Remove staff_auth import from api/main.py
# Delete app/api/routes/staff_auth.py
```

### Environment Cleanup
```bash
# Stop local services
docker compose -f docker-compose.local.yml down

# Clear test data (if needed)
docker compose -f docker-compose.local.yml down -v  # WARNING: Deletes all data
```

---

## Sign-Off Section

### Test Summary

| Test Case | Result |
|-----------|--------|
| TC-1: Successful Login (Owner) | ⬜ PASS / ⬜ FAIL |
| TC-2: JWT Claims | ⬜ PASS / ⬜ FAIL |
| TC-3: Different Roles | ⬜ PASS / ⬜ FAIL |
| TC-4: Wrong Password | ⬜ PASS / ⬜ FAIL |
| TC-5: Nonexistent Email | ⬜ PASS / ⬜ FAIL |
| TC-6: Inactive Staff | ⬜ PASS / ⬜ FAIL |
| TC-7: Table Structure | ⬜ PASS / ⬜ FAIL |
| TC-8: Short Password | ⬜ PASS / ⬜ FAIL |
| TC-9: Invalid Email | ⬜ PASS / ⬜ FAIL |
| EC-1: Consumer as Staff | ⬜ PASS / ⬜ FAIL |
| EC-2: Staff Bearer Token | ⬜ PASS / ⬜ FAIL |
| EC-3: Refresh Token Rejected | ⬜ PASS / ⬜ FAIL |

### Final Verdict

- [ ] **PASS** - All test cases passed, story complete
- [ ] **FAIL** - One or more blocking issues found

### Blocking Issues

________________

### Non-Blocking Notes

________________

### Signature

**Tester:** ________________
**Date:** ________________

---

### Next Story Reference

After this story is complete, proceed to:
- **Story 1.4: JWT Token Refresh** - Automatic token refresh for seamless sessions
