import { client, consumerAuthRefreshConsumerToken } from '@sl/api-client';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const ACCESS_TOKEN_KEY = 'consumer_access_token';
const REFRESH_TOKEN_KEY = 'consumer_refresh_token';
const CONSUMER_KEY = 'consumer_profile';
const AUTH_CHANGE_EVENT = 'sl:consumer-auth-change';

let unauthorizedInterceptorRegistered = false;
let refreshInFlight: Promise<string | null> | null = null;

function handleUnauthorizedSession(): void {
  const hadToken = !!localStorage.getItem(ACCESS_TOKEN_KEY);
  if (!hadToken) {
    return;
  }

  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(CONSUMER_KEY);
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));

  if (window.location.pathname !== '/login') {
    window.location.replace('/login');
  }
}

function shouldSkipRefresh(requestUrl: string): boolean {
  return (
    requestUrl.includes('/api/v1/auth/consumer/login') ||
    requestUrl.includes('/api/v1/auth/consumer/register') ||
    requestUrl.includes('/api/v1/auth/consumer/refresh') ||
    requestUrl.includes('/api/v1/auth/consumer/forgot-password') ||
    requestUrl.includes('/api/v1/auth/consumer/reset-password')
  );
}

async function refreshAccessToken(): Promise<string | null> {
  if (refreshInFlight) {
    return refreshInFlight;
  }

  refreshInFlight = (async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      return null;
    }

    try {
      const response = await consumerAuthRefreshConsumerToken({
        body: { refresh_token: refreshToken },
        throwOnError: true,
      });
      const data = response.data;
      if (!data) {
        return null;
      }

      localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
      window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
      return data.access_token;
    } catch {
      return null;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

if (apiBaseUrl) {
  client.setConfig({
    baseUrl: apiBaseUrl,
  });
}

if (!unauthorizedInterceptorRegistered) {
  client.interceptors.response.use(async (response, request, options) => {
    if (response.status !== 401) {
      return response;
    }

    const hadToken = !!localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!hadToken || shouldSkipRefresh(request.url)) {
      handleUnauthorizedSession();
      return response;
    }

    const accessToken = await refreshAccessToken();
    if (!accessToken) {
      handleUnauthorizedSession();
      return response;
    }

    const retryHeaders = new Headers(request.headers);
    retryHeaders.set('Authorization', `Bearer ${accessToken}`);
    const retryRequest = new Request(request, { headers: retryHeaders });
    const retryResponse = await (options.fetch ?? globalThis.fetch)(retryRequest);

    if (retryResponse.status === 401) {
      handleUnauthorizedSession();
    }

    return retryResponse;
  });
  unauthorizedInterceptorRegistered = true;
}
