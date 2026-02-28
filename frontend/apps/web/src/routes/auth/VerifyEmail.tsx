/**
 * Email verification screen.
 *
 * Handles the verification token from email link and
 * displays the result to the user.
 */

import { Link, useSearchParams } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { consumerAuthVerifyEmailOptions } from '@sl/api-client/hooks';

export function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const { isSuccess, isError, isPending } = useQuery({
    ...consumerAuthVerifyEmailOptions({
      query: { token: token || '' },
    }),
    enabled: !!token,
    retry: false,
  });

  // Derive status from query state
  const status = !token ? 'no-token' : isPending ? 'loading' : isSuccess ? 'success' : isError ? 'error' : 'loading';

  if (status === 'no-token') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100">
            <svg className="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Invalid link</h2>
          <p className="mt-2 text-sm text-gray-600">
            The verification link is invalid. Please check your email for the correct link.
          </p>
          <div className="mt-6">
            <Link
              to="/auth/resend-verification"
              className="text-gray-700 hover:text-gray-500 font-medium"
            >
              Request a new verification email
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16">
            <svg className="animate-spin h-8 w-8 text-gray-700" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <h2 className="mt-6 text-2xl font-semibold text-gray-900">Verifying your email...</h2>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
            <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Verification failed</h2>
          <p className="mt-2 text-sm text-gray-600">
            The verification link is invalid or has expired.
          </p>
          <div className="mt-6 space-y-4">
            <Link
              to="/auth/resend-verification"
              className="block text-gray-700 hover:text-gray-500 font-medium"
            >
              Request a new verification email
            </Link>
            <Link
              to="/auth/login"
              className="block text-gray-600 hover:text-gray-500 text-sm"
            >
              Back to login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Success
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full text-center">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
          <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Email verified!</h2>
        <p className="mt-2 text-sm text-gray-600">
          Your email has been verified successfully. You can now log in to your account.
        </p>
        <div className="mt-6">
          <Link
            to="/auth/login"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gray-700 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Continue to login
          </Link>
        </div>
      </div>
    </div>
  );
}

export default VerifyEmail;
