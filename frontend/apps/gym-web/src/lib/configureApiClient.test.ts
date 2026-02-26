import { beforeEach, describe, expect, it, vi } from 'vitest';

const mockSetConfig = vi.fn();
const mockUseResponseInterceptor = vi.fn();
const mockRefreshStaffToken = vi.fn();

let registeredResponseInterceptor:
  | ((response: Response, request: Request, options: { fetch?: typeof fetch }) => Promise<Response>)
  | undefined;

vi.mock('@sl/api-client', () => ({
  client: {
    setConfig: mockSetConfig,
    interceptors: {
      response: {
        use: mockUseResponseInterceptor.mockImplementation((fn) => {
          registeredResponseInterceptor = fn;
        }),
      },
    },
  },
  staffAuthRefreshStaffToken: mockRefreshStaffToken,
}));

describe('gym-web configureApiClient', () => {
  beforeEach(async () => {
    vi.resetModules();
    mockSetConfig.mockReset();
    mockUseResponseInterceptor.mockClear();
    mockRefreshStaffToken.mockReset();
    registeredResponseInterceptor = undefined;
    localStorage.clear();
    window.history.replaceState({}, '', '/login');
    await import('./configureApiClient');
  });

  it('refreshes token and retries once on 401', async () => {
    localStorage.setItem('gym_staff_access_token', 'old-access');
    localStorage.setItem('gym_staff_refresh_token', 'old-refresh');
    mockRefreshStaffToken.mockResolvedValue({
      data: {
        access_token: 'new-access',
        refresh_token: 'new-refresh',
        token_type: 'bearer',
        role: 'owner',
        gym_id: 'gym-1',
      },
    });

    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));

    const interceptor = registeredResponseInterceptor;
    expect(interceptor).toBeDefined();

    const request = new Request('http://localhost:8000/api/v1/analytics/gyms/gym-1/dashboard', {
      headers: { Authorization: 'Bearer old-access' },
    });

    const retried = await interceptor!(
      new Response(JSON.stringify({ detail: { code: 'INVALID_TOKEN' } }), { status: 401 }),
      request,
      { fetch: fetchMock as typeof fetch },
    );

    expect(mockRefreshStaffToken).toHaveBeenCalledWith({
      body: { refresh_token: 'old-refresh' },
      throwOnError: true,
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem('gym_staff_access_token')).toBe('new-access');
    expect(localStorage.getItem('gym_staff_refresh_token')).toBe('new-refresh');
    expect(retried.status).toBe(200);
  });

  it('clears auth when refresh fails', async () => {
    localStorage.setItem('gym_staff_access_token', 'old-access');
    localStorage.setItem('gym_staff_refresh_token', 'old-refresh');
    localStorage.setItem('gym_staff_info', JSON.stringify({ id: 's1' }));
    mockRefreshStaffToken.mockRejectedValue(new Error('refresh failed'));

    const interceptor = registeredResponseInterceptor;
    expect(interceptor).toBeDefined();

    const request = new Request('http://localhost:8000/api/v1/analytics/gyms/gym-1/dashboard', {
      headers: { Authorization: 'Bearer old-access' },
    });

    const original401 = new Response(JSON.stringify({ detail: { code: 'INVALID_TOKEN' } }), {
      status: 401,
    });
    const result = await interceptor!(original401, request, {});

    expect(result.status).toBe(401);
    expect(localStorage.getItem('gym_staff_access_token')).toBeNull();
    expect(localStorage.getItem('gym_staff_refresh_token')).toBeNull();
    expect(localStorage.getItem('gym_staff_info')).toBeNull();
  });
});
