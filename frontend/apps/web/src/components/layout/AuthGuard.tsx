import { Navigate, Outlet } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { loginTestToken } from '@sl/api-client';
import { getAccessToken, getAuthHeaders } from '../../lib/apiAuth';

export function AuthGuard() {
  const token = getAccessToken();

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['admin-me'],
    queryFn: async () => {
      const result = await loginTestToken({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
    enabled: !!token,
    retry: false,
  });

  if (!token) {
    return <Navigate to="/auth/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-sm text-gray-500">Verifying access...</p>
      </div>
    );
  }

  if (error || !user?.is_superuser) {
    localStorage.removeItem('access_token');
    return <Navigate to="/auth/login" replace />;
  }

  return <Outlet />;
}
