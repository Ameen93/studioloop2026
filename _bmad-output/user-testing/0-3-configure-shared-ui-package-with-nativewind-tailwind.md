# QA Checklist: Story 0.3 - Configure Shared UI Package with NativeWind/Tailwind

**Story ID:** 0.3
**Story Title:** Configure Shared UI Package with NativeWind/Tailwind
**Status:** Pending Testing
**Tester:** Ameen
**Test Date:** _______________

---

## Prerequisites

- [ ] Node.js 18+ installed
- [ ] pnpm installed globally (`npm install -g pnpm`)
- [ ] iOS Simulator available (Xcode installed on macOS)
- [ ] Android Emulator available (Android Studio installed)
- [ ] Modern web browser (Chrome, Firefox, or Safari)
- [ ] Expo Go app installed on physical device (optional)

---

## Environment Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install all dependencies
pnpm install

# 3. Verify no installation errors
echo $?  # Should output 0
```

- [ ] Dependencies installed without errors
- [ ] No peer dependency warnings for NativeWind/Tailwind

---

## Test Cases

### TC-1: Shared Tailwind Config Exists
**Acceptance Criterion:** #1

**Steps:**
1. Check that shared Tailwind config exists:
   ```bash
   ls -la packages/ui/tailwind.config.js
   ```
2. Verify it contains design tokens:
   ```bash
   cat packages/ui/tailwind.config.js | grep -E "colors|spacing|fontFamily"
   ```

**Expected Results:**
- [ ] `packages/ui/tailwind.config.js` file exists
- [ ] Config contains colors definition
- [ ] Config contains spacing definition
- [ ] Config contains typography/fontFamily definition

**Actual Results:** _______________

---

### TC-2: NativeWind Configuration (Consumer Mobile)
**Acceptance Criterion:** #2

**Steps:**
1. Check NativeWind is installed:
   ```bash
   cat apps/consumer-mobile/package.json | grep nativewind
   ```
2. Check babel config:
   ```bash
   cat apps/consumer-mobile/babel.config.js | grep nativewind
   ```
3. Check Metro config:
   ```bash
   cat apps/consumer-mobile/metro.config.js | grep withNativeWind
   ```
4. Check global.css exists:
   ```bash
   cat apps/consumer-mobile/global.css
   ```
5. Start consumer-mobile app:
   ```bash
   pnpm --filter @sl/consumer-mobile start
   ```
6. Press `i` for iOS or `a` for Android

**Expected Results:**
- [ ] NativeWind package is in dependencies
- [ ] Babel config includes nativewind/babel preset
- [ ] Metro config uses withNativeWind wrapper
- [ ] global.css contains @tailwind directives
- [ ] App starts without errors
- [ ] No NativeWind-related warnings in console

**Actual Results:** _______________

---

### TC-3: NativeWind Configuration (Gym Mobile)
**Acceptance Criterion:** #2

**Steps:**
1. Check NativeWind is installed:
   ```bash
   cat apps/gym-mobile/package.json | grep nativewind
   ```
2. Start gym-mobile app:
   ```bash
   pnpm --filter @sl/gym-mobile start
   ```
3. Press `i` for iOS or `a` for Android

**Expected Results:**
- [ ] NativeWind package is in dependencies
- [ ] App starts without errors
- [ ] Styling is applied correctly

**Actual Results:** _______________

---

### TC-4: Tailwind CSS v4 Configuration (Web)
**Acceptance Criterion:** #3

**Steps:**
1. Check Tailwind v4 is installed:
   ```bash
   cat apps/web/package.json | grep tailwindcss
   ```
2. Check Vite config includes Tailwind plugin:
   ```bash
   cat apps/web/vite.config.ts | grep tailwind
   ```
3. Start web app:
   ```bash
   pnpm --filter @sl/web dev
   ```
4. Open http://localhost:5173 in browser

**Expected Results:**
- [ ] Tailwind CSS v4.x is in devDependencies
- [ ] Vite config imports @tailwindcss/vite plugin
- [ ] Web app starts without errors
- [ ] No Tailwind-related warnings in console
- [ ] Browser DevTools shows Tailwind classes being applied

**Actual Results:** _______________

---

### TC-5: Button Component
**Acceptance Criterion:** #4

**Steps:**
1. Check Button component exists:
   ```bash
   ls -la packages/ui/src/primitives/Button.tsx
   ```
2. Check Button is exported:
   ```bash
   cat packages/ui/src/index.ts | grep Button
   ```
3. Import and render Button in consumer-mobile:
   ```tsx
   import { Button } from '@sl/ui';
   <Button variant="primary">Test</Button>
   ```
4. Import and render Button in web app:
   ```tsx
   import { Button } from '@sl/ui';
   <Button variant="primary">Test</Button>
   ```

**Expected Results:**
- [ ] Button.tsx file exists in primitives folder
- [ ] Button is exported from index.ts
- [ ] Button renders on iOS simulator
- [ ] Button renders on Android emulator
- [ ] Button renders on web browser
- [ ] Primary variant shows correct styling
- [ ] Secondary variant shows correct styling
- [ ] Different sizes (sm, md, lg) render correctly

**Actual Results:** _______________

---

### TC-6: Input Component
**Acceptance Criterion:** #4

**Steps:**
1. Check Input component exists:
   ```bash
   ls -la packages/ui/src/primitives/Input.tsx
   ```
2. Test Input on each platform with:
   ```tsx
   import { Input } from '@sl/ui';
   <Input label="Email" placeholder="Enter email" />
   <Input label="Password" error="Invalid password" />
   ```

**Expected Results:**
- [ ] Input.tsx file exists
- [ ] Input renders with label on all platforms
- [ ] Input renders with placeholder on all platforms
- [ ] Input shows error state correctly
- [ ] Input is focusable and accepts text input

**Actual Results:** _______________

---

### TC-7: Card Component
**Acceptance Criterion:** #4

**Steps:**
1. Check Card component exists:
   ```bash
   ls -la packages/ui/src/primitives/Card.tsx
   ```
2. Test Card on each platform:
   ```tsx
   import { Card, CardHeader, CardContent } from '@sl/ui';
   <Card>
     <CardHeader>Title</CardHeader>
     <CardContent>Content here</CardContent>
   </Card>
   ```

**Expected Results:**
- [ ] Card.tsx file exists
- [ ] Card renders with correct background and border
- [ ] CardHeader renders correctly
- [ ] CardContent renders correctly
- [ ] Shadow/elevation is visible

**Actual Results:** _______________

---

### TC-8: Modal Component
**Acceptance Criterion:** #4

**Steps:**
1. Check Modal component exists:
   ```bash
   ls -la packages/ui/src/primitives/Modal.tsx
   ```
2. Test Modal on each platform:
   ```tsx
   import { Modal, Button } from '@sl/ui';
   const [open, setOpen] = useState(false);

   <Button onPress={() => setOpen(true)}>Open Modal</Button>
   <Modal isOpen={open} onClose={() => setOpen(false)} title="Test Modal">
     <Text>Modal content</Text>
   </Modal>
   ```

**Expected Results:**
- [ ] Modal.tsx file exists
- [ ] Modal opens when triggered
- [ ] Modal shows overlay/backdrop
- [ ] Modal title displays correctly
- [ ] Modal closes on backdrop tap (mobile) or click (web)
- [ ] Modal closes on close button click

**Actual Results:** _______________

---

### TC-9: Cross-Platform Rendering (iOS)
**Acceptance Criterion:** #5

**Steps:**
1. Start consumer-mobile on iOS:
   ```bash
   pnpm --filter @sl/consumer-mobile start
   # Press 'i' for iOS
   ```
2. Navigate to a screen with UI components
3. Verify all components render correctly

**Expected Results:**
- [ ] App loads without crashes
- [ ] Button styling matches design tokens
- [ ] Input styling matches design tokens
- [ ] Card styling matches design tokens
- [ ] No layout issues or overflow

**Actual Results:** _______________

---

### TC-10: Cross-Platform Rendering (Android)
**Acceptance Criterion:** #5

**Steps:**
1. Start consumer-mobile on Android:
   ```bash
   pnpm --filter @sl/consumer-mobile start
   # Press 'a' for Android
   ```
2. Navigate to a screen with UI components
3. Verify all components render correctly

**Expected Results:**
- [ ] App loads without crashes
- [ ] Button styling matches design tokens
- [ ] Input styling matches design tokens
- [ ] Card styling matches design tokens
- [ ] No layout issues or overflow

**Actual Results:** _______________

---

### TC-11: Cross-Platform Rendering (Web)
**Acceptance Criterion:** #5

**Steps:**
1. Start web app:
   ```bash
   pnpm --filter @sl/web dev
   ```
2. Open http://localhost:5173
3. Verify all components render correctly
4. Test in Chrome, Firefox, and Safari (if available)

**Expected Results:**
- [ ] App loads without errors
- [ ] Button styling matches design tokens
- [ ] Input styling matches design tokens
- [ ] Card styling matches design tokens
- [ ] Responsive layout works correctly
- [ ] Components work in multiple browsers

**Actual Results:** _______________

---

## Edge Cases and Error Scenarios

### EC-1: Missing Tailwind Classes
**Steps:**
1. Use a non-existent Tailwind class:
   ```tsx
   <View className="bg-nonexistent-color" />
   ```

**Expected Results:**
- [ ] App doesn't crash
- [ ] Style is simply not applied
- [ ] Console shows warning (optional)

**Actual Results:** _______________

---

### EC-2: Hot Reload Styling
**Steps:**
1. Start app in development mode
2. Modify a className in a component
3. Save the file

**Expected Results:**
- [ ] Hot reload triggers
- [ ] New styles are applied without full refresh
- [ ] No styling glitches

**Actual Results:** _______________

---

### EC-3: TypeScript Type Safety
**Steps:**
1. Try to pass invalid props to Button:
   ```tsx
   <Button variant="invalid" size="huge" />
   ```

**Expected Results:**
- [ ] TypeScript shows type error
- [ ] IDE provides autocomplete for valid variants
- [ ] IDE provides autocomplete for valid sizes

**Actual Results:** _______________

---

## Rollback Steps

### Full Rollback
```bash
# Remove all NativeWind/Tailwind configurations
cd frontend

# Reset packages/ui to basic state
git checkout -- packages/ui/

# Reset mobile app configs
git checkout -- apps/consumer-mobile/babel.config.js
git checkout -- apps/consumer-mobile/metro.config.js
rm -f apps/consumer-mobile/global.css
rm -f apps/consumer-mobile/tailwind.config.js

git checkout -- apps/gym-mobile/babel.config.js
git checkout -- apps/gym-mobile/metro.config.js
rm -f apps/gym-mobile/global.css
rm -f apps/gym-mobile/tailwind.config.js

# Reset web app config
git checkout -- apps/web/vite.config.ts

# Reinstall dependencies
pnpm install
```

### Partial Rollback (UI Package Only)
```bash
# Reset only UI package
git checkout -- packages/ui/
pnpm install
```

### Environment Cleanup
```bash
# Clear pnpm cache
pnpm store prune

# Clear Metro cache (mobile)
cd apps/consumer-mobile && npx expo start --clear
cd apps/gym-mobile && npx expo start --clear

# Clear Vite cache (web)
cd apps/web && rm -rf node_modules/.vite
```

---

## Sign-Off

### Test Summary

| Test Case | Status |
|-----------|--------|
| TC-1: Shared Tailwind Config | PASS / FAIL |
| TC-2: NativeWind (Consumer Mobile) | PASS / FAIL |
| TC-3: NativeWind (Gym Mobile) | PASS / FAIL |
| TC-4: Tailwind v4 (Web) | PASS / FAIL |
| TC-5: Button Component | PASS / FAIL |
| TC-6: Input Component | PASS / FAIL |
| TC-7: Card Component | PASS / FAIL |
| TC-8: Modal Component | PASS / FAIL |
| TC-9: iOS Rendering | PASS / FAIL |
| TC-10: Android Rendering | PASS / FAIL |
| TC-11: Web Rendering | PASS / FAIL |
| EC-1: Missing Classes | PASS / FAIL |
| EC-2: Hot Reload | PASS / FAIL |
| EC-3: Type Safety | PASS / FAIL |

### Final Verdict

- [ ] **PASS** - All acceptance criteria met, ready for next story
- [ ] **FAIL** - Blocking issues found, requires fixes

### Blocking Issues
_List any issues that prevent story completion:_

1. _______________
2. _______________
3. _______________

### Non-Blocking Notes
_List any observations or minor issues:_

1. _______________
2. _______________
3. _______________

### Sign-Off

**Tester Signature:** _______________

**Date:** _______________

**Next Story:** 0-4-deploy-database-infrastructure-to-fly-io
