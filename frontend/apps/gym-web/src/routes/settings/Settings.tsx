/**
 * Settings page (Story 12.9).
 *
 * Tabbed settings: Profile, Hours, Policies, Plans,
 * Spaces, Marketplace, Webhooks.
 */

import { useState } from 'react';

type SettingsTab = 'profile' | 'hours' | 'policies' | 'plans' | 'spaces' | 'marketplace' | 'webhooks';

const tabs: { key: SettingsTab; label: string }[] = [
  { key: 'profile', label: 'Profile' },
  { key: 'hours', label: 'Hours' },
  { key: 'policies', label: 'Policies' },
  { key: 'plans', label: 'Plans' },
  { key: 'spaces', label: 'Spaces' },
  { key: 'marketplace', label: 'Marketplace' },
  { key: 'webhooks', label: 'Webhooks' },
];

function ProfileSettings() {
  return (
    <form className="space-y-4 max-w-lg">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Gym Name</label>
        <input type="text" defaultValue="FitZone Sandton" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input type="email" defaultValue="info@fitzone.co.za" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
        <input type="tel" defaultValue="+27 11 234 5678" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
        <textarea defaultValue="123 Rivonia Road, Sandton, 2196" rows={2} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea defaultValue="Premium fitness studio in the heart of Sandton." rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
      </div>
      <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Save Changes
      </button>
    </form>
  );
}

function HoursSettings() {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return (
    <div className="space-y-3 max-w-lg">
      {days.map((day) => (
        <div key={day} className="flex items-center gap-4">
          <span className="w-28 text-sm font-medium text-gray-700">{day}</span>
          <input type="time" defaultValue={day === 'Sunday' ? '08:00' : '05:00'} className="px-2 py-1.5 border border-gray-300 rounded-md text-sm" />
          <span className="text-gray-400">to</span>
          <input type="time" defaultValue={day === 'Sunday' ? '14:00' : '21:00'} className="px-2 py-1.5 border border-gray-300 rounded-md text-sm" />
        </div>
      ))}
      <button className="mt-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Save Hours
      </button>
    </div>
  );
}

function PoliciesSettings() {
  return (
    <div className="space-y-4 max-w-lg">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Cancellation Window (hours)</label>
        <input type="number" defaultValue={4} className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm" />
        <p className="text-xs text-gray-500 mt-1">Members must cancel this many hours before class starts.</p>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Late Cancel Fee (ZAR)</label>
        <input type="number" defaultValue={50} className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">No-Show Fee (ZAR)</label>
        <input type="number" defaultValue={75} className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Freeze Policy</label>
        <select className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm">
          <option>Allow 1 freeze per 6 months (max 30 days)</option>
          <option>Allow 2 freezes per year (max 14 days each)</option>
          <option>No freezes allowed</option>
        </select>
      </div>
      <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Save Policies
      </button>
    </div>
  );
}

function PlansSettings() {
  const plans = [
    { name: 'Premium Monthly', price: 'R 599.00', members: 145, status: 'active' },
    { name: 'Basic Monthly', price: 'R 399.00', members: 120, status: 'active' },
    { name: 'Premium Annual', price: 'R 5,400.00', members: 52, status: 'active' },
    { name: 'Class Pack (10)', price: 'R 250.00', members: 25, status: 'active' },
  ];
  return (
    <div className="space-y-4">
      <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Create Plan
      </button>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Members</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {plans.map((plan, i) => (
              <tr key={i}>
                <td className="px-6 py-3 text-sm text-gray-900">{plan.name}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{plan.price}</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">{plan.members}</td>
                <td className="px-6 py-3 text-sm text-right">
                  <button className="text-blue-600 hover:text-blue-800 mr-3">Edit</button>
                  <button className="text-red-600 hover:text-red-800">Archive</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SpacesSettings() {
  const spaces = [
    { name: 'Studio A', capacity: 20, type: 'Group Fitness' },
    { name: 'Studio B', capacity: 15, type: 'Yoga / Pilates' },
    { name: 'Spin Room', capacity: 25, type: 'Cycling' },
    { name: 'Main Floor', capacity: 30, type: 'CrossFit / Open Gym' },
  ];
  return (
    <div className="space-y-4">
      <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Add Space
      </button>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {spaces.map((space) => (
          <div key={space.name} className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900">{space.name}</h3>
            <p className="text-sm text-gray-500">Capacity: {space.capacity}</p>
            <p className="text-sm text-gray-500">Type: {space.type}</p>
            <button className="mt-2 text-sm text-blue-600 hover:text-blue-800">Edit</button>
          </div>
        ))}
      </div>
    </div>
  );
}

function MarketplaceSettings() {
  return (
    <div className="space-y-4 max-w-lg">
      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
        <div>
          <p className="font-medium text-gray-900">Marketplace Listing</p>
          <p className="text-sm text-gray-500">Show your gym on the StudioLoop marketplace</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input type="checkbox" defaultChecked className="sr-only peer" />
          <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
        <div>
          <p className="font-medium text-gray-900">Accept Marketplace Bookings</p>
          <p className="text-sm text-gray-500">Allow non-members to book classes via the marketplace</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input type="checkbox" defaultChecked className="sr-only peer" />
          <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Drop-in Class Price (ZAR)</label>
        <input type="number" defaultValue={150} className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm" />
      </div>
      <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Save Marketplace Settings
      </button>
    </div>
  );
}

function WebhooksSettings() {
  return (
    <div className="space-y-4 max-w-lg">
      <p className="text-sm text-gray-500">
        Configure webhook endpoints to receive real-time notifications about events in your gym.
      </p>
      <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
        Add Webhook
      </button>
      <div className="border border-gray-200 rounded-lg p-6 text-center text-sm text-gray-500">
        No webhooks configured. Add a webhook endpoint to get started.
      </div>
    </div>
  );
}

export function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

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
        {activeTab === 'profile' && <ProfileSettings />}
        {activeTab === 'hours' && <HoursSettings />}
        {activeTab === 'policies' && <PoliciesSettings />}
        {activeTab === 'plans' && <PlansSettings />}
        {activeTab === 'spaces' && <SpacesSettings />}
        {activeTab === 'marketplace' && <MarketplaceSettings />}
        {activeTab === 'webhooks' && <WebhooksSettings />}
      </div>
    </div>
  );
}
