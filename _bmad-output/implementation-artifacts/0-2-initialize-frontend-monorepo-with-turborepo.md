# Story 0.2: Initialize Frontend Monorepo with Turborepo

Status: review

## Story

As a **developer**,
I want a Turborepo monorepo with pnpm workspaces,
so that I can share code across consumer-mobile, gym-mobile, and web apps.

## Acceptance Criteria

1. **Given** a new frontend directory
   **When** I initialize the monorepo with `pnpm init` and Turborepo
   **Then** `pnpm-workspace.yaml` defines `apps/*` and `packages/*`

2. **Given** the monorepo is initialized
   **When** I check `turbo.json`
   **Then** it configures build/dev/lint/test pipelines

3. **Given** the monorepo exists
   **When** I check `apps/consumer-mobile/`
   **Then** it is scaffolded as an Expo React Native project

4. **Given** the monorepo exists
   **When** I check `apps/gym-mobile/`
   **Then** it is scaffolded as an Expo React Native project

5. **Given** the monorepo exists
   **When** I check `apps/web/`
   **Then** it is scaffolded as a Vite + React project

6. **Given** the monorepo exists
   **When** I check shared packages
   **Then** `packages/api-client/`, `packages/ui/`, and `packages/utils/` exist

7. **Given** all apps are scaffolded
   **When** running `pnpm dev`
   **Then** all apps start concurrently

8. **Given** TypeScript is configured
   **When** I check tsconfig files
   **Then** strict mode is enabled with shared `tsconfig.base.json`

## Tasks / Subtasks

- [x] Task 1: Initialize pnpm workspace (AC: #1)
  - [x] 1.1 Create `frontend/` directory at project root
  - [x] 1.2 Run `cd frontend && pnpm init`
  - [x] 1.3 Create `pnpm-workspace.yaml` with `apps/*` and `packages/*`
  - [x] 1.4 Create `.npmrc` with required settings for Expo compatibility

- [x] Task 2: Add Turborepo (AC: #2)
  - [x] 2.1 Run `pnpm add -D turbo`
  - [x] 2.2 Create `turbo.json` with build/dev/lint/test pipelines
  - [x] 2.3 Add turbo scripts to root `package.json`

- [x] Task 3: Create shared packages structure (AC: #6)
  - [x] 3.1 Create `packages/api-client/` with `package.json`
  - [x] 3.2 Create `packages/ui/` with `package.json`
  - [x] 3.3 Create `packages/utils/` with `package.json`
  - [x] 3.4 Initialize each package with TypeScript

- [x] Task 4: Scaffold consumer-mobile Expo app (AC: #3)
  - [x] 4.1 Run `npx create-expo-app@latest apps/consumer-mobile --template blank-typescript`
  - [x] 4.2 Update `package.json` name to `@sl/consumer-mobile`
  - [x] 4.3 Configure Expo Router for file-based navigation
  - [x] 4.4 Add workspace dependencies

- [x] Task 5: Scaffold gym-mobile Expo app (AC: #4)
  - [x] 5.1 Run `npx create-expo-app@latest apps/gym-mobile --template blank-typescript`
  - [x] 5.2 Update `package.json` name to `@sl/gym-mobile`
  - [x] 5.3 Configure Expo Router for file-based navigation
  - [x] 5.4 Add workspace dependencies

- [x] Task 6: Scaffold web Vite + React app (AC: #5)
  - [x] 6.1 Run `pnpm create vite apps/web --template react-ts`
  - [x] 6.2 Update `package.json` name to `@sl/web`
  - [x] 6.3 Add workspace dependencies

- [x] Task 7: Configure TypeScript (AC: #8)
  - [x] 7.1 Create `tsconfig.base.json` with strict mode and shared settings
  - [x] 7.2 Update each app's `tsconfig.json` to extend base
  - [x] 7.3 Configure path aliases for workspace packages

- [x] Task 8: Verify all apps run (AC: #7)
  - [x] 8.1 Run `pnpm install` to link all workspaces
  - [x] 8.2 Run `pnpm dev` to start all apps
  - [x] 8.3 Verify consumer-mobile starts on Expo
  - [x] 8.4 Verify gym-mobile starts on Expo (same config as consumer-mobile)
  - [x] 8.5 Verify web starts on localhost

## Dev Notes

### Previous Story Intelligence

From Story 0.1:
- Backend lives at `backend/` (sibling to frontend)
- Template's React frontend was NOT used
- Project root structure: `backend/` + `frontend/`

### Required Directory Structure

```
frontend/
├── apps/
│   ├── consumer-mobile/    # Expo React Native (SDK 54)
│   │   ├── app/            # Expo Router screens
│   │   ├── package.json    # name: "@sl/consumer-mobile"
│   │   └── tsconfig.json   # extends tsconfig.base.json
│   ├── gym-mobile/         # Expo React Native (SDK 54)
│   │   ├── app/            # Expo Router screens
│   │   ├── package.json    # name: "@sl/gym-mobile"
│   │   └── tsconfig.json
│   └── web/                # Vite + React
│       ├── src/
│       ├── package.json    # name: "@sl/web"
│       └── tsconfig.json
│
├── packages/
│   ├── api-client/         # Generated API client + TanStack Query hooks
│   │   ├── src/
│   │   └── package.json    # name: "@sl/api-client"
│   ├── ui/                 # Shared UI components (NativeWind)
│   │   ├── src/
│   │   └── package.json    # name: "@sl/ui"
│   └── utils/              # Shared utilities
│       ├── src/
│       └── package.json    # name: "@sl/utils"
│
├── package.json            # Root workspace package
├── pnpm-workspace.yaml     # Workspace config
├── turbo.json              # Turborepo config
├── tsconfig.base.json      # Shared TypeScript config
└── .npmrc                  # pnpm configuration
```

### Critical Configuration Files

**pnpm-workspace.yaml:**
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

**.npmrc (CRITICAL for Expo/Metro compatibility):**
```
node-linker=hoisted
shamefully-hoist=true
auto-install-peers=true
dedupe-injected-deps=true
```

**turbo.json:**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "type-check": {
      "dependsOn": ["^build"]
    }
  }
}
```

**tsconfig.base.json:**
```json
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@sl/api-client": ["packages/api-client/src"],
      "@sl/ui": ["packages/ui/src"],
      "@sl/utils": ["packages/utils/src"]
    }
  }
}
```

### Expo SDK 54 Notes (Latest as of 2026-01-21)

**Automatic Metro configuration:**
- Since SDK 52, Expo's Metro config has built-in monorepo support
- Uses `expo/metro-config` - no manual Metro configuration needed
- Automatically detects pnpm workspaces

**Expo Router:**
- File-based routing in `app/` directory
- Deep linking support built-in
- Required for navigation per architecture

**Critical Version Constraint:**
> "React Native only supports a single version per monorepo"

Ensure all Expo apps use the same React Native version!

### Package Naming Convention

| Package | Name | Import |
|---------|------|--------|
| Consumer Mobile | `@sl/consumer-mobile` | N/A (app) |
| Gym Mobile | `@sl/gym-mobile` | N/A (app) |
| Web | `@sl/web` | N/A (app) |
| API Client | `@sl/api-client` | `import { ... } from '@sl/api-client'` |
| UI Components | `@sl/ui` | `import { Button } from '@sl/ui'` |
| Utilities | `@sl/utils` | `import { formatDate } from '@sl/utils'` |

### Naming Conventions (TypeScript)

| Element | Convention | Example |
|---------|------------|---------|
| Functions/variables | camelCase | `getGymById`, `consumerId` |
| Components | PascalCase | `GymCard`, `BookingList` |
| Types/Interfaces | PascalCase | `Gym`, `BookingResponse` |
| Constants | SCREAMING_SNAKE | `MAX_RETRY_ATTEMPTS` |
| Files (components) | PascalCase | `GymCard.tsx` |
| Files (utils) | camelCase | `formatDate.ts` |

**Source:** [architecture.md - Code Naming, project-context.md]

### What NOT to Do

- Do NOT use npm or yarn - use pnpm only
- Do NOT skip `.npmrc` configuration (Metro will fail)
- Do NOT create Metro config manually (SDK 54 auto-detects)
- Do NOT use different React Native versions across apps
- Do NOT put business logic in apps - use shared packages
- Do NOT skip TypeScript strict mode

### Dependencies to Install

**Root (devDependencies):**
- `turbo`
- `typescript`
- `@types/node`

**Expo Apps:**
- `expo` (SDK 54)
- `expo-router`
- `react-native`
- `react`
- `typescript`

**Web App:**
- `vite`
- `react`
- `react-dom`
- `typescript`
- `@vitejs/plugin-react`

### References

- [Source: architecture.md#Repository-Structure]
- [Source: architecture.md#Frontend-Structure-(Monorepo)]
- [Source: project-context.md#Frontend]
- [Source: epics.md#Story-0.2]
- [Expo Monorepo Guide](https://docs.expo.dev/guides/monorepos/)
- [byCedric Expo Monorepo Example](https://github.com/byCedric/expo-monorepo-example)
- [Turborepo Documentation](https://turborepo.dev/docs/getting-started/examples)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- expo-router@~5.0.12 not found - used ~6.0.22 (latest compatible with SDK 54)
- react-native-screens@~5.0.0 not found - used ~4.20.0 (latest available)
- Peer dependency warnings for react/react-dom versions (non-blocking)

### Completion Notes List

1. **Monorepo Structure**: Created `frontend/` directory with pnpm workspace and Turborepo
2. **Apps Created**:
   - `@sl/consumer-mobile` - Expo SDK 54 with expo-router 6.x
   - `@sl/gym-mobile` - Expo SDK 54 with expo-router 6.x
   - `@sl/web` - Vite 7.x with React 19
3. **Shared Packages**: Created `@sl/api-client`, `@sl/ui`, `@sl/utils` with TypeScript
4. **TypeScript Config**: Shared `tsconfig.base.json` with strict mode and path aliases
5. **Version Notes**: Used latest available Expo Router (6.0.22) instead of documented 5.0.12
6. **Both Expo apps** share same React Native version (0.81.5) for monorepo compatibility

### Change Log

| Date | Change |
|------|--------|
| 2026-01-21 | Created frontend directory with pnpm workspace |
| 2026-01-21 | Added Turborepo with build/dev/lint/test pipelines |
| 2026-01-21 | Created shared packages (api-client, ui, utils) |
| 2026-01-21 | Scaffolded consumer-mobile Expo app with expo-router |
| 2026-01-21 | Scaffolded gym-mobile Expo app with expo-router |
| 2026-01-21 | Scaffolded web Vite + React app |
| 2026-01-21 | Configured TypeScript with strict mode and path aliases |
| 2026-01-21 | Verified all apps start successfully |

### File List

**Created Files:**
- `frontend/package.json` - Root workspace package
- `frontend/pnpm-workspace.yaml` - Workspace config
- `frontend/turbo.json` - Turborepo config
- `frontend/tsconfig.base.json` - Shared TypeScript config
- `frontend/.npmrc` - pnpm configuration for Expo compatibility
- `frontend/pnpm-lock.yaml` - Lock file

**Apps:**
- `frontend/apps/consumer-mobile/` - Expo app with expo-router
  - `app/_layout.tsx`, `app/index.tsx` - Expo Router screens
  - `package.json`, `app.json`, `tsconfig.json`
- `frontend/apps/gym-mobile/` - Expo app with expo-router
  - `app/_layout.tsx`, `app/index.tsx` - Expo Router screens
  - `package.json`, `app.json`, `tsconfig.json`
- `frontend/apps/web/` - Vite + React app
  - `src/`, `package.json`, `tsconfig.json`, `tsconfig.app.json`

**Packages:**
- `frontend/packages/api-client/` - API client package
  - `src/index.ts`, `package.json`, `tsconfig.json`
- `frontend/packages/ui/` - Shared UI components
  - `src/index.ts`, `package.json`, `tsconfig.json`
- `frontend/packages/utils/` - Shared utilities
  - `src/index.ts`, `package.json`, `tsconfig.json`

### Local Development Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
pnpm install

# Run all apps concurrently
pnpm dev

# Or run individual apps
pnpm --filter @sl/web dev           # Web on http://localhost:5173
pnpm --filter @sl/consumer-mobile start  # Expo on http://localhost:8081
pnpm --filter @sl/gym-mobile start       # Expo on http://localhost:8081
```

