/**
 * Member list page (Story 12.4).
 *
 * Displays a searchable, filterable table of gym members.
 * Links to individual member detail pages.
 */

import { useState } from 'react';
import { Link } from 'react-router';

interface Member {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  membership_plan: string;
  status: 'active' | 'expired' | 'frozen';
  joined_at: string;
}

const mockMembers: Member[] = [
  { id: '1', full_name: 'Thabo Mokoena', email: 'thabo@email.com', phone: '+27 82 123 4567', membership_plan: 'Premium Monthly', status: 'active', joined_at: '15 Jan 2026' },
  { id: '2', full_name: 'Sarah Khumalo', email: 'sarah@email.com', phone: '+27 83 234 5678', membership_plan: 'Basic Monthly', status: 'active', joined_at: '03 Feb 2026' },
  { id: '3', full_name: 'John Daniels', email: 'john@email.com', phone: '+27 84 345 6789', membership_plan: 'Premium Annual', status: 'active', joined_at: '20 Nov 2025' },
  { id: '4', full_name: 'Naledi Phiri', email: 'naledi@email.com', phone: '+27 72 456 7890', membership_plan: 'Basic Monthly', status: 'expired', joined_at: '10 Dec 2025' },
  { id: '5', full_name: 'David Louw', email: 'david@email.com', phone: '+27 81 567 8901', membership_plan: 'Premium Monthly', status: 'frozen', joined_at: '05 Jan 2026' },
  { id: '6', full_name: 'Amahle Nkosi', email: 'amahle@email.com', phone: '+27 73 678 9012', membership_plan: 'Class Pack (10)', status: 'active', joined_at: '01 Feb 2026' },
];

const statusStyles: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  expired: 'bg-red-100 text-red-800',
  frozen: 'bg-blue-100 text-blue-800',
};

export function MemberList() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filtered = mockMembers.filter((m) => {
    const matchesSearch =
      !search ||
      m.full_name.toLowerCase().includes(search.toLowerCase()) ||
      m.email.toLowerCase().includes(search.toLowerCase()) ||
      m.phone.includes(search);
    const matchesStatus = statusFilter === 'all' || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Members</h1>
        <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors">
          Add Member
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search by name, email, or phone..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 max-w-md px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="frozen">Frozen</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filtered.map((member) => (
              <tr key={member.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link to={`/members/${member.id}`} className="text-sm font-medium text-blue-600 hover:text-blue-800">
                    {member.full_name}
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <p className="text-sm text-gray-900">{member.email}</p>
                  <p className="text-xs text-gray-500">{member.phone}</p>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{member.membership_plan}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusStyles[member.status]}`}>
                    {member.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{member.joined_at}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-sm text-gray-500">
                  No members found matching your criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <p className="text-sm text-gray-500">{filtered.length} member(s) found</p>
    </div>
  );
}
