/**
 * Profile & Settings screen (Story 13.8).
 *
 * Edit profile, notification preferences, class history,
 * payment history, and delete account.
 */

import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

type SectionType = 'profile' | 'notifications' | 'history' | 'payments' | 'danger';

interface ClassHistoryItem {
  id: string;
  class_name: string;
  gym_name: string;
  date: string;
  status: 'attended' | 'no_show' | 'cancelled';
}

interface PaymentHistoryItem {
  id: string;
  description: string;
  amount_zar: number;
  date: string;
  status: 'paid' | 'pending' | 'refunded';
}

// Placeholder data
const CLASS_HISTORY: ClassHistoryItem[] = [
  { id: '1', class_name: 'Morning Yoga Flow', gym_name: 'ZenFit Studio', date: '2026-02-15', status: 'attended' },
  { id: '2', class_name: 'HIIT Blast', gym_name: 'PowerHouse Gym', date: '2026-02-13', status: 'attended' },
  { id: '3', class_name: 'Pilates Mat', gym_name: 'Body Balance', date: '2026-02-10', status: 'no_show' },
  { id: '4', class_name: 'Spin & Burn', gym_name: 'CycleFit', date: '2026-02-08', status: 'cancelled' },
];

const PAYMENT_HISTORY: PaymentHistoryItem[] = [
  { id: '1', description: 'HIIT Blast - Pay per class', amount_zar: 120, date: '2026-02-13', status: 'paid' },
  { id: '2', description: 'ZenFit Studio - Monthly', amount_zar: 799, date: '2026-02-01', status: 'paid' },
  { id: '3', description: 'StudioLoop Explorer - Monthly', amount_zar: 499, date: '2026-02-01', status: 'paid' },
];

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function Profile() {
  const { consumer, logout } = useAuth();
  const [activeSection, setActiveSection] = useState<SectionType>('profile');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Profile form state
  const [firstName, setFirstName] = useState(consumer?.first_name ?? '');
  const [lastName, setLastName] = useState(consumer?.last_name ?? '');
  const [phone, setPhone] = useState(consumer?.phone ?? '');
  const [profileSaved, setProfileSaved] = useState(false);

  // Notification preferences
  const [notifBookings, setNotifBookings] = useState(true);
  const [notifPromotions, setNotifPromotions] = useState(true);
  const [notifReminders, setNotifReminders] = useState(true);
  const [notifWhatsApp, setNotifWhatsApp] = useState(false);

  const handleSaveProfile = async () => {
    // TODO: Wire up to consumer profile update API
    await new Promise((resolve) => setTimeout(resolve, 500));
    setProfileSaved(true);
    setTimeout(() => setProfileSaved(false), 2000);
  };

  const handleDeleteAccount = async () => {
    // TODO: Wire up to consumer account deletion API (POPIA compliance)
    await new Promise((resolve) => setTimeout(resolve, 500));
    logout();
  };

  const sections: { key: SectionType; label: string }[] = [
    { key: 'profile', label: 'Edit Profile' },
    { key: 'notifications', label: 'Notifications' },
    { key: 'history', label: 'Class History' },
    { key: 'payments', label: 'Payments' },
    { key: 'danger', label: 'Account' },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile & Settings</h1>

      {/* Section tabs */}
      <div className="flex items-center gap-1 overflow-x-auto pb-2 mb-6 -mx-4 px-4">
        {sections.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveSection(key)}
            className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
              activeSection === key
                ? 'bg-indigo-50 text-indigo-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Edit Profile */}
      {activeSection === 'profile' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Edit Profile</h2>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
                  First name
                </label>
                <input
                  id="firstName"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
                  Last name
                </label>
                <input
                  id="lastName"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                type="email"
                value={consumer?.email ?? ''}
                disabled
                className="mt-1 block w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 sm:text-sm"
              />
              <p className="mt-1 text-xs text-gray-400">Email cannot be changed</p>
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone number
              </label>
              <input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+27821234567"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>

            <div className="pt-2">
              <button
                onClick={handleSaveProfile}
                className="px-6 py-2 text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
              >
                {profileSaved ? 'Saved!' : 'Save changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications */}
      {activeSection === 'notifications' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h2>

          <div className="space-y-4">
            <ToggleRow
              label="Booking confirmations & changes"
              description="Get notified when your booking is confirmed, changed, or cancelled"
              checked={notifBookings}
              onChange={setNotifBookings}
            />
            <ToggleRow
              label="Class reminders"
              description="Receive a reminder before your upcoming classes"
              checked={notifReminders}
              onChange={setNotifReminders}
            />
            <ToggleRow
              label="Promotions & offers"
              description="Special deals and discounts from studios"
              checked={notifPromotions}
              onChange={setNotifPromotions}
            />

            <div className="border-t border-gray-100 pt-4">
              <ToggleRow
                label="WhatsApp notifications"
                description="Receive notifications via WhatsApp instead of email"
                checked={notifWhatsApp}
                onChange={setNotifWhatsApp}
              />
            </div>
          </div>
        </div>
      )}

      {/* Class History */}
      {activeSection === 'history' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Class History</h2>

          {CLASS_HISTORY.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No class history yet.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {CLASS_HISTORY.map((item) => (
                <div key={item.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{item.class_name}</p>
                    <p className="text-xs text-gray-500">{item.gym_name} - {formatDate(item.date)}</p>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${
                      item.status === 'attended'
                        ? 'bg-green-100 text-green-700'
                        : item.status === 'no_show'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {item.status.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Payment History */}
      {activeSection === 'payments' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment History</h2>

          {PAYMENT_HISTORY.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No payments yet.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {PAYMENT_HISTORY.map((item) => (
                <div key={item.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{item.description}</p>
                    <p className="text-xs text-gray-500">{formatDate(item.date)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900 text-sm">R {item.amount_zar.toFixed(2)}</p>
                    <span
                      className={`text-xs font-medium capitalize ${
                        item.status === 'paid'
                          ? 'text-green-600'
                          : item.status === 'refunded'
                            ? 'text-amber-600'
                            : 'text-gray-500'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Danger Zone */}
      {activeSection === 'danger' && (
        <div className="bg-white rounded-xl border border-red-200 p-6">
          <h2 className="text-lg font-semibold text-red-700 mb-2">Delete Account</h2>
          <p className="text-sm text-gray-600 mb-4">
            Permanently delete your account and all associated data. This action cannot be undone.
            As per POPIA regulations, all your personal data will be erased.
          </p>

          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-4 py-2 text-sm font-medium rounded-lg text-red-700 bg-red-50 hover:bg-red-100 transition-colors"
            >
              Delete my account
            </button>
          ) : (
            <div className="bg-red-50 rounded-lg p-4">
              <p className="text-sm font-medium text-red-800 mb-3">
                Are you sure? This will permanently delete your account.
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleDeleteAccount}
                  className="px-4 py-2 text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 transition-colors"
                >
                  Yes, delete my account
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-4 py-2 text-sm font-medium rounded-lg text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-900">{label}</p>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          checked ? 'bg-indigo-600' : 'bg-gray-200'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}

export default Profile;
