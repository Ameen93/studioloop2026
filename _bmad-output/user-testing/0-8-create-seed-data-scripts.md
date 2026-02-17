# QA Checklist: Story 0.8 - Create Seed Data Scripts

**Story ID:** 0.8
**Story Title:** Create Seed Data Scripts
**Status:** Pending Testing
**Tester:** Ameen
**Date Tested:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] PostgreSQL database is running locally (Docker Compose)
- [ ] Backend virtual environment is activated
- [ ] Database migrations have been applied
- [ ] No critical data in local database (or backed up)

**Environment Check Commands:**
```bash
# Verify Docker services running
docker compose -f docker-compose.local.yml ps

# Verify database connection
cd backend && uv run python -c "from app.core.db import engine; print('DB connected!')"
```

---

## Environment Setup

1. Start local services (if not running):
```bash
cd /home/ameen/studioloop
docker compose -f docker-compose.local.yml up -d
```

2. Apply any pending migrations:
```bash
cd backend
uv run alembic upgrade head
```

3. Verify clean state (optional):
```bash
# Connect to database and check table counts
docker exec -it studioloop-db psql -U app -d app -c "SELECT COUNT(*) FROM gyms;"
docker exec -it studioloop-db psql -U app -d app -c "SELECT COUNT(*) FROM consumers;"
docker exec -it studioloop-db psql -U app -d app -c "SELECT COUNT(*) FROM spaces;"
```

---

## Test Cases

### TC-1: Basic Seed Execution
**Acceptance Criterion:** AC #1, #2, #8

**Steps:**
1. Navigate to backend directory:
```bash
cd /home/ameen/studioloop/backend
```

2. Run the seed script:
```bash
uv run python scripts/seed.py
```

**Expected Results:**
- [ ] Script executes without errors
- [ ] Output shows summary of seeded entities
- [ ] No duplicate key errors (idempotent)

**Actual Results:**
_________________________________________________

---

### TC-2: Verify Gyms Seeded
**Acceptance Criterion:** AC #1

**Steps:**
1. Query the gyms table:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT name, slug, city, province FROM gyms;"
```

**Expected Results:**
- [ ] 3-5 gyms exist with realistic SA names
- [ ] Gyms have SA city names (Johannesburg, Cape Town, etc.)
- [ ] Gyms have correct province values (Gauteng, Western Cape, etc.)
- [ ] Each gym has a unique slug

**Actual Results:**
_________________________________________________

---

### TC-3: Verify Consumers Seeded
**Acceptance Criterion:** AC #2

**Steps:**
1. Query the consumers table:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT full_name, email, phone FROM consumers LIMIT 10;"
```

2. Verify test consumer exists:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT * FROM consumers WHERE email = 'test@studioloop.com';"
```

**Expected Results:**
- [ ] 10-20 consumers exist
- [ ] Names include diverse SA-style names
- [ ] Phone numbers use SA format (+27...)
- [ ] Test consumer `test@studioloop.com` exists

**Actual Results:**
_________________________________________________

---

### TC-4: Verify Spaces Seeded
**Acceptance Criterion:** (Bonus - model exists)

**Steps:**
1. Query spaces with gym names:
```bash
docker exec -it studioloop-db psql -U app -d app -c "
SELECT s.name, s.capacity, g.name as gym_name
FROM spaces s
JOIN gyms g ON s.gym_id = g.id
ORDER BY g.name, s.name;"
```

**Expected Results:**
- [ ] Each gym has 2-4 spaces
- [ ] Space names are realistic (Main Studio, Spin Room, Yoga Studio)
- [ ] Capacities are reasonable (15-30)
- [ ] All spaces linked to valid gyms

**Actual Results:**
_________________________________________________

---

### TC-5: Idempotent Re-run
**Acceptance Criterion:** AC #8

**Steps:**
1. Count current records:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT 'gyms', COUNT(*) FROM gyms UNION ALL SELECT 'consumers', COUNT(*) FROM consumers UNION ALL SELECT 'spaces', COUNT(*) FROM spaces;"
```

2. Run seed script again:
```bash
uv run python scripts/seed.py
```

3. Re-count records:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT 'gyms', COUNT(*) FROM gyms UNION ALL SELECT 'consumers', COUNT(*) FROM consumers UNION ALL SELECT 'spaces', COUNT(*) FROM spaces;"
```

**Expected Results:**
- [ ] Counts are identical before and after
- [ ] No duplicate key errors
- [ ] Script completes successfully

**Actual Results:**
_________________________________________________

---

### TC-6: Reset Flag
**Acceptance Criterion:** AC #9

**Steps:**
1. Verify data exists:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT COUNT(*) FROM gyms;"
```

2. Run seed with reset flag:
```bash
uv run python scripts/seed.py --reset
```

3. Verify fresh data:
```bash
docker exec -it studioloop-db psql -U app -d app -c "SELECT COUNT(*) FROM gyms;"
```

**Expected Results:**
- [ ] Script accepts `--reset` flag
- [ ] Existing seed data is cleared
- [ ] Fresh seed data is re-created
- [ ] Final counts match expected seed amounts

**Actual Results:**
_________________________________________________

---

### TC-7: Staff Placeholder (Deferred)
**Acceptance Criterion:** AC #3

**Steps:**
1. Check that staff seeding is documented but deferred:
```bash
cat backend/app/seed/staff.py 2>/dev/null || echo "File may not exist - check placeholder"
```

**Expected Results:**
- [ ] Placeholder file exists OR documented in main seed module
- [ ] Comments indicate deferral to Epic 3
- [ ] No runtime errors related to missing Staff model

**Actual Results:**
_________________________________________________

---

### TC-8: Membership Plans Placeholder (Deferred)
**Acceptance Criterion:** AC #4

**Steps:**
1. Check that membership plan seeding is documented but deferred:
```bash
grep -r "MembershipPlan" backend/app/seed/ 2>/dev/null || echo "Check placeholder comments"
```

**Expected Results:**
- [ ] Placeholder exists documenting future implementation
- [ ] Comments indicate deferral to Epic 4
- [ ] Plans documented: Basic (R299), Premium (R499), Unlimited (R699)

**Actual Results:**
_________________________________________________

---

## Edge Cases and Error Scenarios

### EC-1: Run on Empty Database
**Steps:**
1. Reset database completely (if safe):
```bash
docker compose -f docker-compose.local.yml down -v
docker compose -f docker-compose.local.yml up -d
uv run alembic upgrade head
```

2. Run seed on fresh database:
```bash
uv run python scripts/seed.py
```

**Expected Results:**
- [ ] Script handles empty database gracefully
- [ ] All seed data created successfully

**Actual Results:**
_________________________________________________

---

### EC-2: Run Without Database Connection
**Steps:**
1. Stop database:
```bash
docker compose -f docker-compose.local.yml stop db
```

2. Attempt to run seed:
```bash
uv run python scripts/seed.py
```

3. Restart database:
```bash
docker compose -f docker-compose.local.yml start db
```

**Expected Results:**
- [ ] Script fails gracefully with clear error message
- [ ] No partial data corruption

**Actual Results:**
_________________________________________________

---

### EC-3: Invalid Reset Flag Usage
**Steps:**
1. Test help/usage:
```bash
uv run python scripts/seed.py --help
```

**Expected Results:**
- [ ] Help text shows available options
- [ ] `--reset` flag is documented

**Actual Results:**
_________________________________________________

---

## Rollback Steps

### Full Rollback
To completely undo story changes:

```bash
# Remove seed module
rm -rf backend/app/seed/

# Remove seed script
rm -f backend/scripts/seed.py

# Remove seed tests
rm -rf backend/tests/seed/

# Clear seeded data from database
docker exec -it studioloop-db psql -U app -d app -c "DELETE FROM spaces; DELETE FROM consumers; DELETE FROM gyms;"
```

### Partial Rollback (Clear Seed Data Only)
To reset seeded data without removing code:

```bash
# Run with reset flag (if implemented)
uv run python scripts/seed.py --reset

# Or manually clear:
docker exec -it studioloop-db psql -U app -d app -c "DELETE FROM spaces; DELETE FROM consumers WHERE email != 'admin@example.com'; DELETE FROM gyms;"
```

### Environment Cleanup
```bash
# Stop Docker services
docker compose -f docker-compose.local.yml down

# Remove volumes (WARNING: deletes all data)
docker compose -f docker-compose.local.yml down -v
```

---

## Sign-Off

### Test Case Summary

| Test Case | Status |
|-----------|--------|
| TC-1: Basic Seed Execution | PASS / FAIL |
| TC-2: Verify Gyms Seeded | PASS / FAIL |
| TC-3: Verify Consumers Seeded | PASS / FAIL |
| TC-4: Verify Spaces Seeded | PASS / FAIL |
| TC-5: Idempotent Re-run | PASS / FAIL |
| TC-6: Reset Flag | PASS / FAIL |
| TC-7: Staff Placeholder | PASS / FAIL |
| TC-8: Membership Plans Placeholder | PASS / FAIL |
| EC-1: Empty Database | PASS / FAIL |
| EC-2: No Database Connection | PASS / FAIL |
| EC-3: Invalid Flag Usage | PASS / FAIL |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met
- [ ] **FAIL** - Blocking issues found

### Blocking Issues
_________________________________________________
_________________________________________________

### Non-Blocking Notes
_________________________________________________
_________________________________________________

### Tester Signature

**Name:** _______________
**Date:** _______________

---

### Next Story Reference

**Next Story:** 0-9-configure-local-e2e-testing-setup
**Status:** backlog
