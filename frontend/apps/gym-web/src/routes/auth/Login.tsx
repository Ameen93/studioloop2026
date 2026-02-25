/**
 * Staff login page.
 *
 * Allows gym staff to log in with email and password.
 * On success, stores JWT tokens in localStorage and redirects to /dashboard.
 *
 * Uses generated API client for staff auth endpoints.
 */

import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router';
import { staffAuthLoginStaff } from '@sl/api-client';

const ACCESS_TOKEN_KEY = 'gym_staff_access_token';
const REFRESH_TOKEN_KEY = 'gym_staff_refresh_token';
const STAFF_INFO_KEY = 'gym_staff_info';

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export function Login() {
  const navigate = useNavigate();
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (formData: FormData): { email: string; password: string } | null => {
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    const newErrors: FormErrors = {};

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password || password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return null;
    }

    setErrors({});
    return { email, password };
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data = validateForm(formData);

    if (!data) return;

    setIsLoading(true);
    try {
      const response = await staffAuthLoginStaff({
        body: data,
        throwOnError: true,
      });
      const result = response.data;
      if (!result) {
        setErrors({ general: 'Login failed. Please try again.' });
        return;
      }
      onLoginSuccess(result);
    } catch (error: unknown) {
      const err = error as {
        body?: { detail?: { code?: string } };
        detail?: { code?: string };
      };
      const code = err?.body?.detail?.code || err?.detail?.code;

      if (code === 'INVALID_CREDENTIALS') {
        setErrors({ general: 'Invalid email or password' });
      } else if (code === 'ACCOUNT_DISABLED') {
        setErrors({ general: 'Your account has been disabled. Contact your gym owner.' });
      } else {
        setErrors({ general: 'Login failed. Please try again.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const onLoginSuccess = (result: {
    access_token: string;
    refresh_token: string;
    staff_id: string;
    role: string;
    gym_id: string;
  }) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, result.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, result.refresh_token);
    localStorage.setItem(
      STAFF_INFO_KEY,
      JSON.stringify({
        id: result.staff_id,
        role: result.role,
        gym_id: result.gym_id,
      }),
    );
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-3xl font-bold text-gray-900">StudioLoop</h1>
          <h2 className="mt-2 text-center text-xl text-gray-600">Gym Management Portal</h2>
          <p className="mt-4 text-center text-sm text-gray-500">
            Sign in with your staff credentials
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {errors.general && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-700">{errors.general}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="staff@gym.co.za"
              />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your password"
              />
              {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;
