/**
 * Member detail page (Story 12.4).
 *
 * Shows detailed information about a single member including
 * membership, attendance history, and payment history.
 */

import { useParams, Link } from 'react-router';

export function MemberDetail() {
  const { memberId } = useParams<{ memberId: string }>();

  // Mock data - will be replaced with TanStack Query call
  const member = {
    id: memberId,
    full_name: 'Thabo Mokoena',
    email: 'thabo@email.com',
    phone: '+27 82 123 4567',
    date_of_birth: '15 Mar 1992',
    membership_plan: 'Premium Monthly',
    membership_status: 'active',
    membership_start: '15 Jan 2026',
    membership_end: '14 Feb 2026',
    total_check_ins: 24,
    last_check_in: '18 Feb 2026, 07:15',
    outstanding_balance: 'R 0.00',
  };

  const recentAttendance = [
    { date: '18 Feb 2026', time: '07:15', class_name: 'Morning HIIT' },
    { date: '17 Feb 2026', time: '06:30', class_name: 'Open Gym' },
    { date: '16 Feb 2026', time: '08:00', class_name: 'Yoga Flow' },
    { date: '14 Feb 2026', time: '07:00', class_name: 'Morning HIIT' },
    { date: '13 Feb 2026', time: '17:30', class_name: 'Spin Class' },
  ];

  const recentPayments = [
    { date: '15 Feb 2026', amount: 'R 599.00', method: 'Ozow', status: 'paid' },
    { date: '15 Jan 2026', amount: 'R 599.00', method: 'Ozow', status: 'paid' },
    { date: '15 Dec 2025', amount: 'R 599.00', method: 'PayFast', status: 'paid' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/members" className="text-sm text-blue-600 hover:text-blue-800">
          &larr; Back to Members
        </Link>
      </div>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{member.full_name}</h1>
            <p className="text-sm text-gray-500 mt-1">{member.email} | {member.phone}</p>
            <p className="text-sm text-gray-500">DOB: {member.date_of_birth}</p>
          </div>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
              Edit
            </button>
            <button className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700">
              Check In
            </button>
          </div>
        </div>
      </div>

      {/* Membership info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Membership</h2>
          <p className="text-lg font-semibold text-gray-900">{member.membership_plan}</p>
          <span className="inline-flex items-center mt-2 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
            {member.membership_status}
          </span>
          <div className="mt-3 text-sm text-gray-500">
            <p>Start: {member.membership_start}</p>
            <p>End: {member.membership_end}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Attendance</h2>
          <p className="text-3xl font-bold text-gray-900">{member.total_check_ins}</p>
          <p className="text-sm text-gray-500 mt-1">Total check-ins</p>
          <p className="text-sm text-gray-500 mt-2">Last: {member.last_check_in}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Billing</h2>
          <p className="text-3xl font-bold text-gray-900">{member.outstanding_balance}</p>
          <p className="text-sm text-gray-500 mt-1">Outstanding balance</p>
        </div>
      </div>

      {/* Attendance history */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Attendance</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Class</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {recentAttendance.map((a, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{a.date}</td>
                <td className="px-6 py-3 text-sm text-gray-500">{a.time}</td>
                <td className="px-6 py-3 text-sm text-gray-700">{a.class_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Payment history */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Payment History</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {recentPayments.map((p, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{p.date}</td>
                <td className="px-6 py-3 text-sm text-gray-700">{p.amount}</td>
                <td className="px-6 py-3 text-sm text-gray-500">{p.method}</td>
                <td className="px-6 py-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize">
                    {p.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
