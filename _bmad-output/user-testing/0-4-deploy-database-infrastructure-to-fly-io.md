# QA Checklist: Story 0.4 - Deploy Database Infrastructure to Fly.io

**Story ID:** 0.4
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

Before testing, ensure you have:

- [ ] Fly.io account created and verified
- [ ] flyctl CLI installed (`curl -L https://fly.io/install.sh | sh`)
- [ ] Authenticated with Fly.io (`fly auth login`)
- [ ] Access to studioloop organization on Fly.io
- [ ] Backend repository cloned and accessible
- [ ] Terminal access with internet connectivity

---

## Environment Setup

### Step 1: Verify Fly CLI Installation
```bash
fly version
```
**Expected:** Version output like `flyctl v0.x.x`
- [ ] flyctl CLI is installed and responding

### Step 2: Verify Authentication
```bash
fly auth whoami
```
**Expected:** Your email address displayed
- [ ] Authenticated with correct account

### Step 3: Verify Region Availability
```bash
fly platform regions | grep jnb
```
**Expected:** `jnb` region listed (Johannesburg, South Africa)
- [ ] Johannesburg region is available

---

## Test Cases

### TC-1: PostgreSQL Deployment in Johannesburg
**Acceptance Criterion:** #1

**Steps:**
1. List existing Postgres apps:
   ```bash
   fly postgres list
   ```
2. Check if studioloop-db exists:
   ```bash
   fly status -a studioloop-db
   ```
3. Verify region is `jnb`:
   ```bash
   fly regions list -a studioloop-db
   ```

**Expected Results:**
- [ ] studioloop-db app exists
- [ ] Status shows "running"
- [ ] Primary region is `jnb`

**Actual Results:** _______________

---

### TC-2: PostgreSQL Version and PostGIS
**Acceptance Criterion:** #1

**Steps:**
1. Connect to PostgreSQL:
   ```bash
   fly postgres connect -a studioloop-db
   ```
2. Check PostgreSQL version:
   ```sql
   SELECT version();
   ```
3. Check PostGIS extension:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'postgis';
   ```
4. Exit: `\q`

**Expected Results:**
- [ ] Connection successful
- [ ] PostgreSQL version is 16.x
- [ ] PostGIS extension is installed

**Actual Results:** _______________

---

### TC-3: Redis Deployment in Johannesburg
**Acceptance Criterion:** #2

**Steps:**
1. Check Redis app status:
   ```bash
   fly status -a studioloop-redis
   ```
2. Verify region:
   ```bash
   fly regions list -a studioloop-redis
   ```
3. Check Redis volume:
   ```bash
   fly volumes list -a studioloop-redis
   ```

**Expected Results:**
- [ ] studioloop-redis app exists
- [ ] Status shows "running"
- [ ] Primary region is `jnb`
- [ ] Volume `redis_data` is attached

**Actual Results:** _______________

---

### TC-4: Connection Secrets Configuration
**Acceptance Criterion:** #3

**Steps:**
1. List backend secrets:
   ```bash
   fly secrets list -a studioloop-api
   ```

**Expected Results:**
- [ ] `DATABASE_URL` secret exists
- [ ] `REDIS_URL` secret exists

**Actual Results:** _______________

---

### TC-5: Backend Database Connectivity
**Acceptance Criterion:** #4

**Steps:**
1. Check backend status:
   ```bash
   fly status -a studioloop-api
   ```
2. Check recent logs for database connection:
   ```bash
   fly logs -a studioloop-api | grep -i "database\|postgres\|redis"
   ```
3. Test health endpoint:
   ```bash
   curl -s https://studioloop-api.fly.dev/health | jq
   ```

**Expected Results:**
- [ ] Backend is running
- [ ] Logs show successful database connection
- [ ] Logs show successful Redis connection
- [ ] Health endpoint returns 200 OK

**Actual Results:** _______________

---

### TC-6: PostgreSQL SSL Configuration
**Acceptance Criterion:** #5

**Steps:**
1. Connect to PostgreSQL with SSL verification:
   ```bash
   fly postgres connect -a studioloop-db
   ```
2. Check SSL status:
   ```sql
   SHOW ssl;
   SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid();
   ```

**Expected Results:**
- [ ] SSL is enabled (`on`)
- [ ] Current connection is using SSL (`t` or `true`)

**Actual Results:** _______________

---

### TC-7: Backend fly.toml Configuration
**Acceptance Criterion:** #6

**Steps:**
1. Check backend fly.toml exists:
   ```bash
   cat backend/fly.toml
   ```
2. Verify configuration:
   - Check `primary_region`
   - Check `internal_port`
   - Check health check path

**Expected Results:**
- [ ] fly.toml exists in backend directory
- [ ] primary_region is `jnb`
- [ ] internal_port is 8000
- [ ] health check path is `/health`

**Actual Results:** _______________

---

## Edge Cases and Error Scenarios

### EC-1: Database Connection Failure Recovery
**Steps:**
1. Simulate connection issue by scaling down Postgres:
   ```bash
   fly scale count 0 -a studioloop-db
   ```
2. Check backend logs for error handling:
   ```bash
   fly logs -a studioloop-api
   ```
3. Restore Postgres:
   ```bash
   fly scale count 1 -a studioloop-db
   ```
4. Verify backend reconnects automatically

**Expected Behavior:**
- [ ] Backend logs connection error gracefully
- [ ] Backend reconnects when database is restored

**Actual Results:** _______________

---

### EC-2: Redis Connection Failure Recovery
**Steps:**
1. Simulate Redis issue by restarting:
   ```bash
   fly apps restart studioloop-redis
   ```
2. Check backend logs:
   ```bash
   fly logs -a studioloop-api
   ```
3. Wait 30 seconds and verify reconnection

**Expected Behavior:**
- [ ] Backend handles Redis restart gracefully
- [ ] Backend reconnects to Redis automatically

**Actual Results:** _______________

---

### EC-3: Incorrect Region Deployment (Negative Test)
**Steps:**
1. Verify all apps are in jnb region:
   ```bash
   fly status -a studioloop-db | grep Region
   fly status -a studioloop-redis | grep Region
   fly status -a studioloop-api | grep Region
   ```

**Expected Behavior:**
- [ ] ALL apps show `jnb` region (Johannesburg)
- [ ] NO apps deployed to other regions

**Actual Results:** _______________

---

## Rollback Steps

### Full Rollback (Remove All Infrastructure)
```bash
# WARNING: This destroys all data!

# Remove backend app
fly apps destroy studioloop-api --yes

# Remove Redis
fly apps destroy studioloop-redis --yes

# Remove PostgreSQL
fly apps destroy studioloop-db --yes
```

### Partial Rollback (Redis Only)
```bash
fly apps destroy studioloop-redis --yes
fly volume delete redis_data --yes
```

### Environment Cleanup
```bash
# Remove local fly.toml files if needed
rm backend/fly.toml
rm -rf infrastructure/redis/

# Revert config changes
git checkout backend/app/core/config.py
git checkout backend/app/core/database.py
```

---

## Sign-Off Section

### Test Summary

| Test Case | Status |
|-----------|--------|
| TC-1: PostgreSQL Deployment | Pass / Fail |
| TC-2: PostgreSQL Version and PostGIS | Pass / Fail |
| TC-3: Redis Deployment | Pass / Fail |
| TC-4: Connection Secrets | Pass / Fail |
| TC-5: Backend Connectivity | Pass / Fail |
| TC-6: PostgreSQL SSL | Pass / Fail |
| TC-7: fly.toml Configuration | Pass / Fail |
| EC-1: Database Recovery | Pass / Fail |
| EC-2: Redis Recovery | Pass / Fail |
| EC-3: Region Verification | Pass / Fail |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, story ready for completion
- [ ] **FAIL** - Blocking issues found, see notes below

### Blocking Issues
_List any issues that prevent story completion:_

1. _______________
2. _______________

### Non-Blocking Notes
_List any observations or minor issues:_

1. _______________
2. _______________

### Sign-Off

**Tester Signature:** _______________
**Date:** _______________

---

**Next Story:** 0.5 - Configure CI/CD Pipelines with GitHub Actions
