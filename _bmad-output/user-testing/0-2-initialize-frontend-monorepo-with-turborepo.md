# QA Checklist: Story 0.2 - Initialize Frontend Monorepo with Turborepo

**Story:** Initialize Frontend Monorepo with Turborepo
**Status:** Pending Testing
**Tester:** Ameen
**Date:** _______________

---

## Prerequisites

Before testing, ensure the following are in place:

- [ ] Node.js 18+ installed (`node --version`)
- [ ] pnpm installed (`pnpm --version`)
- [ ] Story 0.1 completed (backend directory exists)
- [ ] Terminal access to project root directory
- [ ] Internet connection (for npm package downloads)

---

## Environment Setup

### 1. Prepare Test Environment

```bash
# Navigate to project root
cd /home/ameen/studioloop

# Verify backend exists from Story 0.1
ls -la backend/

# Verify no existing frontend directory
ls -la frontend/
```

- [ ] Project directory accessible
- [ ] Backend directory exists (from Story 0.1)
- [ ] No conflicting `frontend/` directory exists

### 2. Verify pnpm Installation

```bash
# Check pnpm version (should be 8.x or 9.x)
pnpm --version

# If not installed:
# npm install -g pnpm
```

- [ ] pnpm installed and accessible (v8+ or v9+)

---

## Test Cases

### TC-1: pnpm Workspace Configuration

**Acceptance Criterion:** #1 - pnpm-workspace.yaml defines apps/* and packages/*

**Steps:**
1. Navigate to frontend directory:
   ```bash
   cd /home/ameen/studioloop/frontend
   ```

2. Check pnpm-workspace.yaml exists:
   ```bash
   cat pnpm-workspace.yaml
   ```

3. Verify content includes:
   ```yaml
   packages:
     - 'apps/*'
     - 'packages/*'
   ```

**Expected Results:**
- [ ] `frontend/` directory exists
- [ ] `pnpm-workspace.yaml` exists
- [ ] Workspace defines `apps/*`
- [ ] Workspace defines `packages/*`

**Actual Results:** _______________

---

### TC-2: Turborepo Configuration

**Acceptance Criterion:** #2 - turbo.json configures build/dev/lint/test pipelines

**Steps:**
1. Check turbo.json exists:
   ```bash
   cat frontend/turbo.json
   ```

2. Verify pipelines are defined:
   ```bash
   cat frontend/turbo.json | grep -E '"build"|"dev"|"lint"|"test"'
   ```

3. Verify turbo is in devDependencies:
   ```bash
   cat frontend/package.json | grep turbo
   ```

**Expected Results:**
- [ ] `turbo.json` exists in frontend/
- [ ] `build` pipeline defined
- [ ] `dev` pipeline defined
- [ ] `lint` pipeline defined
- [ ] `test` pipeline defined
- [ ] `turbo` in devDependencies

**Actual Results:** _______________

---

### TC-3: Consumer Mobile App (Expo)

**Acceptance Criterion:** #3 - apps/consumer-mobile/ is an Expo React Native project

**Steps:**
1. Check directory exists:
   ```bash
   ls -la frontend/apps/consumer-mobile/
   ```

2. Verify package.json:
   ```bash
   cat frontend/apps/consumer-mobile/package.json | head -20
   ```

3. Check for Expo dependencies:
   ```bash
   cat frontend/apps/consumer-mobile/package.json | grep -E '"expo"|"expo-router"'
   ```

4. Verify app directory (Expo Router):
   ```bash
   ls frontend/apps/consumer-mobile/app/
   ```

**Expected Results:**
- [ ] `apps/consumer-mobile/` directory exists
- [ ] `package.json` has name `@sl/consumer-mobile`
- [ ] `expo` in dependencies
- [ ] `expo-router` in dependencies
- [ ] `app/` directory exists (Expo Router)

**Actual Results:** _______________

---

### TC-4: Gym Mobile App (Expo)

**Acceptance Criterion:** #4 - apps/gym-mobile/ is an Expo React Native project

**Steps:**
1. Check directory exists:
   ```bash
   ls -la frontend/apps/gym-mobile/
   ```

2. Verify package.json:
   ```bash
   cat frontend/apps/gym-mobile/package.json | head -20
   ```

3. Check for Expo dependencies:
   ```bash
   cat frontend/apps/gym-mobile/package.json | grep -E '"expo"|"expo-router"'
   ```

**Expected Results:**
- [ ] `apps/gym-mobile/` directory exists
- [ ] `package.json` has name `@sl/gym-mobile`
- [ ] `expo` in dependencies
- [ ] `expo-router` in dependencies
- [ ] `app/` directory exists (Expo Router)

**Actual Results:** _______________

---

### TC-5: Web App (Vite + React)

**Acceptance Criterion:** #5 - apps/web/ is a Vite + React project

**Steps:**
1. Check directory exists:
   ```bash
   ls -la frontend/apps/web/
   ```

2. Verify package.json:
   ```bash
   cat frontend/apps/web/package.json | head -20
   ```

3. Check for Vite:
   ```bash
   cat frontend/apps/web/package.json | grep vite
   ```

4. Check for vite.config:
   ```bash
   ls frontend/apps/web/vite.config.*
   ```

**Expected Results:**
- [ ] `apps/web/` directory exists
- [ ] `package.json` has name `@sl/web`
- [ ] `vite` in devDependencies
- [ ] `react` in dependencies
- [ ] `vite.config.ts` exists

**Actual Results:** _______________

---

### TC-6: Shared Packages

**Acceptance Criterion:** #6 - packages/api-client/, packages/ui/, packages/utils/ exist

**Steps:**
1. Check api-client package:
   ```bash
   ls frontend/packages/api-client/
   cat frontend/packages/api-client/package.json | grep name
   ```

2. Check ui package:
   ```bash
   ls frontend/packages/ui/
   cat frontend/packages/ui/package.json | grep name
   ```

3. Check utils package:
   ```bash
   ls frontend/packages/utils/
   cat frontend/packages/utils/package.json | grep name
   ```

**Expected Results:**
- [ ] `packages/api-client/` exists with `@sl/api-client` name
- [ ] `packages/ui/` exists with `@sl/ui` name
- [ ] `packages/utils/` exists with `@sl/utils` name
- [ ] Each package has `src/` directory
- [ ] Each package has TypeScript configured

**Actual Results:** _______________

---

### TC-7: Concurrent App Development

**Acceptance Criterion:** #7 - pnpm dev starts all apps concurrently

**Steps:**
1. Install dependencies:
   ```bash
   cd /home/ameen/studioloop/frontend
   pnpm install
   ```

2. Run dev command:
   ```bash
   pnpm dev
   ```

3. Observe output for all apps starting

4. In separate terminals, verify:
   ```bash
   # Web should be running (check port, usually 5173)
   curl http://localhost:5173

   # Expo apps should show QR codes or Metro bundler
   ```

**Expected Results:**
- [ ] `pnpm install` completes without errors
- [ ] `pnpm dev` starts without errors
- [ ] Web app accessible at localhost (check port in output)
- [ ] Consumer mobile shows Expo/Metro running
- [ ] Gym mobile shows Expo/Metro running

**Actual Results:** _______________

---

### TC-8: TypeScript Configuration

**Acceptance Criterion:** #8 - TypeScript strict mode with shared tsconfig.base.json

**Steps:**
1. Check base config:
   ```bash
   cat frontend/tsconfig.base.json
   ```

2. Verify strict mode:
   ```bash
   cat frontend/tsconfig.base.json | grep '"strict"'
   ```

3. Check app configs extend base:
   ```bash
   cat frontend/apps/consumer-mobile/tsconfig.json | grep extends
   cat frontend/apps/gym-mobile/tsconfig.json | grep extends
   cat frontend/apps/web/tsconfig.json | grep extends
   ```

4. Run type check:
   ```bash
   pnpm type-check
   ```

**Expected Results:**
- [ ] `tsconfig.base.json` exists in frontend/
- [ ] `"strict": true` is set
- [ ] Consumer mobile tsconfig extends base
- [ ] Gym mobile tsconfig extends base
- [ ] Web tsconfig extends base
- [ ] `pnpm type-check` passes without errors

**Actual Results:** _______________

---

## Edge Cases & Error Scenarios

### EC-1: Missing .npmrc Configuration

**Scenario:** Running without proper .npmrc settings

**Test:**
```bash
# Check .npmrc exists
cat frontend/.npmrc

# Should contain:
# node-linker=hoisted
# shamefully-hoist=true
```

**Expected:** .npmrc exists with Metro-compatible settings

**Result:** _______________

---

### EC-2: Different React Native Versions

**Scenario:** Apps using different RN versions (should be identical)

**Test:**
```bash
# Compare React Native versions
cat frontend/apps/consumer-mobile/package.json | grep '"react-native"'
cat frontend/apps/gym-mobile/package.json | grep '"react-native"'
```

**Expected:** Both apps use the exact same React Native version

**Result:** _______________

---

### EC-3: Workspace Package Resolution

**Scenario:** Apps can import from shared packages

**Test:**
```bash
# Check if workspace packages are linked
cd frontend
pnpm list --depth 0 | grep @sl/
```

**Expected:** All @sl/* packages should be listed and linked

**Result:** _______________

---

## Rollback Steps

If testing fails or you need to reset:

### Full Rollback
```bash
# Remove the entire frontend directory
rm -rf /home/ameen/studioloop/frontend/

# Re-run create-story workflow if needed
```

### Partial Rollback (Keep Structure, Reset Dependencies)
```bash
# Remove node_modules and lock file
cd /home/ameen/studioloop/frontend
rm -rf node_modules/
rm -rf apps/*/node_modules/
rm -rf packages/*/node_modules/
rm pnpm-lock.yaml

# Reinstall
pnpm install
```

### Environment Cleanup
```bash
# Stop any running dev servers
pkill -f "vite"
pkill -f "expo"
pkill -f "metro"

# Clear pnpm cache if needed
pnpm store prune
```

---

## Sign-Off

### Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-1: pnpm Workspace | [ ] Pass / [ ] Fail | |
| TC-2: Turborepo Config | [ ] Pass / [ ] Fail | |
| TC-3: Consumer Mobile | [ ] Pass / [ ] Fail | |
| TC-4: Gym Mobile | [ ] Pass / [ ] Fail | |
| TC-5: Web App | [ ] Pass / [ ] Fail | |
| TC-6: Shared Packages | [ ] Pass / [ ] Fail | |
| TC-7: Concurrent Dev | [ ] Pass / [ ] Fail | |
| TC-8: TypeScript Config | [ ] Pass / [ ] Fail | |
| EC-1: .npmrc Config | [ ] Pass / [ ] Fail | |
| EC-2: RN Versions | [ ] Pass / [ ] Fail | |
| EC-3: Package Resolution | [ ] Pass / [ ] Fail | |

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
1. Update sprint-status.yaml: `0-2-initialize-frontend-monorepo-with-turborepo: done`
2. Proceed to Story 0.3: Configure Shared UI Package with NativeWind/Tailwind
