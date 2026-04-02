import { client } from '@sl/api-client';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const ACCESS_TOKEN_KEY = 'access_token';

if (apiBaseUrl) {
  client.setConfig({
    baseUrl: apiBaseUrl,
  });
}

client.interceptors.response.use(async (response) => {
  if (response.status === 401) {
    const hadToken = !!localStorage.getItem(ACCESS_TOKEN_KEY);
    if (hadToken) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      if (window.location.pathname !== '/auth/login') {
        window.location.replace('/auth/login');
      }
    }
  }
  return response;
});
