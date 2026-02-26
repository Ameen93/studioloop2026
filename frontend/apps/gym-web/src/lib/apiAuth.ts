const ACCESS_TOKEN_KEY = 'gym_staff_access_token';
const STAFF_INFO_KEY = 'gym_staff_info';

type StoredStaffInfo = {
  id?: string;
  role: string;
  gym_id: string;
};

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

export function getStoredStaffInfo(): StoredStaffInfo | null {
  const raw = localStorage.getItem(STAFF_INFO_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as Partial<StoredStaffInfo>;
    if (typeof parsed.role === 'string' && typeof parsed.gym_id === 'string') {
      return {
        role: parsed.role,
        gym_id: parsed.gym_id,
        ...(typeof parsed.id === 'string' ? { id: parsed.id } : {}),
      };
    }
  } catch {
    return null;
  }

  return null;
}
