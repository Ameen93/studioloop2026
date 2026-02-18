/**
 * Consumer authentication hook.
 *
 * Manages access/refresh tokens in localStorage and provides
 * authentication state for the consumer web app.
 */

import { useState, useCallback } from 'react';

const ACCESS_TOKEN_KEY = 'consumer_access_token';
const REFRESH_TOKEN_KEY = 'consumer_refresh_token';
const CONSUMER_KEY = 'consumer_profile';

export interface ConsumerProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  avatar_url?: string | null;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    () => !!localStorage.getItem(ACCESS_TOKEN_KEY),
  );

  const [consumer, setConsumer] = useState<ConsumerProfile | null>(() => {
    const stored = localStorage.getItem(CONSUMER_KEY);
    return stored ? (JSON.parse(stored) as ConsumerProfile) : null;
  });

  const login = useCallback(
    (accessToken: string, refreshToken: string, profile?: ConsumerProfile) => {
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
      if (profile) {
        localStorage.setItem(CONSUMER_KEY, JSON.stringify(profile));
        setConsumer(profile);
      }
      setIsAuthenticated(true);
    },
    [],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(CONSUMER_KEY);
    setIsAuthenticated(false);
    setConsumer(null);
  }, []);

  const getAccessToken = useCallback((): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }, []);

  const getRefreshToken = useCallback((): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }, []);

  const updateProfile = useCallback((profile: ConsumerProfile) => {
    localStorage.setItem(CONSUMER_KEY, JSON.stringify(profile));
    setConsumer(profile);
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
