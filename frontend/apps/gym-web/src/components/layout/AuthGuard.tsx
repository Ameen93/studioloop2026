/**
 * Auth guard component.
 *
 * Redirects to /login if no staff access token is found in localStorage.
 * Wraps protected routes with <Outlet />.
 */

import { Navigate, Outlet } from 'react-router';

const ACCESS_TOKEN_KEY = 'gym_staff_access_token';

export function AuthGuard() {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
