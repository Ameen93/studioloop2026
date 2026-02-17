// Type-only smoke test to verify exports work correctly
// This file validates the package's public API surface compiles without errors

// Re-export types to verify they are accessible
// If any of these fail to compile, the exports are broken
export type { UserPublic, ItemPublic, Token, Message } from '../index';
export type { UserCreate, UserRegister, ItemCreate } from '../index';

// Re-export hooks to verify they are accessible
export {
  loginLoginAccessTokenMutation,
  usersReadUsersOptions,
  itemsReadItemsOptions,
  healthHealthCheckOptions,
} from '../hooks';

// Runtime export to verify module loads
export const SMOKE_TEST_PASSED = true;
