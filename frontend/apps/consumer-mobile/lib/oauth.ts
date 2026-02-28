/**
 * OAuth helpers for consumer mobile app.
 *
 * Uses expo-web-browser to open backend OAuth URLs in system browser.
 * Backend redirects through Google/Apple, then back to app via deep link.
 */

import * as WebBrowser from 'expo-web-browser';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl
  ?? process.env.EXPO_PUBLIC_API_BASE_URL
  ?? 'http://localhost:8000';

const REDIRECT_URI = 'studioloop-consumer://oauth-callback';

interface OAuthResult {
  type: 'success';
  access_token: string;
  refresh_token: string;
} | {
  type: 'error';
  error: string;
  error_message?: string;
} | {
  type: 'dismiss';
}

function parseOAuthResult(url: string): OAuthResult {
  const hashIndex = url.indexOf('#');
  if (hashIndex === -1) {
    return { type: 'error', error: 'NO_FRAGMENT', error_message: 'No authentication data received' };
  }

  const params = new URLSearchParams(url.substring(hashIndex + 1));

  const error = params.get('error');
  if (error) {
    return {
      type: 'error',
      error,
      error_message: params.get('error_message') ?? undefined,
    };
  }

  const access_token = params.get('access_token');
  const refresh_token = params.get('refresh_token');

  if (!access_token || !refresh_token) {
    return { type: 'error', error: 'MISSING_TOKENS', error_message: 'Missing authentication tokens' };
  }

  return { type: 'success', access_token, refresh_token };
}

export async function startGoogleLogin(): Promise<OAuthResult> {
  const url = `${API_BASE_URL}/api/v1/auth/consumer/google?redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;

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
  const url = `${API_BASE_URL}/api/v1/auth/consumer/apple?redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;

  const result = await WebBrowser.openAuthSessionAsync(url, REDIRECT_URI);

  if (result.type === 'cancel' || result.type === 'dismiss') {
    return { type: 'dismiss' };
  }

  if (result.type === 'success' && result.url) {
    return parseOAuthResult(result.url);
  }

  return { type: 'error', error: 'BROWSER_ERROR', error_message: 'Browser session failed' };
}
