// Type-only smoke test to verify exports work correctly
// This file validates the package's public API surface compiles without errors

// Re-export types to verify they are accessible
// If any of these fail to compile, the exports are broken
export type { UserPublic, ItemPublic, Token, Message } from '../index';
export type { UserCreate, UserRegister, ItemCreate } from '../index';
export type {
  ConsumerLoginRequest,
  StaffLoginRequest,
  ConsumerToken,
  StaffToken,
} from '../index';

// Re-export hooks to verify they are accessible
export {
  loginLoginAccessTokenMutation,
  usersReadUsersOptions,
  itemsReadItemsOptions,
  healthHealthCheckOptions,
} from '../hooks';

// Critical auth contract-lock exports (compile-time guard against SDK drift)
export {
  consumerAuthLoginConsumer,
  consumerAuthForgotPassword,
  consumerAuthResendVerificationEmail,
  consumerAuthRefreshConsumerToken,
  staffAuthLoginStaff,
  staffAuthForgotPassword,
  staffAuthRefreshStaffToken,
} from '../index';

// Runtime export to verify module loads
export const SMOKE_TEST_PASSED = true;
