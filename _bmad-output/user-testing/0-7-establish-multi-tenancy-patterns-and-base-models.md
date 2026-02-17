# QA Checklist: Story 0.7 - Establish Multi-Tenancy Patterns and Base Models

**Story ID:** 0.7
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## 1. Prerequisites

Before testing, ensure the following are ready:

- [ ] Python 3.11+ installed
- [ ] PostgreSQL 16 running (via Docker Compose)
- [ ] Backend virtual environment activated
- [ ] Database migrations applied
- [ ] Backend server running at `http://localhost:8000`

---

## 2. Environment Setup

### 2.1 Start Infrastructure
```bash
cd /home/ameen/studioloop
docker compose up -d
```
**Verification:** PostgreSQL container is running
- [ ] `docker ps` shows postgres container healthy

### 2.2 Apply Migrations
```bash
cd /home/ameen/studioloop/backend
uv run alembic upgrade head
```
**Verification:** No errors during migration
- [ ] Migration completes successfully
- [ ] Tables `gyms`, `consumers`, `spaces` exist in database

### 2.3 Start Backend Server
```bash
cd /home/ameen/studioloop/backend
uv run uvicorn app.main:app --reload
```
**Verification:** Server starts without errors
- [ ] Server running at http://localhost:8000
- [ ] `/health` endpoint returns `{"status": "healthy"}`

---

## 3. Test Cases

### TC-1: Base Model Structure (AC #1, #5, #6)

**Acceptance Criterion:** `app/models/base.py` defines `BaseModel` with UUID primary key, `created_at`, `updated_at`

**Steps:**
1. Open file `backend/app/models/base.py`
2. Verify `BaseModel` class exists
3. Check for required fields

**Expected Results:**
- [ ] File `backend/app/models/base.py` exists
- [ ] `BaseModel` class is defined
- [ ] `id` field is UUID type with `default_factory=uuid4`
- [ ] `created_at` field is datetime with index
- [ ] `updated_at` field is datetime
- [ ] All field names use snake_case (not camelCase)

**Actual Results:** _______________

---

### TC-2: GymScopedModel Mixin (AC #2)

**Acceptance Criterion:** `app/models/base.py` defines `GymScopedModel` mixin with `gym_id` foreign key

**Steps:**
1. Open file `backend/app/models/base.py`
2. Locate `GymScopedModel` class
3. Verify `gym_id` foreign key configuration

**Expected Results:**
- [ ] `GymScopedModel` class is defined
- [ ] `gym_id` field is UUID type
- [ ] `gym_id` has `foreign_key="gyms.id"`
- [ ] `gym_id` has index for performance

**Actual Results:** _______________

---

### TC-3: Gym Dependency Injection (AC #3)

**Acceptance Criterion:** `app/core/dependencies.py` provides `get_current_gym()` dependency

**Steps:**
1. Open file `backend/app/api/deps.py`
2. Locate `get_current_gym` function
3. Check for `GymDep` annotated type

**Expected Results:**
- [ ] `get_current_gym()` function exists
- [ ] Function accepts `gym_id: UUID` parameter
- [ ] Function validates gym exists (returns 404 if not)
- [ ] `GymDep` type alias is defined

**Actual Results:** _______________

---

### TC-4: Repository Base Class with Tenant Filtering (AC #4)

**Acceptance Criterion:** Repository base class automatically filters by `gym_id` for gym-scoped models

**Steps:**
1. Open file `backend/app/repositories/base.py`
2. Verify `BaseRepository` class
3. Verify `GymScopedRepository` class with tenant filtering

**Expected Results:**
- [ ] `BaseRepository` class with CRUD operations exists
- [ ] `GymScopedRepository` class exists
- [ ] `get_multi()` method includes `gym_id` filter
- [ ] `get()` method validates tenant access
- [ ] `create()` method sets `gym_id` automatically

**Actual Results:** _______________

---

### TC-5: Naming Convention Compliance (AC #5)

**Acceptance Criterion:** Naming conventions follow snake_case per ARCH-24

**Steps:**
1. Check database tables via psql or pgAdmin
2. Verify all table and column names

```bash
# Connect to database
docker exec -it studioloop-db psql -U postgres -d app

# List tables
\dt

# Describe gyms table
\d gyms
```

**Expected Results:**
- [ ] Table names are snake_case, plural: `gyms`, `consumers`, `spaces`
- [ ] Column names are snake_case: `gym_id`, `created_at`, `updated_at`
- [ ] Foreign keys follow `{table}_id` pattern
- [ ] No camelCase anywhere in schema

**Actual Results:** _______________

---

### TC-6: UUID Primary Keys (AC #6)

**Acceptance Criterion:** All IDs use UUIDs per ARCH-27

**Steps:**
1. Create a test gym via API or direct insert
2. Verify ID format

```bash
curl -X POST http://localhost:8000/api/v1/gyms \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Gym", "slug": "test-gym"}'
```

**Expected Results:**
- [ ] Gym ID is UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- [ ] ID is not an auto-increment integer
- [ ] All related models use UUID primary keys

**Actual Results:** _______________

---

### TC-7: Error Response Format (AC #7)

**Acceptance Criterion:** API error response format matches architecture specification

**Steps:**
1. Trigger a 404 error (non-existent gym)
2. Trigger a 400 validation error
3. Verify response structure

```bash
# 404 error test
curl http://localhost:8000/api/v1/gyms/00000000-0000-0000-0000-000000000000

# 400 validation error test (if endpoint exists)
curl -X POST http://localhost:8000/api/v1/gyms \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Results:**
- [ ] Error response has `{"error": {...}}` wrapper
- [ ] Error object contains `code` field (machine-readable)
- [ ] Error object contains `message` field (human-readable)
- [ ] Error object contains optional `details` field

**Example expected format:**
```json
{
  "error": {
    "code": "GYM_NOT_FOUND",
    "message": "Gym not found",
    "details": { "gym_id": "00000000-0000-0000-0000-000000000000" }
  }
}
```

**Actual Results:** _______________

---

## 4. Edge Cases and Error Scenarios

### EC-1: Cross-Tenant Access Prevention

**Steps:**
1. Create two gyms (Gym A and Gym B)
2. Create a space under Gym A
3. Attempt to access the space with Gym B's context

**Expected:**
- [ ] Access is denied or 404 returned
- [ ] No data leakage across tenants

**Actual Results:** _______________

---

### EC-2: Missing gym_id Validation

**Steps:**
1. Attempt to create a gym-scoped resource without gym_id
2. Verify validation error

**Expected:**
- [ ] 400 or 422 validation error returned
- [ ] Clear error message about missing gym_id

**Actual Results:** _______________

---

### EC-3: Invalid UUID Format

**Steps:**
1. Send request with malformed UUID

```bash
curl http://localhost:8000/api/v1/gyms/not-a-uuid
```

**Expected:**
- [ ] 400 or 422 validation error
- [ ] Clear error message about invalid UUID format

**Actual Results:** _______________

---

## 5. Rollback Steps

### 5.1 Full Rollback

To completely undo Story 0.7 changes:

```bash
# Rollback migrations
cd /home/ameen/studioloop/backend
uv run alembic downgrade -1  # Or specific revision

# Revert code changes
git checkout HEAD -- backend/app/models/
git checkout HEAD -- backend/app/repositories/
git checkout HEAD -- backend/app/schemas/
git checkout HEAD -- backend/app/core/exceptions.py
git checkout HEAD -- backend/app/api/deps.py
```

### 5.2 Partial Rollback (Models Only)

```bash
# Remove new model files
rm -rf backend/app/models/base.py
rm -rf backend/app/models/gym.py
rm -rf backend/app/models/consumer.py
rm -rf backend/app/models/space.py
```

### 5.3 Environment Cleanup

```bash
# Stop and remove containers
docker compose down

# Remove test data (if needed)
docker volume rm studioloop_postgres-data
```

---

## 6. Sign-Off Section

### Test Results Summary

| Test Case | Result |
|-----------|--------|
| TC-1: Base Model Structure | [ ] PASS / [ ] FAIL |
| TC-2: GymScopedModel Mixin | [ ] PASS / [ ] FAIL |
| TC-3: Gym Dependency Injection | [ ] PASS / [ ] FAIL |
| TC-4: Repository Tenant Filtering | [ ] PASS / [ ] FAIL |
| TC-5: Naming Convention Compliance | [ ] PASS / [ ] FAIL |
| TC-6: UUID Primary Keys | [ ] PASS / [ ] FAIL |
| TC-7: Error Response Format | [ ] PASS / [ ] FAIL |
| EC-1: Cross-Tenant Prevention | [ ] PASS / [ ] FAIL |
| EC-2: Missing gym_id Validation | [ ] PASS / [ ] FAIL |
| EC-3: Invalid UUID Format | [ ] PASS / [ ] FAIL |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready for merge
- [ ] **FAIL** - Blocking issues found, requires rework

### Blocking Issues

_______________________________________________________________

### Non-Blocking Notes

_______________________________________________________________

### Signature

**Tester:** _______________
**Date:** _______________

### Next Story

After this story passes, proceed to:
- **Story 0.8:** Create Seed Data Scripts
