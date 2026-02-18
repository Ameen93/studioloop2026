/**
 * Staff management page (Story 12.8).
 *
 * Staff list with role management. Allows owners/managers to
 * view, add, and edit staff members and their roles.
 */

import { useState } from 'react';

interface StaffMember {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role: 'owner' | 'manager' | 'front_desk' | 'instructor';
  status: 'active' | 'inactive';
  joined_at: string;
}

const mockStaff: StaffMember[] = [
  { id: '1', full_name: 'Mpho Naidoo', email: 'mpho@gym.co.za', phone: '+27 82 111 2222', role: 'owner', status: 'active', joined_at: '01 Jan 2025' },
  { id: '2', full_name: 'Anele van der Berg', email: 'anele@gym.co.za', phone: '+27 83 222 3333', role: 'manager', status: 'active', joined_at: '15 Mar 2025' },
  { id: '3', full_name: 'Coach Sipho', email: 'sipho@gym.co.za', phone: '+27 84 333 4444', role: 'instructor', status: 'active', joined_at: '01 Apr 2025' },
  { id: '4', full_name: 'Lerato Mosia', email: 'lerato@gym.co.za', phone: '+27 72 444 5555', role: 'instructor', status: 'active', joined_at: '15 May 2025' },
  { id: '5', full_name: 'David Coetzee', email: 'david@gym.co.za', phone: '+27 81 555 6666', role: 'instructor', status: 'active', joined_at: '01 Jun 2025' },
  { id: '6', full_name: 'Zanele Khumalo', email: 'zanele@gym.co.za', phone: '+27 73 666 7777', role: 'instructor', status: 'active', joined_at: '15 Jul 2025' },
  { id: '7', full_name: 'Themba Dlamini', email: 'themba@gym.co.za', phone: '+27 82 777 8888', role: 'front_desk', status: 'active', joined_at: '01 Sep 2025' },
  { id: '8', full_name: 'Fiona Adams', email: 'fiona@gym.co.za', phone: '+27 83 888 9999', role: 'front_desk', status: 'inactive', joined_at: '01 Oct 2025' },
];

const roleStyles: Record<string, string> = {
  owner: 'bg-purple-100 text-purple-800',
  manager: 'bg-blue-100 text-blue-800',
  front_desk: 'bg-gray-100 text-gray-800',
  instructor: 'bg-green-100 text-green-800',
};

const roleLabels: Record<string, string> = {
  owner: 'Owner',
  manager: 'Manager',
  front_desk: 'Front Desk',
  instructor: 'Instructor',
};

export function StaffManagement() {
  const [showAddModal, setShowAddModal] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Staff Management</h1>
        <button
          onClick={() => setShowAddModal(!showAddModal)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          Invite Staff
        </button>
      </div>

      {/* Staff summary */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Staff', value: mockStaff.length },
          { label: 'Instructors', value: mockStaff.filter((s) => s.role === 'instructor').length },
          { label: 'Front Desk', value: mockStaff.filter((s) => s.role === 'front_desk').length },
          { label: 'Active', value: mockStaff.filter((s) => s.status === 'active').length },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Invite form (toggle) */}
      {showAddModal && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Invite New Staff Member</h2>
          <form className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Jane Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="jane@gym.co.za"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                type="tel"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="+27 82 000 0000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
                <option value="instructor">Instructor</option>
                <option value="front_desk">Front Desk</option>
                <option value="manager">Manager</option>
              </select>
            </div>
            <div className="sm:col-span-2 flex gap-3">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
              >
                Send Invite
              </button>
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Staff table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {mockStaff.map((staff) => (
              <tr key={staff.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {staff.full_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <p className="text-sm text-gray-900">{staff.email}</p>
                  <p className="text-xs text-gray-500">{staff.phone}</p>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roleStyles[staff.role]}`}>
                    {roleLabels[staff.role]}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                    staff.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {staff.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{staff.joined_at}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <button className="text-sm text-blue-600 hover:text-blue-800 mr-3">Edit</button>
                  {staff.role !== 'owner' && (
                    <button className="text-sm text-red-600 hover:text-red-800">Deactivate</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
