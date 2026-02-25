import { Navigate } from 'react-router';
import type { ReactNode } from 'react';

interface AuthGuardProps {
  children: ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/auth/login" replace />;
  }
  return <>{children}</>;
}
