/**
 * Consumer login screen.
 *
 * Allows consumers to login with email and password.
 * Stores tokens in localStorage upon successful login.
 */

import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router';
import { useMutation } from '@tanstack/react-query';
import { consumerAuthLoginConsumer } from '@sl/api-client';
import type { ConsumerLoginRequest } from '@sl/api-client';

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export function Login() {
  const navigate = useNavigate();
  const [errors, setErrors] = useState<FormErrors>({});

  const loginMutation = useMutation({
    mutationFn: async (data: ConsumerLoginRequest) => {
      const response = await consumerAuthLoginConsumer({
        body: data,
        throwOnError: true,
      });

      return response.data;
    },
    onSuccess: (tokens) => {

      // Store tokens in localStorage (AC #2 - web uses memory/localStorage)
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      // Navigate to home screen (AC #3)
      navigate('/');
    },
    onError: (error: unknown) => {
      const err = error as {
        body?: { detail?: { code?: string; message?: string } };
        detail?: { code?: string; message?: string };
      };
      const code = err?.body?.detail?.code || err?.detail?.code;

      if (code === 'EMAIL_NOT_VERIFIED') {
        setErrors({
          general: 'Please verify your email before logging in. Check your inbox for the verification link.',
        });
      } else if (code === 'INVALID_CREDENTIALS') {
        setErrors({ general: 'Invalid email or password' });
      } else {
        setErrors({ general: 'Login failed. Please try again.' });
      }
    },
  });

  const validateForm = (formData: FormData): ConsumerLoginRequest | null => {
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

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data = validateForm(formData);

    if (data) {
      loginMutation.mutate(data);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/auth/register" className="font-medium text-primary-600 hover:text-primary-500">
              Create one
            </Link>
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
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="john@example.com"
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
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your password"
              />
              {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm">
              <Link to="/auth/forgot-password" className="font-medium text-primary-600 hover:text-primary-500">
                Forgot your password?
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;
