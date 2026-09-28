/**
 * Staff OAuth callback handler.
 *
 * Parses tokens and staff info from URL fragment after Google/Apple OAuth redirect.
 * Stores in localStorage and navigates to dashboard.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

const ACCESS_TOKEN_KEY = 'gym_staff_access_token';
const REFRESH_TOKEN_KEY = 'gym_staff_refresh_token';
const STAFF_INFO_KEY = 'gym_staff_info';

type StaffSession = {
  accessToken: string;
  refreshToken: string;
  staffId: string;
  role: string;
  gymId: string;
  gymName: string;
};

type CallbackResult = { error: string } | { error: null; session: StaffSession };

/**
 * The redirect fragment is already in the URL when this route mounts, so the
 * outcome is derivable at render time. Reading it here rather than setting
 * state inside an effect avoids a cascading render.
 */
function readCallbackFragment(): CallbackResult {
  const params = new URLSearchParams(window.location.hash.substring(1));

  const errorCode = params.get('error');
  if (errorCode) {
    if (errorCode === 'NO_STAFF_ACCOUNT') {
      return {
        error:
          'No staff account found for this email. Your gym administrator must create your account first.',
      };
    }
    return {
      error: params.get('error_message') || 'OAuth sign-in failed. Please try again.',
    };
  }

  const accessToken = params.get('access_token');
  const refreshToken = params.get('refresh_token');
  const staffId = params.get('staff_id');
  const role = params.get('role');
  const gymId = params.get('gym_id');

  if (!accessToken || !refreshToken || !staffId || !role || !gymId) {
    return { error: 'Missing authentication data. Please try again.' };
  }

  return {
    error: null,
    session: {
      accessToken,
      refreshToken,
      staffId,
      role,
      gymId,
      gymName: params.get('gym_name') || '',
    },
  };
}

export function OAuthCallback() {
  const navigate = useNavigate();
  const [result] = useState(readCallbackFragment);
  const error = result.error;

  useEffect(() => {
    if (result.error !== null) {
      return;
    }

    const { accessToken, refreshToken, staffId, role, gymId, gymName } = result.session;

    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(
      STAFF_INFO_KEY,
      JSON.stringify({
        id: staffId,
        role,
        gym_id: gymId,
        gym_name: gymName,
      }),
    );

    navigate('/dashboard', { replace: true });
  }, [navigate, result]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full text-center space-y-4">
          <div className="mx-auto w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
            <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Sign-in failed</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={() => navigate('/login', { replace: true })}
            className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-gold-600 bg-gold-50 rounded-lg hover:bg-gold-100 transition-colors"
          >
            Back to sign in
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-600 mx-auto" />
        <p className="mt-4 text-gray-600">Completing sign-in...</p>
      </div>
    </div>
  );
}

export default OAuthCallback;
