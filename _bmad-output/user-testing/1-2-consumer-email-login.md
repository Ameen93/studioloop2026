# QA Checklist: Story 1.2 - Consumer Email Login

**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

- [ ] Backend server running locally (`cd backend && uv run fastapi dev`)
- [ ] Frontend web app running (`cd frontend && pnpm dev --filter @sl/web`)
- [ ] Consumer mobile app running (`cd frontend && pnpm dev --filter @sl/consumer-mobile`)
- [ ] Test consumer account exists with verified email (from Story 1.1)
- [ ] Test consumer account exists with unverified email (for negative testing)
- [ ] Database accessible (PostgreSQL via Docker)

---

## Environment Setup

```bash
# 1. Ensure Docker services are running
docker compose -f docker-compose.local.yml up -d

# 2. Start backend server
cd backend
uv run fastapi dev

# 3. In new terminal, start frontend
cd frontend
pnpm dev
```

**Verification:**
- [ ] Backend API accessible at http://localhost:8000
- [ ] Web app accessible at http://localhost:5173
- [ ] Mobile app running in Expo Go / simulator

---

## Test Cases

### TC-1: Successful Consumer Login (AC #1, #2, #3)

**Acceptance Criterion:** Given I have a verified consumer account, When I enter correct email and password, Then I receive tokens and am redirected to home.

**Steps:**
1. Navigate to login page: http://localhost:5173/auth/login
2. Enter verified test email: `test@studioloop.com`
3. Enter correct password: `testpassword123` (or actual test password)
4. Click "Login" button
5. Observe browser network tab / DevTools

**Expected Results:**
- [ ] API returns 200 status code
- [ ] Response contains `access_token` (JWT format)
- [ ] Response contains `refresh_token` (JWT format)
- [ ] Response contains `token_type: "bearer"`
- [ ] User is redirected to home screen
- [ ] Tokens are stored (check DevTools > Application > Local Storage)

**Actual Results:** _______________

---

### TC-2: Invalid Password Returns 401 (AC #4)

**Acceptance Criterion:** Invalid credentials return 401 with INVALID_CREDENTIALS error code.

**Steps:**
1. Navigate to login page
2. Enter valid email: `test@studioloop.com`
3. Enter incorrect password: `wrongpassword`
4. Click "Login" button

**Expected Results:**
- [ ] API returns 401 status code
- [ ] Response contains `code: "INVALID_CREDENTIALS"`
- [ ] Response contains `message: "Invalid email or password"`
- [ ] Error message displayed on screen
- [ ] User is NOT redirected

**Actual Results:** _______________

---

### TC-3: Non-existent Email Returns 401 (AC #4)

**Acceptance Criterion:** Same error for non-existent email (prevent enumeration).

**Steps:**
1. Navigate to login page
2. Enter non-existent email: `doesnotexist@example.com`
3. Enter any password: `anypassword123`
4. Click "Login" button

**Expected Results:**
- [ ] API returns 401 status code
- [ ] Response contains `code: "INVALID_CREDENTIALS"` (SAME as wrong password)
- [ ] Error message displayed: "Invalid email or password"
- [ ] No indication whether email exists

**Actual Results:** _______________

---

### TC-4: Unverified Account Cannot Login (AC #5)

**Acceptance Criterion:** Unverified accounts return 403 with EMAIL_NOT_VERIFIED error code.

**Steps:**
1. Register a new account but do NOT click verification link
2. Navigate to login page
3. Enter unverified email and correct password
4. Click "Login" button

**Expected Results:**
- [ ] API returns 403 status code
- [ ] Response contains `code: "EMAIL_NOT_VERIFIED"`
- [ ] Response contains `message: "Please verify your email before logging in"`
- [ ] Error message prompts user to verify email
- [ ] User is NOT logged in

**Actual Results:** _______________

---

### TC-5: Mobile Login with MMKV Storage (AC #2)

**Acceptance Criterion:** Tokens stored in MMKV on mobile, not AsyncStorage.

**Steps:**
1. Open consumer mobile app
2. Navigate to login screen
3. Enter valid credentials
4. Login successfully
5. Close app completely
6. Reopen app

**Expected Results:**
- [ ] Login successful, tokens stored
- [ ] App remembers login state after restart
- [ ] Tokens NOT in AsyncStorage (verify via React Native Debugger if needed)

**Actual Results:** _______________

---

### TC-6: Login Form Validation

**Steps:**
1. Navigate to login page
2. Try to submit with empty fields
3. Enter invalid email format
4. Enter password less than 8 characters

**Expected Results:**
- [ ] Empty fields show validation error
- [ ] Invalid email format rejected
- [ ] Short password shows error (if client-side validation)
- [ ] Submit button disabled until valid

**Actual Results:** _______________

---

## Edge Cases and Error Scenarios

### EC-1: Network Failure During Login

**Steps:**
1. Disable network/WiFi
2. Attempt to login

**Expected:**
- [ ] Graceful error message shown
- [ ] No crash or unhandled exception
- [ ] User can retry when online

---

### EC-2: Concurrent Login Sessions

**Steps:**
1. Login on web browser
2. Login on mobile app with same account

**Expected:**
- [ ] Both sessions work independently
- [ ] No errors or conflicts

---

### EC-3: Token Expiry Handling (Edge Case for Future)

**Note:** Full token refresh testing is in Story 1.4. Here just verify tokens are issued with correct expiry.

**Steps:**
1. Login and capture access_token
2. Decode JWT at https://jwt.io
3. Check `exp` claim

**Expected:**
- [ ] Access token expires within 24 hours from now
- [ ] Refresh token has longer expiry (7 days)

---

## Rollback Steps

### Full Rollback (Undo All Story Changes)

```bash
# 1. Revert database (if migration added)
cd backend
alembic downgrade -1

# 2. Revert code changes
git checkout main -- backend/app/api/routes/consumers.py
git checkout main -- backend/app/core/security.py
git checkout main -- backend/app/core/config.py

# 3. Regenerate API client (removes login endpoint)
cd frontend
pnpm --filter @sl/api-client generate
```

### Partial Rollback (Remove Frontend Only)

```bash
rm frontend/apps/web/src/routes/auth/Login.tsx
rm frontend/apps/consumer-mobile/app/\(auth\)/login.tsx
```

### Environment Cleanup

```bash
# Clear local storage (web)
# In browser DevTools: localStorage.clear()

# Reset mobile storage
# Reinstall app or clear app data
```

---

## Sign-Off Section

| Test Case | Status |
|-----------|--------|
| TC-1: Successful Login | [ ] PASS / [ ] FAIL |
| TC-2: Invalid Password | [ ] PASS / [ ] FAIL |
| TC-3: Non-existent Email | [ ] PASS / [ ] FAIL |
| TC-4: Unverified Account | [ ] PASS / [ ] FAIL |
| TC-5: Mobile MMKV Storage | [ ] PASS / [ ] FAIL |
| TC-6: Form Validation | [ ] PASS / [ ] FAIL |
| EC-1: Network Failure | [ ] PASS / [ ] FAIL |
| EC-2: Concurrent Sessions | [ ] PASS / [ ] FAIL |
| EC-3: Token Expiry | [ ] PASS / [ ] FAIL |

---

### Final Verdict

- [ ] **PASS** - All test cases passed, story ready for completion
- [ ] **FAIL** - Issues found, requires fixes

**Blocking Issues:**
_______________

**Non-Blocking Notes:**
_______________

**Tester Signature:** _______________
**Date:** _______________

---

**Next Story:** 1-3-staff-email-login
