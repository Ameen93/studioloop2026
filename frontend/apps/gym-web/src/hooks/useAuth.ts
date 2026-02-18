/**
 * Auth hook for gym staff authentication.
 *
 * Manages staff JWT tokens in localStorage and provides
 * login/logout/auth-check utilities.
 */

import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router';

const ACCESS_TOKEN_KEY = 'gym_staff_access_token';
const REFRESH_TOKEN_KEY = 'gym_staff_refresh_token';
const STAFF_INFO_KEY = 'gym_staff_info';

export interface StaffInfo {
  id: string;
  email: string;
  full_name: string;
  role: string;
  gym_id: string;
  gym_name: string;
}

export function useAuth() {
  const navigate = useNavigate();

  const isAuthenticated = useMemo(() => {
    return !!localStorage.getItem(ACCESS_TOKEN_KEY);
  }, []);

  const accessToken = useMemo(() => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }, []);

  const staffInfo = useMemo((): StaffInfo | null => {
    const raw = localStorage.getItem(STAFF_INFO_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as StaffInfo;
    } catch {
      return null;
    }
  }, []);

  const login = useCallback(
    (tokens: { access_token: string; refresh_token: string }, staff: StaffInfo) => {
      localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
      localStorage.setItem(STAFF_INFO_KEY, JSON.stringify(staff));
      navigate('/dashboard');
    },
    [navigate],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(STAFF_INFO_KEY);
    navigate('/login');
  }, [navigate]);

  return {
    isAuthenticated,
    accessToken,
    staffInfo,
    login,
    logout,
  };
}
