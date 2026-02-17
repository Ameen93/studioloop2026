/**
 * Email verification sent confirmation screen.
 *
 * Displayed after successful registration to inform the user
 * to check their email for the verification link.
 */

import { Link } from 'react-router';

export function VerifyEmailSent() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
            <svg
              className="h-8 w-8 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">Check your email</h2>
          <p className="mt-2 text-sm text-gray-600">
            We&apos;ve sent a verification link to your email address. Please click the link to
            verify your account.
          </p>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            The verification link will expire in 24 hours.
          </p>

          <div className="border-t border-gray-200 pt-4">
            <p className="text-sm text-gray-600">
              Didn&apos;t receive the email?{' '}
              <Link
                to="/auth/resend-verification"
                className="font-medium text-primary-600 hover:text-primary-500"
              >
                Click here to resend
              </Link>
            </p>
          </div>

          <div>
            <Link
              to="/auth/login"
              className="text-sm font-medium text-gray-600 hover:text-gray-500"
            >
              Back to login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VerifyEmailSent;
