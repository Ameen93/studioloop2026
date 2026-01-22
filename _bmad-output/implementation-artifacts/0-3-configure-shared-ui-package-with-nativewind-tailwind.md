# Story 0.3: Configure Shared UI Package with NativeWind/Tailwind

Status: ready-for-dev

## Story

As a **developer**,
I want a shared UI package using NativeWind (mobile) and Tailwind CSS (web),
so that components have consistent styling across all 4 frontend apps.

## Acceptance Criteria

1. **Given** the `packages/ui` directory exists
   **When** I configure NativeWind v4 for mobile apps and Tailwind CSS v4 for web apps
   **Then** `packages/ui/tailwind.config.js` defines shared design tokens (colors, spacing, typography)

2. **Given** NativeWind is configured
   **When** mobile apps (consumer-mobile, gym-mobile) import components from `@sl/ui`
   **Then** components use `className` props and render correctly with NativeWind styling

3. **Given** Tailwind CSS is configured
   **When** web apps (gym-web, consumer-web) import components from `@sl/ui`
   **Then** components render correctly with Tailwind CSS styling

4. **Given** the shared UI package
   **When** I check primitive components
   **Then** Button, Input, Card, and Modal primitives are created and functional on all platforms

5. **Given** all components are implemented
   **When** tested on iOS, Android, and web
   **Then** components render correctly on all platforms (iOS simulator, Android emulator, web browsers)

## Tasks / Subtasks

- [ ] Task 1: Configure NativeWind v4 for mobile apps (AC: #1, #2)
  - [ ] 1.1 Install NativeWind v4.2.1+ and Tailwind CSS v3.4.x in mobile apps
  - [ ] 1.2 Configure babel.config.js with nativewind/babel preset
  - [ ] 1.3 Configure Metro bundler with withNativeWind wrapper
  - [ ] 1.4 Create global.css with Tailwind directives
  - [ ] 1.5 Import global.css in app/_layout.tsx

- [ ] Task 2: Configure Tailwind CSS v4 for web apps (AC: #1, #3)
  - [ ] 2.1 Install Tailwind CSS v4 in gym-web and consumer-web (when created)
  - [ ] 2.2 Create CSS-first theme configuration with @theme directive
  - [ ] 2.3 Configure Vite to process Tailwind CSS
  - [ ] 2.4 Import tailwind CSS in main entry file

- [ ] Task 3: Create shared design tokens (AC: #1)
  - [ ] 3.1 Create `packages/ui/src/tokens/colors.ts` with brand palette
  - [ ] 3.2 Create `packages/ui/src/tokens/spacing.ts` with consistent spacing scale
  - [ ] 3.3 Create `packages/ui/src/tokens/typography.ts` with font definitions
  - [ ] 3.4 Create `packages/ui/tailwind.config.js` as shared preset (Tailwind v3 syntax for NativeWind)
  - [ ] 3.5 Create `packages/ui/theme.css` for Tailwind v4 web apps

- [ ] Task 4: Create Button primitive (AC: #4)
  - [ ] 4.1 Create `packages/ui/src/primitives/Button.tsx` with platform detection
  - [ ] 4.2 Implement variants: primary, secondary, outline, ghost
  - [ ] 4.3 Implement sizes: sm, md, lg
  - [ ] 4.4 Add loading state with spinner
  - [ ] 4.5 Export from packages/ui/src/index.ts

- [ ] Task 5: Create Input primitive (AC: #4)
  - [ ] 5.1 Create `packages/ui/src/primitives/Input.tsx` with platform detection
  - [ ] 5.2 Implement label, placeholder, error states
  - [ ] 5.3 Implement sizes: sm, md, lg
  - [ ] 5.4 Export from packages/ui/src/index.ts

- [ ] Task 6: Create Card primitive (AC: #4)
  - [ ] 6.1 Create `packages/ui/src/primitives/Card.tsx` with platform detection
  - [ ] 6.2 Implement variants: default, elevated, outlined
  - [ ] 6.3 Add CardHeader, CardContent, CardFooter sub-components
  - [ ] 6.4 Export from packages/ui/src/index.ts

- [ ] Task 7: Create Modal primitive (AC: #4)
  - [ ] 7.1 Create `packages/ui/src/primitives/Modal.tsx` with platform detection
  - [ ] 7.2 Implement title, close button, overlay
  - [ ] 7.3 Handle keyboard dismissal on mobile
  - [ ] 7.4 Export from packages/ui/src/index.ts

- [ ] Task 8: Update packages/ui package.json (AC: #2, #3)
  - [ ] 8.1 Add NativeWind and Tailwind dependencies
  - [ ] 8.2 Configure conditional exports for web/native
  - [ ] 8.3 Add peer dependencies for React/React Native

- [ ] Task 9: Verify components on all platforms (AC: #5)
  - [ ] 9.1 Test Button on web, iOS, Android
  - [ ] 9.2 Test Input on web, iOS, Android
  - [ ] 9.3 Test Card on web, iOS, Android
  - [ ] 9.4 Test Modal on web, iOS, Android
  - [ ] 9.5 Document any platform-specific quirks

## Dev Notes

### Previous Story Intelligence

From Story 0.2:
- Frontend monorepo at `frontend/` with Turborepo + pnpm
- Apps: `@sl/consumer-mobile`, `@sl/gym-mobile`, `@sl/web` (single web app currently)
- Packages: `@sl/api-client`, `@sl/ui`, `@sl/utils`
- Expo SDK 54 with expo-router 6.x
- React 19.1.0, React Native 0.81.5
- TypeScript strict mode enabled
- pnpm workspaces with hoisted node_modules (Metro compatibility)

**Current State of @sl/ui:**
- Empty package with only version export
- No styling dependencies installed
- No components created yet

**Note:** Architecture specifies 4 apps (gym-web, consumer-web, consumer-mobile, gym-mobile) but Story 0.2 only created a single `apps/web/`. The gym-web and consumer-web split may need to happen in a future story. For now, configure the single web app.

### Critical Version Compatibility

**CRITICAL: NativeWind v4 requires Tailwind CSS v3, NOT v4!**

For this story, we have two options:
1. **Option A (Recommended):** Use NativeWind v4 + Tailwind v3.4.x for mobile, Tailwind v4 for web
   - Different Tailwind versions between mobile and web
   - More complex but uses latest web features

2. **Option B:** Use NativeWind v5 + Tailwind v4 for all
   - Unified Tailwind v4 across all platforms
   - Requires NativeWind v5 (ensure stable)

**Per research, recommend Option A** as NativeWind v4.2.1+ is proven stable with Expo SDK 54.

### Required Package Versions

**Mobile Apps (NativeWind v4):**
```json
{
  "dependencies": {
    "nativewind": "^4.2.1",
    "react-native-reanimated": "~4.1.1"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.17"
  }
}
```

**Web Apps (Tailwind v4):**
```json
{
  "devDependencies": {
    "tailwindcss": "^4.1.0",
    "@tailwindcss/vite": "^4.1.0"
  }
}
```

**Shared UI Package:**
```json
{
  "dependencies": {
    "clsx": "^2.1.0"
  },
  "peerDependencies": {
    "react": ">=18.0.0",
    "react-native": ">=0.73.0",
    "nativewind": ">=4.0.0",
    "tailwindcss": ">=3.4.0"
  }
}
```

### File Structure to Create

```
frontend/packages/ui/
├── package.json
├── tsconfig.json
├── tailwind.config.js     # Shared preset (Tailwind v3 syntax)
├── theme.css              # Tailwind v4 CSS-first tokens (for web)
│
└── src/
    ├── index.ts           # Main exports
    │
    ├── tokens/
    │   ├── colors.ts      # Brand colors
    │   ├── spacing.ts     # Spacing scale
    │   └── typography.ts  # Font definitions
    │
    └── primitives/
        ├── Button.tsx     # Platform-aware Button
        ├── Input.tsx      # Platform-aware Input
        ├── Card.tsx       # Platform-aware Card
        └── Modal.tsx      # Platform-aware Modal
```

### NativeWind Configuration (Mobile Apps)

**babel.config.js:**
```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ['babel-preset-expo', { jsxImportSource: 'nativewind' }],
      'nativewind/babel'
    ],
    plugins: ['react-native-reanimated/plugin'],
  };
};
```

**metro.config.js:**
```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

**global.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**tailwind.config.js (Mobile App):**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,jsx,ts,tsx}',
    '../../packages/ui/src/**/*.{js,jsx,ts,tsx}'
  ],
  presets: [require('@sl/ui/tailwind.config')],
};
```

### Tailwind v4 Configuration (Web Apps)

**vite.config.ts:**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

**src/index.css:**
```css
@import "tailwindcss";
@import "@sl/ui/theme.css";
```

### Design Token Specifications

**Colors (StudioLoop Brand):**
```typescript
// packages/ui/src/tokens/colors.ts
export const colors = {
  primary: {
    50: '#f0f5ff',
    100: '#e0ebff',
    200: '#c7d7fe',
    300: '#a4bbfc',
    400: '#7c96f8',
    500: '#5b6ff2',  // Primary brand color
    600: '#4650e6',
    700: '#3a3fd3',
    800: '#3235ab',
    900: '#2d3288',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
};
```

**Spacing Scale:**
```typescript
// packages/ui/src/tokens/spacing.ts
export const spacing = {
  xs: '0.25rem',  // 4px
  sm: '0.5rem',   // 8px
  md: '1rem',     // 16px
  lg: '1.5rem',   // 24px
  xl: '2rem',     // 32px
  '2xl': '3rem',  // 48px
};
```

**Typography:**
```typescript
// packages/ui/src/tokens/typography.ts
export const typography = {
  fontFamily: {
    sans: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    display: '"Inter", ui-sans-serif, system-ui, sans-serif',
  },
  fontSize: {
    xs: '0.75rem',   // 12px
    sm: '0.875rem',  // 14px
    base: '1rem',    // 16px
    lg: '1.125rem',  // 18px
    xl: '1.25rem',   // 20px
    '2xl': '1.5rem', // 24px
  },
};
```

### Platform Detection Pattern

```typescript
import { Platform } from 'react-native';

// Use for conditional rendering
if (Platform.OS === 'web') {
  return <div className={className}>{children}</div>;
}
return <View className={className}>{children}</View>;
```

### Component Export Pattern

```typescript
// packages/ui/src/index.ts
export { Button } from './primitives/Button';
export type { ButtonProps } from './primitives/Button';

export { Input } from './primitives/Input';
export type { InputProps } from './primitives/Input';

export { Card, CardHeader, CardContent, CardFooter } from './primitives/Card';
export type { CardProps } from './primitives/Card';

export { Modal } from './primitives/Modal';
export type { ModalProps } from './primitives/Modal';

// Re-export tokens
export * from './tokens/colors';
export * from './tokens/spacing';
export * from './tokens/typography';
```

### What NOT to Do

- **DO NOT** use Tailwind v4 with NativeWind v4 (incompatible)
- **DO NOT** skip react-native-reanimated (required for NativeWind v4)
- **DO NOT** use `styled()` wrapper (removed in NativeWind v4)
- **DO NOT** use rem units in NativeWind without understanding default is 14 (not 16)
- **DO NOT** use AsyncStorage for any data - use MMKV per architecture
- **DO NOT** create platform-specific files (.web.tsx, .native.tsx) unless absolutely necessary - prefer Platform.OS checks

### References

- [Source: architecture.md#Frontend-Structure-(Monorepo)]
- [Source: architecture.md#Shared-UI-Package]
- [Source: project-context.md#Frontend]
- [Source: epics.md#Story-0.3]
- [NativeWind v4 Documentation](https://www.nativewind.dev/v4/overview)
- [NativeWind Monorepo Guide](https://www.nativewind.dev/docs/guides/using-with-monorepos)
- [Tailwind CSS v4 Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Tailwind CSS v4 Theme Configuration](https://tailwindcss.com/docs/theme)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### Change Log

| Date | Change |
|------|--------|

### File List

**Files to Create:**
- `frontend/packages/ui/tailwind.config.js` - Shared Tailwind preset
- `frontend/packages/ui/theme.css` - Tailwind v4 CSS-first tokens
- `frontend/packages/ui/src/tokens/colors.ts`
- `frontend/packages/ui/src/tokens/spacing.ts`
- `frontend/packages/ui/src/tokens/typography.ts`
- `frontend/packages/ui/src/primitives/Button.tsx`
- `frontend/packages/ui/src/primitives/Input.tsx`
- `frontend/packages/ui/src/primitives/Card.tsx`
- `frontend/packages/ui/src/primitives/Modal.tsx`

**Files to Modify:**
- `frontend/packages/ui/package.json` - Add dependencies
- `frontend/packages/ui/src/index.ts` - Export components
- `frontend/apps/consumer-mobile/package.json` - Add NativeWind deps
- `frontend/apps/consumer-mobile/babel.config.js` - NativeWind preset
- `frontend/apps/consumer-mobile/metro.config.js` - withNativeWind
- `frontend/apps/consumer-mobile/tailwind.config.js` - Create
- `frontend/apps/consumer-mobile/global.css` - Create
- `frontend/apps/consumer-mobile/app/_layout.tsx` - Import global.css
- `frontend/apps/gym-mobile/` - Same changes as consumer-mobile
- `frontend/apps/web/package.json` - Add Tailwind v4 deps
- `frontend/apps/web/vite.config.ts` - Add Tailwind plugin
- `frontend/apps/web/src/index.css` - Import Tailwind

### Local Development Verification

```bash
# Navigate to frontend
cd frontend

# Install new dependencies
pnpm install

# Verify mobile apps start
pnpm --filter @sl/consumer-mobile start
pnpm --filter @sl/gym-mobile start

# Verify web app starts
pnpm --filter @sl/web dev

# Run type checks
pnpm type-check
```
