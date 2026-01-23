# Story 0.5: Configure Local CI (Lint and Tests)

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want CI pipelines that lint and test code on every PR,
so that code quality is maintained during local development.

## Acceptance Criteria

1. **Given** a GitHub repository with the codebase **When** I configure GitHub Actions workflows **Then** `.github/workflows/ci.yml` runs lint, type-check, and tests on every PR
2. Backend linting runs with `ruff`
3. Backend tests run with `pytest`
4. Frontend linting runs with ESLint
5. Frontend type-checking runs with TypeScript
6. Frontend tests run with Jest (or Vitest for consistency with Vite)
7. Turborepo caching is enabled for faster CI runs
8. PRs are blocked if CI fails
9. No deployment workflows are configured (deferred to Epic 16)

## Tasks / Subtasks

- [x] Task 1: Create GitHub Actions CI workflow (AC: #1, #7)
  - [x] Create `.github/workflows/ci.yml` with PR trigger
  - [x] Configure Turborepo Remote Caching with GitHub Actions cache
  - [x] Set up job matrix for parallel backend/frontend jobs

- [x] Task 2: Configure backend CI jobs (AC: #2, #3)
  - [x] Add backend lint job using `ruff check app/`
  - [x] Add backend type-check job using `mypy app/`
  - [x] Add backend test job using `pytest`
  - [x] Ensure backend uses Python 3.11 and uv for dependency management

- [x] Task 3: Configure frontend CI jobs (AC: #4, #5)
  - [x] Add frontend lint job using `pnpm lint` (Turborepo ESLint pipeline)
  - [x] Add frontend type-check job using `pnpm type-check`
  - [x] Configure pnpm setup with caching

- [x] Task 4: Add frontend testing infrastructure (AC: #6)
  - [x] Add Vitest to web app (matches Vite tooling)
  - [x] Add basic test configuration for consumer-mobile/gym-mobile
  - [x] Create `pnpm test` script in turbo.json
  - [x] Add at least one smoke test per app

- [x] Task 5: Configure branch protection (AC: #8)
  - [x] Document branch protection rules (manual GitHub setup)
  - [x] Ensure CI workflow name matches protection rules

- [x] Task 6: Verify no deployment workflows (AC: #9)
  - [x] Confirm no deploy/release workflows exist
  - [x] Add comment in CI file noting deployment deferred to Epic 16

## Dev Notes

### Architecture Compliance
- **ARCH-9**: GitHub Actions with Turborepo caching - this story implements the local CI portion (no deployment)
- Turborepo already configured with lint/test/type-check tasks in `turbo.json`
- Backend uses `ruff` for linting (already in pyproject.toml dev dependencies)
- Backend uses `pytest` for testing (already in pyproject.toml dev dependencies)
- Backend uses `mypy` for type-checking (already in pyproject.toml)

### Current Codebase State (from Stories 0.1-0.4)

**Backend (`/home/ameen/studioloop/backend/`)**:
- Python 3.11+ with FastAPI
- Uses `uv` for dependency management
- `pyproject.toml` has ruff, mypy, pytest configured
- No `tests/` directory yet (may need to create placeholder)

**Frontend (`/home/ameen/studioloop/frontend/`)**:
- Turborepo monorepo with pnpm@10.28.1
- `turbo.json` already defines `lint`, `test`, `type-check` pipelines
- Apps: web (Vite+React), consumer-mobile (Expo), gym-mobile (Expo)
- web app has ESLint configured (`eslint.config.js`)
- Mobile apps missing lint/eslint config (need to add)
- No test infrastructure yet (Jest/Vitest not configured)

### Technical Decisions

1. **Vitest over Jest for web app**: Vite projects work better with Vitest (same bundler, faster, native ESM)
2. **Jest for mobile apps**: Expo projects traditionally use Jest (Expo provides jest-expo preset)
3. **Parallel jobs**: Backend and frontend can run in parallel for faster CI
4. **Turborepo cache**: Use GitHub Actions cache for Turborepo remote caching (free tier friendly)

### File Structure Requirements

```
.github/
└── workflows/
    └── ci.yml           # Main CI workflow

frontend/
├── apps/
│   ├── web/
│   │   ├── vitest.config.ts    # New: Vitest config
│   │   └── src/__tests__/      # New: Test directory
│   ├── consumer-mobile/
│   │   ├── eslint.config.js    # New: ESLint config
│   │   └── __tests__/          # New: Test directory
│   └── gym-mobile/
│       ├── eslint.config.js    # New: ESLint config
│       └── __tests__/          # New: Test directory
├── packages/
│   └── ui/
│       └── src/__tests__/      # New: UI component tests
└── turbo.json                   # Verify test task exists
```

### Testing Standards (from project-context.md)

- Unit tests: Co-located as `*.test.ts` or `*.test.tsx`
- Integration tests: `tests/` directory
- Backend: pytest with async support
- Frontend: Jest + React Testing Library (or Vitest for web)
- E2E mobile: Detox (deferred to Story 0.9)

### Key Dependencies to Add

**Frontend (web app)**:
```json
"devDependencies": {
  "vitest": "^3.x",
  "@testing-library/react": "^16.x",
  "@testing-library/jest-dom": "^6.x",
  "jsdom": "^25.x"
}
```

**Frontend (mobile apps)**:
```json
"devDependencies": {
  "eslint": "^9.x",
  "@eslint/js": "^9.x",
  "typescript-eslint": "^8.x",
  "jest": "^29.x",
  "jest-expo": "~54.x",
  "@testing-library/react-native": "^12.x"
}
```

### Project Structure Notes

- Frontend monorepo at `/home/ameen/studioloop/frontend/`
- Backend at `/home/ameen/studioloop/backend/`
- GitHub Actions should reference paths correctly: `./backend` and `./frontend`
- Use `working-directory` in GitHub Actions jobs

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 0.5]
- [Source: _bmad-output/project-context.md#Testing Rules]
- [Source: backend/pyproject.toml#tool.ruff, tool.mypy]
- [Source: frontend/turbo.json#tasks]
- [Source: frontend/apps/web/eslint.config.js]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

### Completion Notes List

- Created `.github/workflows/ci.yml` with parallel backend/frontend jobs
- Backend CI: ruff lint, mypy type-check, pytest tests (using uv + Python 3.11)
- Frontend CI: pnpm lint, pnpm type-check, pnpm test (with Turborepo caching)
- Added Vitest to web app with test setup and smoke test
- Added Jest (jest-expo) to consumer-mobile and gym-mobile with smoke tests
- Added ESLint configs to all packages (utils, api-client, ui) and mobile apps
- Fixed lint errors in @sl/ui (removed unused imports)
- Added `"type": "module"` to packages for ESM compatibility
- Created `.github/BRANCH_PROTECTION.md` with setup instructions
- All local validations pass: lint ✅, type-check ✅, tests ✅

### File List

**New files:**
- `.github/workflows/ci.yml` - Main CI workflow
- `.github/BRANCH_PROTECTION.md` - Branch protection documentation
- `frontend/apps/web/vitest.config.ts` - Vitest configuration
- `frontend/apps/web/src/test/setup.ts` - Test setup with jest-dom
- `frontend/apps/web/src/App.test.tsx` - Web app smoke test
- `frontend/apps/consumer-mobile/eslint.config.js` - ESLint config
- `frontend/apps/consumer-mobile/__tests__/HomeScreen.test.tsx` - Mobile smoke test
- `frontend/apps/gym-mobile/eslint.config.js` - ESLint config
- `frontend/apps/gym-mobile/__tests__/HomeScreen.test.tsx` - Mobile smoke test
- `frontend/packages/utils/eslint.config.js` - ESLint config
- `frontend/packages/api-client/eslint.config.js` - ESLint config
- `frontend/packages/ui/eslint.config.js` - ESLint config

**Modified files:**
- `frontend/apps/web/package.json` - Added Vitest, testing-library deps, test scripts
- `frontend/apps/consumer-mobile/package.json` - Added ESLint, Jest, testing deps
- `frontend/apps/gym-mobile/package.json` - Added ESLint, Jest, testing deps
- `frontend/packages/utils/package.json` - Added ESLint deps, type: module
- `frontend/packages/api-client/package.json` - Added ESLint deps, type: module
- `frontend/packages/ui/package.json` - Added ESLint deps, type: module
- `frontend/packages/ui/src/primitives/Button.tsx` - Removed unused imports
- `frontend/packages/ui/src/primitives/Input.tsx` - Removed unused import
- `frontend/pnpm-lock.yaml` - Updated with new dependencies
