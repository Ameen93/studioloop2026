/**
 * OAuth helpers for gym staff mobile app.
 *
 * Uses expo-web-browser to open backend OAuth URLs in system browser.
 * Backend redirects through Google/Apple, then back to app via deep link.
 * Staff OAuth is link-only (staff must be pre-created by gym owner).
 */

import * as WebBrowser from 'expo-web-browser';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl
  ?? process.env.EXPO_PUBLIC_API_BASE_URL
  ?? 'http://localhost:8000';

const REDIRECT_URI = 'studioloop-gym://oauth-callback';

interface OAuthSuccess {
  type: 'success';
  access_token: string;
  refresh_token: string;
  staff_id: string;
  role: string;
  gym_id: string;
  gym_name: string;
}

interface OAuthError {
  type: 'error';
  error: string;
  error_message?: string;
}

interface OAuthDismiss {
  type: 'dismiss';
}

type OAuthResult = OAuthSuccess | OAuthError | OAuthDismiss;

function parseOAuthResult(url: string): OAuthResult {
  const hashIndex = url.indexOf('#');
  if (hashIndex === -1) {
    return { type: 'error', error: 'NO_FRAGMENT', error_message: 'No authentication data received' };
  }

  const params = new URLSearchParams(url.substring(hashIndex + 1));

  const error = params.get('error');
  if (error) {
    const errorMessage = error === 'NO_STAFF_ACCOUNT'
      ? 'No staff account found for this email. Contact your gym admin.'
      : params.get('error_message') ?? undefined;
    return { type: 'error', error, error_message: errorMessage };
  }

  const access_token = params.get('access_token');
  const refresh_token = params.get('refresh_token');
  const staff_id = params.get('staff_id');
  const role = params.get('role');
  const gym_id = params.get('gym_id');
  const gym_name = params.get('gym_name');

  if (!access_token || !refresh_token || !staff_id || !role || !gym_id) {
    return { type: 'error', error: 'MISSING_DATA', error_message: 'Missing authentication data' };
  }

  return {
    type: 'success',
    access_token,
    refresh_token,
    staff_id,
    role,
    gym_id,
    gym_name: gym_name ?? '',
  };
}

export async function startGoogleLogin(): Promise<OAuthResult> {
  const url = `${API_BASE_URL}/api/v1/auth/staff/google?redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;

  const result = await WebBrowser.openAuthSessionAsync(url, REDIRECT_URI);

  if (result.type === 'cancel' || result.type === 'dismiss') {
    return { type: 'dismiss' };
  }

  if (result.type === 'success' && result.url) {
    return parseOAuthResult(result.url);
  }

  return { type: 'error', error: 'BROWSER_ERROR', error_message: 'Browser session failed' };
}

export async function startAppleLogin(): Promise<OAuthResult> {
  const url = `${API_BASE_URL}/api/v1/auth/staff/apple?redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;

  const result = await WebBrowser.openAuthSessionAsync(url, REDIRECT_URI);

  if (result.type === 'cancel' || result.type === 'dismiss') {
    return { type: 'dismiss' };
  }

  if (result.type === 'success' && result.url) {
    return parseOAuthResult(result.url);
  }

  return { type: 'error', error: 'BROWSER_ERROR', error_message: 'Browser session failed' };
}
