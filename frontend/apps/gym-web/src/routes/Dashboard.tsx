/**
 * Dashboard page (Story 12.3).
 *
 * Shows today's summary: revenue, check-ins, bookings, action items,
 * and quick metrics for the gym.
 */

import { useState } from 'react';

interface ActionItem {
  id: string;
  type: 'warning' | 'info' | 'urgent';
  message: string;
  time: string;
}

const mockActionItems: ActionItem[] = [
  { id: '1', type: 'urgent', message: '3 memberships expiring today', time: '09:00' },
  { id: '2', type: 'warning', message: '2 failed payment retries scheduled', time: '10:30' },
  { id: '3', type: 'info', message: 'New member registration pending approval', time: '11:15' },
  { id: '4', type: 'info', message: 'Yoga class at 14:00 is 90% full', time: '12:00' },
];

interface SummaryCard {
  label: string;
  value: string;
  change: string;
  positive: boolean;
}

const mockSummary: SummaryCard[] = [
  { label: "Today's Revenue", value: 'R 12,450.00', change: '+8.2%', positive: true },
  { label: 'Check-ins Today', value: '47', change: '+12%', positive: true },
  { label: 'Active Bookings', value: '28', change: '-3%', positive: false },
  { label: 'Active Members', value: '342', change: '+2.1%', positive: true },
];

const typeStyles: Record<string, string> = {
  urgent: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
};

export function Dashboard() {
  const [_filter] = useState<string>('today');

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">
          {new Date().toLocaleDateString('en-ZA', {
            weekday: 'long',
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          })}
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {mockSummary.map((card) => (
          <div
            key={card.label}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <p className="text-sm font-medium text-gray-500">{card.label}</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">{card.value}</p>
            <p
              className={`mt-1 text-sm font-medium ${
                card.positive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {card.change} vs last week
            </p>
          </div>
        ))}
      </div>

      {/* Action items */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Action Items</h2>
        </div>
        <ul className="divide-y divide-gray-200">
          {mockActionItems.map((item) => (
            <li key={item.id} className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeStyles[item.type]}`}
                >
                  {item.type}
                </span>
                <span className="text-sm text-gray-900">{item.message}</span>
              </div>
              <span className="text-xs text-gray-500">{item.time}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Quick metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Popular Classes Today</h3>
          <div className="space-y-3">
            {[
              { name: 'Morning HIIT', time: '06:00', booked: 18, capacity: 20 },
              { name: 'Yoga Flow', time: '08:00', booked: 12, capacity: 15 },
              { name: 'Spin Class', time: '12:00', booked: 22, capacity: 25 },
              { name: 'Pilates', time: '17:00', booked: 10, capacity: 12 },
            ].map((cls) => (
              <div key={cls.name} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{cls.name}</p>
                  <p className="text-xs text-gray-500">{cls.time}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${(cls.booked / cls.capacity) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">
                    {cls.booked}/{cls.capacity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {[
              { action: 'Check-in', member: 'Thabo M.', time: '2 min ago' },
              { action: 'Booking', member: 'Sarah K.', time: '5 min ago' },
              { action: 'Payment', member: 'John D.', time: '12 min ago' },
              { action: 'New Member', member: 'Naledi P.', time: '25 min ago' },
              { action: 'Check-in', member: 'David L.', time: '30 min ago' },
            ].map((activity, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                    {activity.action}
                  </span>
                  <span className="text-sm text-gray-900">{activity.member}</span>
                </div>
                <span className="text-xs text-gray-500">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
