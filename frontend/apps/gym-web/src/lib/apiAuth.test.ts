import { beforeEach, describe, expect, it } from 'vitest';
import { getStoredStaffInfo } from './apiAuth';

describe('getStoredStaffInfo', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns role and gym_id when id is not present', () => {
    localStorage.setItem(
      'gym_staff_info',
      JSON.stringify({
        role: 'front_desk',
        gym_id: 'gym-123',
      }),
    );

    expect(getStoredStaffInfo()).toEqual({
      role: 'front_desk',
      gym_id: 'gym-123',
    });
  });

  it('returns null when required fields are missing', () => {
    localStorage.setItem(
      'gym_staff_info',
      JSON.stringify({
        id: 'staff-1',
      }),
    );

    expect(getStoredStaffInfo()).toBeNull();
  });
});
