import { useState, type FormEvent } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  analyticsConsumerClassHistory,
  consumerAuthDeleteConsumerAccount,
  consumerAuthGetCurrentConsumerProfile,
  consumerAuthUpdateConsumerProfile,
  paymentsConsumerPaymentHistory,
} from '@sl/api-client';
import { useAuth } from '../../hooks/useAuth';
import { getAuthHeaders } from '../../lib/apiAuth';

type SectionType = 'profile' | 'notifications' | 'history' | 'payments' | 'danger';

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function Profile() {
  const { logout, updateProfile } = useAuth();
  const [activeSection, setActiveSection] = useState<SectionType>('profile');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const [notifBookings, setNotifBookings] = useState(true);
  const [notifPromotions, setNotifPromotions] = useState(true);
  const [notifReminders, setNotifReminders] = useState(true);
  const [notifWhatsApp, setNotifWhatsApp] = useState(false);

  const profileQuery = useQuery({
    queryKey: ['consumer-profile'],
    queryFn: async () => {
      const response = await consumerAuthGetCurrentConsumerProfile({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const classHistoryQuery = useQuery({
    queryKey: ['consumer-class-history-profile'],
    queryFn: async () => {
      const response = await analyticsConsumerClassHistory({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data?.items ?? [];
    },
  });

  const paymentsQuery = useQuery({
    queryKey: ['consumer-payments-profile'],
    queryFn: async () => {
      const response = await paymentsConsumerPaymentHistory({
        headers: getAuthHeaders(),
      });
      return response.data?.items ?? [];
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: async (payload: {
      first_name: string;
      last_name: string;
      phone: string | null;
    }) => {
      const response = await consumerAuthUpdateConsumerProfile({
        body: payload,
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setActionError(null);
      if (data) {
        updateProfile({
          id: data.id,
          email: data.email,
          first_name: data.first_name,
          last_name: data.last_name,
          phone: data.phone,
          avatar_url: data.avatar_url,
        });
      }
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2000);
    },
    onError: () => {
      setProfileSaved(false);
      setActionError('Could not save profile changes. Please try again.');
    },
  });

  const deleteAccountMutation = useMutation({
    mutationFn: async () => {
      await consumerAuthDeleteConsumerAccount({
        body: { password: '' },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setActionError(null);
      logout();
    },
    onError: () => {
      setActionError('Could not delete your account. Please try again.');
    },
  });

  const classHistoryItems = classHistoryQuery.data ?? [];
  const paymentItems = paymentsQuery.data ?? [];

  const sections: { key: SectionType; label: string }[] = [
    { key: 'profile', label: 'Edit Profile' },
    { key: 'notifications', label: 'Notifications' },
    { key: 'history', label: 'Class History' },
    { key: 'payments', label: 'Payments' },
    { key: 'danger', label: 'Account' },
  ];

  const handleProfileSave = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const firstName = String(formData.get('firstName') ?? '').trim();
    const lastName = String(formData.get('lastName') ?? '').trim();
    const phone = String(formData.get('phone') ?? '').trim();
    setActionError(null);
    setProfileSaved(false);

    updateProfileMutation.mutate({
      first_name: firstName,
      last_name: lastName,
      phone: phone || null,
    });
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile & Settings</h1>

      {actionError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 mb-4">
          {actionError}
        </div>
      )}

      <div className="flex items-center gap-1 overflow-x-auto pb-2 mb-6 -mx-4 px-4">
        {sections.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveSection(key)}
            className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
              activeSection === key
                ? 'bg-coral-50 text-coral-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {(profileQuery.isLoading || classHistoryQuery.isLoading || paymentsQuery.isLoading) && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600 mb-4">
          Loading profile data...
        </div>
      )}

      {(profileQuery.error || classHistoryQuery.error || paymentsQuery.error) && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 mb-4">
          Could not load all profile data.
        </div>
      )}

      {activeSection === 'profile' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Edit Profile</h2>

          <form className="space-y-4" onSubmit={handleProfileSave}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
                  First name
                </label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  defaultValue={profileQuery.data?.first_name ?? ''}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 sm:text-sm"
                />
              </div>
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
                  Last name
                </label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  defaultValue={profileQuery.data?.last_name ?? ''}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 sm:text-sm"
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
                value={profileQuery.data?.email ?? ''}
                disabled
                className="mt-1 block w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 sm:text-sm"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone number
              </label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  defaultValue={profileQuery.data?.phone ?? ''}
                  placeholder="+27821234567"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 sm:text-sm"
                />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={updateProfileMutation.isPending}
                className="px-6 py-2 text-sm font-medium rounded-lg text-white bg-coral-600 hover:bg-coral-700 transition-colors disabled:opacity-50"
              >
                {updateProfileMutation.isPending
                  ? 'Saving...'
                  : profileSaved
                    ? 'Saved!'
                    : 'Save changes'}
              </button>
            </div>
          </form>
        </div>
      )}

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
            <ToggleRow
              label="WhatsApp notifications"
              description="Receive notifications via WhatsApp instead of email"
              checked={notifWhatsApp}
              onChange={setNotifWhatsApp}
            />
          </div>
        </div>
      )}

      {activeSection === 'history' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Class History</h2>
          {classHistoryItems.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No class history yet.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {classHistoryItems.map((item) => (
                <div key={`${item.session_id}-${item.attended_at}`} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{item.class_name}</p>
                    <p className="text-xs text-gray-500">
                      {item.gym_id} - {formatDate(item.attended_at)}
                    </p>
                  </div>
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full capitalize bg-green-100 text-green-700">
                    attended
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeSection === 'payments' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment History</h2>
          {paymentItems.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No payments yet.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {paymentItems.map((item) => (
                <div key={item.payment_id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{item.description}</p>
                    <p className="text-xs text-gray-500">{formatDate(item.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900 text-sm">
                      R {(item.amount_cents / 100).toFixed(2)}
                    </p>
                    <span
                      className={`text-xs font-medium capitalize ${
                        item.status === 'completed'
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

      {activeSection === 'danger' && (
        <div className="bg-white rounded-xl border border-red-200 p-6">
          <h2 className="text-lg font-semibold text-red-700 mb-2">Delete Account</h2>
          <p className="text-sm text-gray-600 mb-4">
            Permanently delete your account and all associated data.
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
                  onClick={() => deleteAccountMutation.mutate()}
                  disabled={deleteAccountMutation.isPending}
                  className="px-4 py-2 text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {deleteAccountMutation.isPending ? 'Deleting...' : 'Yes, delete my account'}
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
  onChange: (val: boolean) => void;
}) {
  return (
    <label className="flex items-start justify-between gap-4 cursor-pointer">
      <div>
        <p className="text-sm font-medium text-gray-900">{label}</p>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          checked ? 'bg-coral-600' : 'bg-gray-300'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </label>
  );
}

export default Profile;
