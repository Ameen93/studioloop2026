# QA Checklist: Story 2.1 - Gym Registration and Owner Account

**Story ID:** 2.1
**Story Key:** 2-1-gym-registration-and-owner-account
**Status:** Pending Testing
**Tester:** Ameen
**Date Tested:** _______________

---

## Prerequisites

- [ ] Docker Desktop running
- [ ] Local services started (`docker compose -f docker-compose.local.yml up -d`)
- [ ] Backend virtual environment activated
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Backend server running on `http://localhost:8000`
- [ ] Email testing setup (check Adminer or logs for sent emails)
- [ ] API documentation accessible at `http://localhost:8000/docs`

---

## Environment Setup

```bash
# 1. Start local services
cd /home/ameen/studioloop/backend
docker compose -f docker-compose.local.yml up -d

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Apply migrations
alembic upgrade head

# 4. Start backend server
uvicorn app.main:app --reload

# 5. Verify server is running
curl http://localhost:8000/api/v1/health
```

**Verification:**
- [ ] Health endpoint returns 200
- [ ] PostgreSQL accessible on localhost:5432
- [ ] Adminer accessible at localhost:8080

---

## Test Cases

### TC-1: Successful Gym Registration

**Acceptance Criterion:** #1, #2, #3, #4, #5

**Steps:**
1. Open API docs at `http://localhost:8000/docs`
2. Navigate to `POST /api/v1/auth/gym/register`
3. Execute with the following body:
```json
{
  "email": "owner@testgym.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "gym_name": "Test Fitness Studio",
  "gym_contact_email": "info@testgym.com",
  "gym_contact_phone": "+27821234567"
}
```

**Expected Results:**
- [ ] Response status is 201 Created
- [ ] Response contains `owner_id` (UUID)
- [ ] Response contains `gym_id` (UUID)
- [ ] Response contains `staff_id` (UUID)
- [ ] Response contains `gym_slug` (e.g., "test-fitness-studio")
- [ ] Response contains success message about email verification

**Actual Results:** _______________

---

### TC-2: Consumer Record Created with Owner Role

**Acceptance Criterion:** #1

**Steps:**
1. After TC-1, open Adminer at `http://localhost:8080`
2. Login: System=PostgreSQL, Server=db, User=postgres, Password=changethis, Database=app
3. Query the consumers table:
```sql
SELECT id, email, first_name, last_name, role, is_email_verified
FROM consumers
WHERE email = 'owner@testgym.com';
```

**Expected Results:**
- [ ] Consumer record exists
- [ ] `role` field equals `owner`
- [ ] `is_email_verified` is `false`
- [ ] `first_name` is "John"
- [ ] `last_name` is "Doe"

**Actual Results:** _______________

---

### TC-3: Gym Record Created with Correct Fields

**Acceptance Criterion:** #2, #5

**Steps:**
1. Query the gyms table in Adminer:
```sql
SELECT id, name, slug, contact_email, contact_phone, is_active
FROM gyms
WHERE name = 'Test Fitness Studio';
```

**Expected Results:**
- [ ] Gym record exists with UUID primary key
- [ ] `name` is "Test Fitness Studio"
- [ ] `slug` is "test-fitness-studio" (URL-friendly)
- [ ] `contact_email` is "info@testgym.com"
- [ ] `contact_phone` is "+27821234567"
- [ ] `is_active` is `true`

**Actual Results:** _______________

---

### TC-4: Staff Record Links Owner to Gym

**Acceptance Criterion:** #3

**Steps:**
1. Query the staff table in Adminer:
```sql
SELECT s.id, s.email, s.role, s.gym_id, g.name as gym_name
FROM staff s
JOIN gyms g ON s.gym_id = g.id
WHERE s.email = 'owner@testgym.com';
```

**Expected Results:**
- [ ] Staff record exists
- [ ] `role` equals `owner`
- [ ] `gym_id` matches the gym created in TC-3
- [ ] `email` matches owner email

**Actual Results:** _______________

---

### TC-5: Verification Email Sent

**Acceptance Criterion:** #4

**Steps:**
1. Check backend logs for email sending (if using MailHog or similar):
```bash
# Check backend logs
docker logs studioloop-backend 2>&1 | grep -i email
```
2. Or check the email-templates rendered output

**Expected Results:**
- [ ] Email send attempt logged to `owner@testgym.com`
- [ ] Email contains verification link
- [ ] Email subject mentions verification

**Actual Results:** _______________

---

### TC-6: Duplicate Email Rejected

**Acceptance Criterion:** #1

**Steps:**
1. Try to register with the same email again:
```bash
curl -X POST http://localhost:8000/api/v1/auth/gym/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@testgym.com",
    "password": "AnotherPass123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "gym_name": "Another Gym"
  }'
```

**Expected Results:**
- [ ] Response status is 400
- [ ] Response contains error code `EMAIL_ALREADY_EXISTS`
- [ ] Error message indicates email is already in use
- [ ] No new Consumer, Gym, or Staff records created

**Actual Results:** _______________

---

### TC-7: Unique Slug Generation

**Acceptance Criterion:** #5

**Steps:**
1. Register a new gym with a similar name:
```bash
curl -X POST http://localhost:8000/api/v1/auth/gym/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner2@testgym.com",
    "password": "SecurePass123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "gym_name": "Test Fitness Studio"
  }'
```
2. Check the generated slug in Adminer:
```sql
SELECT name, slug FROM gyms ORDER BY created_at DESC LIMIT 2;
```

**Expected Results:**
- [ ] First gym has slug "test-fitness-studio"
- [ ] Second gym has slug "test-fitness-studio-1" (or similar unique variant)
- [ ] No duplicate slugs exist

**Actual Results:** _______________

---

## Edge Cases and Error Scenarios

### EC-1: Password Too Short

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/gym/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "short@test.com",
    "password": "abc",
    "first_name": "Test",
    "last_name": "User",
    "gym_name": "Short Pass Gym"
  }'
```

**Expected Results:**
- [ ] Response status is 422 (Validation Error)
- [ ] Error indicates password must be at least 8 characters

**Actual Results:** _______________

---

### EC-2: Invalid Email Format

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/gym/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "gym_name": "Invalid Email Gym"
  }'
```

**Expected Results:**
- [ ] Response status is 422 (Validation Error)
- [ ] Error indicates invalid email format

**Actual Results:** _______________

---

### EC-3: Empty Gym Name

**Steps:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/gym/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "empty@test.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "gym_name": ""
  }'
```

**Expected Results:**
- [ ] Response status is 422 (Validation Error)
- [ ] Error indicates gym name is required

**Actual Results:** _______________

---

## Rollback Steps

### Full Rollback

To completely undo all changes from this story:

```bash
# 1. Stop the backend server (Ctrl+C)

# 2. Rollback database migration
cd /home/ameen/studioloop/backend
alembic downgrade -1

# 3. Verify migration rolled back
alembic current

# 4. Clean up test data (if needed)
# Connect to Adminer and run:
# DELETE FROM staff WHERE email LIKE '%testgym%';
# DELETE FROM consumers WHERE email LIKE '%testgym%';
# DELETE FROM gyms WHERE slug LIKE 'test-fitness%';
```

### Partial Rollback - Clean Test Data Only

```sql
-- Run in Adminer
BEGIN;
DELETE FROM staff WHERE email LIKE '%testgym%' OR email LIKE '%test.com';
DELETE FROM consumers WHERE email LIKE '%testgym%' OR email LIKE '%test.com';
DELETE FROM gyms WHERE slug LIKE 'test-fitness%' OR slug LIKE 'another-gym%';
COMMIT;
```

### Environment Cleanup

```bash
# Stop local services
docker compose -f docker-compose.local.yml down

# Remove volumes (full reset)
docker compose -f docker-compose.local.yml down -v
```

---

## Sign-Off Section

### Test Summary

| Test Case | Description | Result |
|-----------|-------------|--------|
| TC-1 | Successful Gym Registration | Pass / Fail |
| TC-2 | Consumer Record with Owner Role | Pass / Fail |
| TC-3 | Gym Record with Correct Fields | Pass / Fail |
| TC-4 | Staff Record Links Owner | Pass / Fail |
| TC-5 | Verification Email Sent | Pass / Fail |
| TC-6 | Duplicate Email Rejected | Pass / Fail |
| TC-7 | Unique Slug Generation | Pass / Fail |
| EC-1 | Password Too Short | Pass / Fail |
| EC-2 | Invalid Email Format | Pass / Fail |
| EC-3 | Empty Gym Name | Pass / Fail |

### Final Verdict

- [ ] **PASS** - All test cases passed, story is complete
- [ ] **FAIL** - One or more critical test cases failed

### Blocking Issues

_List any issues that prevent the story from being accepted:_

1. _______________
2. _______________

### Non-Blocking Notes

_List any minor issues or observations:_

1. _______________
2. _______________

### Sign-Off

**Tester:** _______________
**Date:** _______________
**Signature:** _______________

---

**Next Story:** 2-2-gym-profile-configuration
