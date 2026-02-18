/**
 * Consumer auth utility with MMKV token storage.
 *
 * Uses react-native-mmkv (NOT AsyncStorage) per architecture requirements.
 * Provides centralized token management for the consumer mobile app.
 */

import { createMMKV } from 'react-native-mmkv';

const AUTH_STORAGE_ID = 'consumer-auth-storage';

const storage = createMMKV({ id: AUTH_STORAGE_ID });

// Storage keys
const KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  CONSUMER_ID: 'consumer_id',
  CONSUMER_EMAIL: 'consumer_email',
  CONSUMER_NAME: 'consumer_name',
} as const;

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface ConsumerProfile {
  id: string;
  email: string;
  name: string;
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
 * Check if a user is currently authenticated (has stored tokens).
 */
export function isAuthenticated(): boolean {
  return !!storage.getString(KEYS.ACCESS_TOKEN);
}

/**
 * Store consumer profile data in MMKV for quick access.
 */
export function setConsumerProfile(profile: ConsumerProfile): void {
  storage.set(KEYS.CONSUMER_ID, profile.id);
  storage.set(KEYS.CONSUMER_EMAIL, profile.email);
  storage.set(KEYS.CONSUMER_NAME, profile.name);
}

/**
 * Get stored consumer profile data from MMKV.
 */
export function getConsumerProfile(): ConsumerProfile | null {
  const id = storage.getString(KEYS.CONSUMER_ID);
  const email = storage.getString(KEYS.CONSUMER_EMAIL);
  const name = storage.getString(KEYS.CONSUMER_NAME);

  if (!id || !email || !name) return null;
  return { id, email, name };
}

/**
 * Clear all auth data from MMKV (logout).
 */
export function clearAuth(): void {
  storage.remove(KEYS.ACCESS_TOKEN);
  storage.remove(KEYS.REFRESH_TOKEN);
  storage.remove(KEYS.CONSUMER_ID);
  storage.remove(KEYS.CONSUMER_EMAIL);
  storage.remove(KEYS.CONSUMER_NAME);
}

/**
 * Get the MMKV storage instance for direct access if needed.
 */
export function getAuthStorage() {
  return storage;
}
