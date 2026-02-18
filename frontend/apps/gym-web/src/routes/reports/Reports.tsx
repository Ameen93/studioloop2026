/**
 * Reports page (Story 12.7).
 *
 * Tabbed report views: Revenue, Attendance, Membership,
 * Class Performance, and Staff reports.
 */

import { useState } from 'react';

type ReportTab = 'revenue' | 'attendance' | 'membership' | 'class_performance' | 'staff';

const tabs: { key: ReportTab; label: string }[] = [
  { key: 'revenue', label: 'Revenue' },
  { key: 'attendance', label: 'Attendance' },
  { key: 'membership', label: 'Membership' },
  { key: 'class_performance', label: 'Class Performance' },
  { key: 'staff', label: 'Staff' },
];

function RevenueReport() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500">This Month</p>
          <p className="text-2xl font-bold text-gray-900">R 87,450.00</p>
          <p className="text-sm text-green-600">+12.3% vs last month</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500">Last Month</p>
          <p className="text-2xl font-bold text-gray-900">R 77,890.00</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500">Year to Date</p>
          <p className="text-2xl font-bold text-gray-900">R 165,340.00</p>
        </div>
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {[
              { source: 'Membership Subscriptions', amount: 'R 62,300.00', count: 104 },
              { source: 'Class Packs', amount: 'R 12,500.00', count: 25 },
              { source: 'Drop-in Classes', amount: 'R 8,400.00', count: 56 },
              { source: 'Merchandise', amount: 'R 4,250.00', count: 34 },
            ].map((row, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{row.source}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.amount}</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AttendanceReport() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Today', value: '47' },
          { label: 'This Week', value: '312' },
          { label: 'This Month', value: '1,247' },
          { label: 'Avg Daily', value: '42' },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time Slot</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Check-ins</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Peak Day</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {[
              { slot: '06:00 - 08:00', avg: 18, peak: 'Monday' },
              { slot: '08:00 - 10:00', avg: 12, peak: 'Wednesday' },
              { slot: '12:00 - 14:00', avg: 8, peak: 'Tuesday' },
              { slot: '16:00 - 18:00', avg: 15, peak: 'Thursday' },
              { slot: '18:00 - 20:00', avg: 10, peak: 'Monday' },
            ].map((row, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{row.slot}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.avg}</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">{row.peak}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MembershipReport() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Active Members', value: '342' },
          { label: 'New This Month', value: '28' },
          { label: 'Churned', value: '8' },
          { label: 'Retention Rate', value: '94.2%' },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Active</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">MRR</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {[
              { plan: 'Premium Monthly', active: 145, mrr: 'R 86,855.00' },
              { plan: 'Basic Monthly', active: 120, mrr: 'R 47,880.00' },
              { plan: 'Premium Annual', active: 52, mrr: 'R 23,400.00' },
              { plan: 'Class Pack (10)', active: 25, mrr: 'R 6,250.00' },
            ].map((row, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{row.plan}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.active}</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">{row.mrr}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ClassPerformanceReport() {
  return (
    <div className="space-y-6">
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Class</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Attendance</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Fill Rate</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Revenue</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {[
              { name: 'Morning HIIT', avg: 17, fill: '85%', revenue: 'R 12,400.00' },
              { name: 'Spin Class', avg: 21, fill: '84%', revenue: 'R 9,800.00' },
              { name: 'Yoga Flow', avg: 13, fill: '87%', revenue: 'R 7,200.00' },
              { name: 'Boxing Fitness', avg: 16, fill: '80%', revenue: 'R 6,400.00' },
              { name: 'CrossFit', avg: 14, fill: '70%', revenue: 'R 5,600.00' },
              { name: 'Pilates', avg: 9, fill: '75%', revenue: 'R 4,100.00' },
            ].map((row, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{row.name}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.avg}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.fill}</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">{row.revenue}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StaffReport() {
  return (
    <div className="space-y-6">
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Staff Member</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Classes Taught</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Rating</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {[
              { name: 'Coach Sipho', role: 'Instructor', classes: 24, rating: '4.8' },
              { name: 'Lerato M.', role: 'Instructor', classes: 20, rating: '4.9' },
              { name: 'Coach David', role: 'Instructor', classes: 18, rating: '4.7' },
              { name: 'Zanele K.', role: 'Instructor', classes: 12, rating: '4.8' },
            ].map((row, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{row.name}</td>
                <td className="px-6 py-3 text-sm text-gray-500">{row.role}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.classes}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.rating}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function Reports() {
  const [activeTab, setActiveTab] = useState<ReportTab>('revenue');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <button className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors">
          Export CSV
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {activeTab === 'revenue' && <RevenueReport />}
        {activeTab === 'attendance' && <AttendanceReport />}
        {activeTab === 'membership' && <MembershipReport />}
        {activeTab === 'class_performance' && <ClassPerformanceReport />}
        {activeTab === 'staff' && <StaffReport />}
      </div>
    </div>
  );
}
