# QA Checklist: Story 0.1 - Initialize Backend with FastAPI Template

**Story:** Initialize Backend with FastAPI Template
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] Git installed and configured
- [ ] Python 3.11+ installed (`python --version`)
- [ ] `uv` package manager installed (`uv --version`) OR `pip` available
- [ ] `pipx` installed for copier (`pipx --version`)
- [ ] Terminal access to project root directory
- [ ] Internet connection (for template download)

---

## Environment Setup

### 1. Prepare Test Environment

```bash
# Navigate to project root
cd /home/ameen/studioloop

# Verify no existing backend directory (or backup if exists)
ls -la backend/
```

- [ ] Project directory accessible
- [ ] No conflicting `backend/` directory exists (or backed up)

### 2. Install Required Tools (if not present)

```bash
# Install copier via pipx
pipx install copier

# Verify installation
copier --version
```

- [ ] Copier installed and accessible

---

## Test Cases

### TC-1: Backend Initialization with Copier

**Acceptance Criterion:** #1 - Copier creates working FastAPI application

**Steps:**
1. Run the copier command:
   ```bash
   copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust
   ```

2. When prompted, enter:
   - `project_name`: **studioloop**
   - `stack_name`: **studioloop**
   - Accept defaults for other prompts (or note customizations)

3. Wait for template to download and generate

**Expected Results:**
- [ ] Command completes without errors
- [ ] `backend/` directory created at project root
- [ ] No error messages during generation
- [ ] Post-creation scripts run successfully

**Actual Results:** _______________

---

### TC-2: Directory Structure Verification

**Acceptance Criterion:** #2 - Directory structure follows architecture

**Steps:**
1. Check the directory structure:
   ```bash
   ls -la backend/
   ls -la backend/app/
   ```

2. Verify core directories exist:
   ```bash
   # Check each required directory
   ls backend/app/api/routes/
   ls backend/app/models/
   ls backend/app/schemas/
   ls backend/app/core/
   ```

3. Verify custom directories were created (by dev):
   ```bash
   ls backend/app/services/
   ls backend/app/repositories/
   ls backend/app/utils/
   ```

**Expected Results:**
- [ ] `backend/app/` directory exists
- [ ] `backend/app/api/routes/` exists with route files
- [ ] `backend/app/models/` exists
- [ ] `backend/app/schemas/` exists
- [ ] `backend/app/core/` exists
- [ ] `backend/app/services/` exists (created by dev)
- [ ] `backend/app/repositories/` exists (created by dev)
- [ ] `backend/app/utils/` exists (created by dev)

**Actual Results:** _______________

---

### TC-3: Python Configuration Verification

**Acceptance Criterion:** #3 - Python 3.11+ configured

**Steps:**
1. Check pyproject.toml:
   ```bash
   cat backend/pyproject.toml | grep -A5 "python"
   ```

2. Verify Python version requirement:
   ```bash
   grep "requires-python" backend/pyproject.toml
   ```

**Expected Results:**
- [ ] `pyproject.toml` exists in backend/
- [ ] Python version >= 3.11 specified
- [ ] Dependencies listed include FastAPI, SQLModel, Pydantic

**Actual Results:** _______________

---

### TC-4: Alembic Configuration Verification

**Acceptance Criterion:** #4 - Alembic configured for migrations

**Steps:**
1. Check Alembic directory:
   ```bash
   ls -la backend/alembic/
   ```

2. Verify configuration files:
   ```bash
   cat backend/alembic.ini | head -20
   ls backend/alembic/versions/
   ```

3. Check env.py exists:
   ```bash
   ls backend/alembic/env.py
   ```

**Expected Results:**
- [ ] `backend/alembic/` directory exists
- [ ] `backend/alembic.ini` configuration file exists
- [ ] `backend/alembic/env.py` exists
- [ ] `backend/alembic/versions/` directory exists

**Actual Results:** _______________

---

### TC-5: Server Startup Test

**Acceptance Criterion:** #5 - Server starts successfully

**Steps:**
1. Navigate to backend:
   ```bash
   cd backend
   ```

2. Create/check .env file with minimal config:
   ```bash
   # Check if .env exists
   cat .env

   # If missing, create minimal .env:
   # SECRET_KEY=testsecretkey123456789012345678901234567890
   # FIRST_SUPERUSER_PASSWORD=testpassword123
   # POSTGRES_SERVER=localhost
   # POSTGRES_USER=postgres
   # POSTGRES_PASSWORD=postgres
   # POSTGRES_DB=studioloop
   ```

3. Install dependencies:
   ```bash
   uv sync
   # OR: pip install -e .
   ```

4. Start the server:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

5. Observe startup logs

**Expected Results:**
- [ ] Dependencies install without errors
- [ ] Server starts without crashes
- [ ] Logs show "Uvicorn running on http://127.0.0.1:8000"
- [ ] No import errors or missing module errors

**Notes:** Server may show database connection warnings if PostgreSQL not running - this is expected for this story.

**Actual Results:** _______________

---

### TC-6: Health Endpoint Test

**Acceptance Criterion:** #6 - Health endpoint responds

**Steps:**
1. With server running, open new terminal

2. Test health endpoint:
   ```bash
   curl -i http://localhost:8000/health
   ```

3. Alternative: Open browser to `http://localhost:8000/health`

4. Check API docs:
   ```bash
   curl -i http://localhost:8000/docs
   ```

**Expected Results:**
- [ ] `GET /health` returns HTTP 200
- [ ] Response body indicates healthy status
- [ ] `/docs` shows Swagger UI (may require auth bypass for full access)
- [ ] `/openapi.json` returns valid OpenAPI schema

**Actual Results:** _______________

---

## Edge Cases & Error Scenarios

### EC-1: Duplicate Backend Directory

**Scenario:** Running copier when backend/ already exists

**Test:**
```bash
# If backend exists, try running copier again
copier copy https://github.com/fastapi/full-stack-fastapi-template backend --trust
```

**Expected:** Copier should warn about existing directory and ask to overwrite or abort

**Result:** _______________

---

### EC-2: Missing Environment Variables

**Scenario:** Starting server without .env file

**Test:**
```bash
# Remove or rename .env
mv backend/.env backend/.env.backup
uv run uvicorn app.main:app --reload
```

**Expected:** Server should fail with clear error about missing configuration

**Result:** _______________

---

### EC-3: Wrong Python Version

**Scenario:** Running with Python < 3.11

**Test:**
```bash
python3.10 -m uvicorn app.main:app --reload
```

**Expected:** Should fail with version compatibility error

**Result:** _______________

---

## Rollback Steps

If testing fails or you need to reset:

### Full Rollback
```bash
# Remove the backend directory entirely
rm -rf backend/

# Re-run create-story workflow if needed
```

### Partial Rollback (Keep Template, Reset Changes)
```bash
# Remove custom directories only
rm -rf backend/app/services/
rm -rf backend/app/repositories/
rm -rf backend/app/utils/

# Reset any modified files
cd backend && git checkout .
```

### Environment Cleanup
```bash
# Stop any running servers
pkill -f "uvicorn app.main"

# Remove virtual environment if created
rm -rf backend/.venv/
```

---

## Sign-Off

### Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-1: Backend Init | [ ] Pass / [ ] Fail | |
| TC-2: Directory Structure | [ ] Pass / [ ] Fail | |
| TC-3: Python Config | [ ] Pass / [ ] Fail | |
| TC-4: Alembic Config | [ ] Pass / [ ] Fail | |
| TC-5: Server Startup | [ ] Pass / [ ] Fail | |
| TC-6: Health Endpoint | [ ] Pass / [ ] Fail | |
| EC-1: Duplicate Dir | [ ] Pass / [ ] Fail | |
| EC-2: Missing Env | [ ] Pass / [ ] Fail | |
| EC-3: Wrong Python | [ ] Pass / [ ] Fail | |

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
1. Update sprint-status.yaml: `0-1-initialize-backend-with-fastapi-template: done`
2. Proceed to Story 0.2: Initialize Frontend Monorepo with Turborepo
