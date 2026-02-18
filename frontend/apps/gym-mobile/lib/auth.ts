/**
 * Staff auth utility with MMKV token storage.
 *
 * Uses react-native-mmkv (NOT AsyncStorage) per architecture requirements.
 * Provides centralized token management for the gym staff mobile app.
 */

import { createMMKV } from 'react-native-mmkv';

const AUTH_STORAGE_ID = 'gym-staff-auth-storage';

const storage = createMMKV({ id: AUTH_STORAGE_ID });

const KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  STAFF_ID: 'staff_id',
  STAFF_EMAIL: 'staff_email',
  STAFF_NAME: 'staff_name',
  STAFF_ROLE: 'staff_role',
  GYM_ID: 'gym_id',
  GYM_NAME: 'gym_name',
} as const;

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface StaffProfile {
  id: string;
  email: string;
  name: string;
  role: string;
  gymId: string;
  gymName: string;
}

/**
 * Store authentication tokens in MMKV.
 */
export function setTokens(tokens: AuthTokens): void {
  storage.set(KEYS.ACCESS_TOKEN, tokens.access_token);
  storage.set(KEYS.REFRESH_TOKEN, tokens.refresh_token);
}

/**
 * Get the current access token from MMKV.
 */
export function getAccessToken(): string | undefined {
  return storage.getString(KEYS.ACCESS_TOKEN);
}

/**
 * Get the current refresh token from MMKV.
 */
export function getRefreshToken(): string | undefined {
  return storage.getString(KEYS.REFRESH_TOKEN);
}

/**
 * Check if a staff member is currently authenticated.
 */
export function isAuthenticated(): boolean {
  return !!storage.getString(KEYS.ACCESS_TOKEN);
}

/**
 * Store staff profile data in MMKV for quick access.
 */
export function setStaffProfile(profile: StaffProfile): void {
  storage.set(KEYS.STAFF_ID, profile.id);
  storage.set(KEYS.STAFF_EMAIL, profile.email);
  storage.set(KEYS.STAFF_NAME, profile.name);
  storage.set(KEYS.STAFF_ROLE, profile.role);
  storage.set(KEYS.GYM_ID, profile.gymId);
  storage.set(KEYS.GYM_NAME, profile.gymName);
}

/**
 * Get stored staff profile data from MMKV.
 */
export function getStaffProfile(): StaffProfile | null {
  const id = storage.getString(KEYS.STAFF_ID);
  const email = storage.getString(KEYS.STAFF_EMAIL);
  const name = storage.getString(KEYS.STAFF_NAME);
  const role = storage.getString(KEYS.STAFF_ROLE);
  const gymId = storage.getString(KEYS.GYM_ID);
  const gymName = storage.getString(KEYS.GYM_NAME);

  if (!id || !email || !name || !role || !gymId || !gymName) return null;
  return { id, email, name, role, gymId, gymName };
}

/**
 * Get the current gym ID.
 */
export function getGymId(): string | undefined {
  return storage.getString(KEYS.GYM_ID);
}

/**
 * Clear all auth data from MMKV (logout).
 */
export function clearAuth(): void {
  storage.remove(KEYS.ACCESS_TOKEN);
  storage.remove(KEYS.REFRESH_TOKEN);
  storage.remove(KEYS.STAFF_ID);
  storage.remove(KEYS.STAFF_EMAIL);
  storage.remove(KEYS.STAFF_NAME);
  storage.remove(KEYS.STAFF_ROLE);
  storage.remove(KEYS.GYM_ID);
  storage.remove(KEYS.GYM_NAME);
}

/**
 * Get the MMKV storage instance for direct access if needed.
 */
export function getAuthStorage() {
  return storage;
}
