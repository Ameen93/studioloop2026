import { client } from '@sl/api-client';
import { clearAuth, getAccessToken } from './auth';
import { emitSessionExpired } from './authSession';

const apiBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL;
let unauthorizedInterceptorRegistered = false;

function handleUnauthorizedSession(): void {
  const hadToken = !!getAccessToken();
  if (!hadToken) {
    return;
  }

  clearAuth();
  emitSessionExpired();
}

if (apiBaseUrl) {
  client.setConfig({
    baseUrl: apiBaseUrl,
  });
}

if (!unauthorizedInterceptorRegistered) {
  client.interceptors.error.use((error, response) => {
    if (response.status === 401) {
      handleUnauthorizedSession();
    }
    return error;
  });
  unauthorizedInterceptorRegistered = true;
}
