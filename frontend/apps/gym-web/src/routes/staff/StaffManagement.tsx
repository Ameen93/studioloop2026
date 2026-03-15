import { useMemo, useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  staffMembershipsAddStaffMember,
  staffMembershipsDeactivateStaffMember,
  staffMembershipsListStaff,
  staffMembershipsUpdateStaffRole,
  type StaffRole,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

const roleStyles: Record<StaffRole, string> = {
  owner: 'bg-purple-100 text-purple-800',
  manager: 'bg-gold-100 text-gold-800',
  front_desk: 'bg-gray-100 text-gray-800',
  instructor: 'bg-green-100 text-green-800',
};

const roleLabels: Record<StaffRole, string> = {
  owner: 'Owner',
  manager: 'Manager',
  front_desk: 'Front Desk',
  instructor: 'Instructor',
};

export function StaffManagement() {
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const staffQuery = useQuery({
    queryKey: ['gym-staff-list'],
    queryFn: async () => {
      const response = await staffMembershipsListStaff({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const refreshStaff = () => {
    void queryClient.invalidateQueries({ queryKey: ['gym-staff-list'] });
  };

  const addStaffMutation = useMutation({
    mutationFn: async (payload: {
      email: string;
      first_name: string;
      last_name: string;
      phone: string | null;
      role: StaffRole;
    }) => {
      await staffMembershipsAddStaffMember({
        body: payload,
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setActionError(null);
      setShowAddForm(false);
      refreshStaff();
    },
    onError: () => {
      setActionError('Could not invite staff member.');
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: async ({ staffId, role }: { staffId: string; role: StaffRole }) => {
      await staffMembershipsUpdateStaffRole({
        path: { staff_id: staffId },
        body: { role },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setActionError(null);
      refreshStaff();
    },
    onError: () => {
      setActionError('Could not update staff role.');
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: async (staffId: string) => {
      await staffMembershipsDeactivateStaffMember({
        path: { staff_id: staffId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setActionError(null);
      refreshStaff();
    },
    onError: () => {
      setActionError('Could not deactivate staff member.');
    },
  });

  const stats = useMemo(() => {
    const rows = staffQuery.data ?? [];
    return {
      total: rows.length,
      instructors: rows.filter((s) => s.role === 'instructor').length,
      frontDesk: rows.filter((s) => s.role === 'front_desk').length,
      active: rows.filter((s) => s.is_active).length,
    };
  }, [staffQuery.data]);

  const handleInviteStaff = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const fullName = String(formData.get('fullName') ?? '').trim();
    const email = String(formData.get('email') ?? '').trim();
    const phone = String(formData.get('phone') ?? '').trim();
    const role = String(formData.get('role') ?? 'instructor') as StaffRole;

    const parts = fullName.split(/\s+/).filter(Boolean);
    const firstName = parts[0] ?? '';
    const lastName = parts.slice(1).join(' ') || 'Staff';
    if (!email || !firstName) {
      setActionError('Please provide full name and email.');
      return;
    }

    addStaffMutation.mutate({
      email,
      first_name: firstName,
      last_name: lastName,
      phone: phone || null,
      role,
    });
  };

  const staffRows = staffQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Staff Management</h1>
        <button
          onClick={() => setShowAddForm((v) => !v)}
          className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 transition-colors"
        >
          {showAddForm ? 'Close' : 'Invite Staff'}
        </button>
      </div>

      {actionError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {actionError}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Staff', value: stats.total },
          { label: 'Instructors', value: stats.instructors },
          { label: 'Front Desk', value: stats.frontDesk },
          { label: 'Active', value: stats.active },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      {showAddForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Invite New Staff Member</h2>
          <form className="grid grid-cols-1 sm:grid-cols-2 gap-4" onSubmit={handleInviteStaff}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                name="fullName"
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
                placeholder="Jane Doe"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                name="email"
                type="email"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
                placeholder="jane@gym.co.za"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                name="phone"
                type="tel"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
                placeholder="+27 82 000 0000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <select
                name="role"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
              >
                <option value="instructor">Instructor</option>
                <option value="front_desk">Front Desk</option>
                <option value="manager">Manager</option>
              </select>
            </div>
            <div className="sm:col-span-2 flex gap-3">
              <button
                type="submit"
                disabled={addStaffMutation.isPending}
                className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 transition-colors disabled:opacity-50"
              >
                {addStaffMutation.isPending ? 'Sending...' : 'Send Invite'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {staffQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading staff...
        </div>
      )}

      {staffQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load staff members.
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {staffRows.map((staff) => (
              <tr key={staff.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {staff.first_name} {staff.last_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <p className="text-sm text-gray-900">{staff.email}</p>
                  <p className="text-xs text-gray-500">{staff.phone ?? '-'}</p>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roleStyles[staff.role]}`}
                  >
                    {roleLabels[staff.role]}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                      staff.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {staff.is_active ? 'active' : 'inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  {staff.role !== 'owner' && (
                    <>
                      <select
                        defaultValue={staff.role}
                        onChange={(e) =>
                          updateRoleMutation.mutate({
                            staffId: staff.id,
                            role: e.target.value as StaffRole,
                          })
                        }
                        className="mr-3 px-2 py-1 text-xs border border-gray-300 rounded"
                      >
                        <option value="manager">Manager</option>
                        <option value="front_desk">Front Desk</option>
                        <option value="instructor">Instructor</option>
                      </select>
                      {staff.is_active && (
                        <button
                          onClick={() => deactivateMutation.mutate(staff.id)}
                          className="text-sm text-red-600 hover:text-red-800"
                        >
                          Deactivate
                        </button>
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))}
            {staffRows.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-sm text-gray-500">
                  No staff found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
