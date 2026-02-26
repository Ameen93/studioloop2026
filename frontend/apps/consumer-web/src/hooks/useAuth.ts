/**
 * Consumer authentication hook.
 *
 * Manages access/refresh tokens in localStorage and provides
 * authentication state for the consumer web app.
 */

import { useCallback, useMemo, useSyncExternalStore } from 'react';

const ACCESS_TOKEN_KEY = 'consumer_access_token';
const REFRESH_TOKEN_KEY = 'consumer_refresh_token';
const CONSUMER_KEY = 'consumer_profile';
const AUTH_CHANGE_EVENT = 'sl:consumer-auth-change';

export interface ConsumerProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  avatar_url?: string | null;
}

function parseStoredProfile(raw: string | null): ConsumerProfile | null {
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as ConsumerProfile;
  } catch {
    return null;
  }
}

function subscribeAuthChange(onStoreChange: () => void): () => void {
  const handleStorage = (event: StorageEvent) => {
    if (
      event.key === ACCESS_TOKEN_KEY ||
      event.key === REFRESH_TOKEN_KEY ||
      event.key === CONSUMER_KEY
    ) {
      onStoreChange();
    }
  };
  const handleAuthEvent = () => onStoreChange();

  window.addEventListener('storage', handleStorage);
  window.addEventListener(AUTH_CHANGE_EVENT, handleAuthEvent);

  return () => {
    window.removeEventListener('storage', handleStorage);
    window.removeEventListener(AUTH_CHANGE_EVENT, handleAuthEvent);
  };
}

function emitAuthChange(): void {
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
}

export function useAuth() {
  const accessToken = useSyncExternalStore(
    subscribeAuthChange,
    () => localStorage.getItem(ACCESS_TOKEN_KEY),
    () => null,
  );
  const consumerRaw = useSyncExternalStore(
    subscribeAuthChange,
    () => localStorage.getItem(CONSUMER_KEY),
    () => null,
  );

  const isAuthenticated = !!accessToken;
  const consumer = useMemo(() => parseStoredProfile(consumerRaw), [consumerRaw]);

  const login = useCallback(
    (accessToken: string, refreshToken: string, profile?: ConsumerProfile) => {
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
      if (profile) {
        localStorage.setItem(CONSUMER_KEY, JSON.stringify(profile));
      }
      emitAuthChange();
    },
    [],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(CONSUMER_KEY);
    emitAuthChange();
  }, []);

  const getAccessToken = useCallback((): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }, []);

  const getRefreshToken = useCallback((): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }, []);

  const updateProfile = useCallback((profile: ConsumerProfile) => {
    localStorage.setItem(CONSUMER_KEY, JSON.stringify(profile));
    emitAuthChange();
  }, []);

  return {
    isAuthenticated,
    consumer,
    login,
    logout,
    getAccessToken,
    getRefreshToken,
    updateProfile,
  };
}
