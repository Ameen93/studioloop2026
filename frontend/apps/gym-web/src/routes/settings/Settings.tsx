/**
 * Settings page (Story 12.9).
 *
 * Tabbed settings: Profile, Hours, Policies, Plans,
 * Spaces, Marketplace, Webhooks.
 *
 * All tabs except Plans and Webhooks are wired to real API endpoints.
 */

import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  gymsGetMyGymProfile,
  gymsUpdateMyGymProfile,
  gymsGetMyGymOperatingHours,
  gymsUpdateMyGymOperatingHours,
  gymsGetMyGymCancellationPolicy,
  gymsUpdateMyGymCancellationPolicy,
  gymsListMySpaces,
  gymsCreateMySpace,
  gymsDeactivateMySpace,
  gymsGetMyMarketplaceToggle,
  gymsUpdateMyMarketplaceToggle,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type SettingsTab = 'profile' | 'hours' | 'policies' | 'plans' | 'spaces' | 'marketplace' | 'webhooks';

const settingsTabs: { key: SettingsTab; label: string }[] = [
  { key: 'profile', label: 'Profile' },
  { key: 'hours', label: 'Hours' },
  { key: 'policies', label: 'Policies' },
  { key: 'plans', label: 'Plans' },
  { key: 'spaces', label: 'Spaces' },
  { key: 'marketplace', label: 'Marketplace' },
  { key: 'webhooks', label: 'Webhooks' },
];

function SaveFeedback({ isPending, isSuccess, isError }: { isPending: boolean; isSuccess: boolean; isError: boolean }) {
  if (isPending) return <span className="text-sm text-gray-500">Saving...</span>;
  if (isSuccess) return <span className="text-sm text-green-600">Saved.</span>;
  if (isError) return <span className="text-sm text-red-600">Failed to save.</span>;
  return null;
}

function LoadingState({ label }: { label: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-600">
      Loading {label}...
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {message}
    </div>
  );
}

function ProfileSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['gym-profile'],
    queryFn: async () => {
      const result = await gymsGetMyGymProfile({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  // Local edits override server data; null means user hasn't edited yet
  const [edits, setEdits] = useState<Record<string, string> | null>(null);
  const form = {
    name: edits?.name ?? data?.name ?? '',
    description: edits?.description ?? data?.description ?? '',
    tagline: edits?.tagline ?? data?.tagline ?? '',
    contact_email: edits?.contact_email ?? data?.contact_email ?? '',
    contact_phone: edits?.contact_phone ?? data?.contact_phone ?? '',
    address_line1: edits?.address_line1 ?? data?.address_line1 ?? '',
    city: edits?.city ?? data?.city ?? '',
    province: edits?.province ?? data?.province ?? '',
    postal_code: edits?.postal_code ?? data?.postal_code ?? '',
  };
  const setForm = (next: typeof form) => setEdits(next);

  const mutation = useMutation({
    mutationFn: async (payload: typeof form) => {
      await gymsUpdateMyGymProfile({
        body: {
          name: payload.name || null,
          description: payload.description || null,
          tagline: payload.tagline || null,
          contact_email: payload.contact_email || null,
          contact_phone: payload.contact_phone || null,
          address_line1: payload.address_line1 || null,
          city: payload.city || null,
          province: payload.province || null,
          postal_code: payload.postal_code || null,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gym-profile'] });
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  if (isLoading) return <LoadingState label="profile" />;
  if (error) return <ErrorState message="Could not load gym profile." />;

  return (
    <form className="space-y-4 max-w-lg" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Gym Name</label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input
          type="email"
          value={form.contact_email}
          onChange={(e) => setForm({ ...form, contact_email: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
        <input
          type="tel"
          value={form.contact_phone}
          onChange={(e) => setForm({ ...form, contact_phone: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tagline</label>
        <input
          type="text"
          value={form.tagline}
          onChange={(e) => setForm({ ...form, tagline: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
        <input
          type="text"
          value={form.address_line1}
          onChange={(e) => setForm({ ...form, address_line1: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
        />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
          <input
            type="text"
            value={form.city}
            onChange={(e) => setForm({ ...form, city: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Province</label>
          <input
            type="text"
            value={form.province}
            onChange={(e) => setForm({ ...form, province: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
          <input
            type="text"
            value={form.postal_code}
            onChange={(e) => setForm({ ...form, postal_code: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
        />
      </div>
      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving...' : 'Save Changes'}
        </button>
        <SaveFeedback isPending={false} isSuccess={mutation.isSuccess} isError={mutation.isError} />
      </div>
    </form>
  );
}

const WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const WEEKDAY_LABELS: Record<string, string> = {
  monday: 'Monday',
  tuesday: 'Tuesday',
  wednesday: 'Wednesday',
  thursday: 'Thursday',
  friday: 'Friday',
  saturday: 'Saturday',
  sunday: 'Sunday',
};

type DayHours = { open: string; close: string; is_closed: boolean };
type BusinessHoursForm = Record<string, DayHours>;

function defaultBusinessHours(): BusinessHoursForm {
  const hours: BusinessHoursForm = {};
  for (const day of WEEKDAYS) {
    hours[day] = { open: '06:00', close: '21:00', is_closed: false };
  }
  return hours;
}

function HoursSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['gym-operating-hours'],
    queryFn: async () => {
      const result = await gymsGetMyGymOperatingHours({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  const [localHours, setLocalHours] = useState<BusinessHoursForm | null>(null);

  // Derive hours from server data, with local edits taking precedence
  const serverHours: BusinessHoursForm = (() => {
    if (!data?.business_hours) return defaultBusinessHours();
    const parsed: BusinessHoursForm = {};
    for (const day of WEEKDAYS) {
      const dayData = data.business_hours[day];
      if (dayData) {
        parsed[day] = {
          open: (dayData.open as string) ?? '06:00',
          close: (dayData.close as string) ?? '21:00',
          is_closed: (dayData.is_closed as boolean) ?? false,
        };
      } else {
        parsed[day] = { open: '06:00', close: '21:00', is_closed: false };
      }
    }
    return parsed;
  })();
  const hours = localHours ?? serverHours;
  const setHours = setLocalHours;

  const mutation = useMutation({
    mutationFn: async (payload: BusinessHoursForm) => {
      await gymsUpdateMyGymOperatingHours({
        body: { business_hours: payload },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gym-operating-hours'] });
    },
  });

  const updateDay = (day: string, field: keyof DayHours, value: string | boolean) => {
    setHours((prev) => ({
      ...prev,
      [day]: { ...prev[day], [field]: value },
    }));
  };

  if (isLoading) return <LoadingState label="operating hours" />;
  if (error) return <ErrorState message="Could not load operating hours." />;

  return (
    <div className="space-y-3 max-w-lg">
      {WEEKDAYS.map((day) => (
        <div key={day} className="flex items-center gap-4">
          <span className="w-28 text-sm font-medium text-gray-700">{WEEKDAY_LABELS[day]}</span>
          <label className="flex items-center gap-1 text-xs text-gray-500">
            <input
              type="checkbox"
              checked={hours[day]?.is_closed ?? false}
              onChange={(e) => updateDay(day, 'is_closed', e.target.checked)}
            />
            Closed
          </label>
          {!hours[day]?.is_closed && (
            <>
              <input
                type="time"
                value={hours[day]?.open ?? '06:00'}
                onChange={(e) => updateDay(day, 'open', e.target.value)}
                className="px-2 py-1.5 border border-gray-300 rounded-md text-sm"
              />
              <span className="text-gray-400">to</span>
              <input
                type="time"
                value={hours[day]?.close ?? '21:00'}
                onChange={(e) => updateDay(day, 'close', e.target.value)}
                className="px-2 py-1.5 border border-gray-300 rounded-md text-sm"
              />
            </>
          )}
        </div>
      ))}
      <div className="flex items-center gap-3 mt-4">
        <button
          onClick={() => mutation.mutate(hours)}
          disabled={mutation.isPending}
          className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving...' : 'Save Hours'}
        </button>
        <SaveFeedback isPending={false} isSuccess={mutation.isSuccess} isError={mutation.isError} />
      </div>
    </div>
  );
}

function PoliciesSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['gym-cancellation-policy'],
    queryFn: async () => {
      const result = await gymsGetMyGymCancellationPolicy({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  const [edits, setEdits] = useState<{ cancellation_window_hours: number; no_show_penalty: string } | null>(null);
  const form = {
    cancellation_window_hours: edits?.cancellation_window_hours ?? (data as Record<string, unknown>)?.cancellation_window_hours as number ?? 4,
    no_show_penalty: edits?.no_show_penalty ?? (data as Record<string, unknown>)?.no_show_penalty as string ?? 'fee',
  };
  const setForm = (next: typeof form) => setEdits(next);

  const mutation = useMutation({
    mutationFn: async (payload: typeof form) => {
      await gymsUpdateMyGymCancellationPolicy({
        body: payload,
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gym-cancellation-policy'] });
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  if (isLoading) return <LoadingState label="cancellation policy" />;
  if (error) return <ErrorState message="Could not load cancellation policy." />;

  return (
    <form className="space-y-4 max-w-lg" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Cancellation Window (hours)</label>
        <input
          type="number"
          value={form.cancellation_window_hours}
          onChange={(e) => setForm({ ...form, cancellation_window_hours: parseInt(e.target.value) || 0 })}
          className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
        />
        <p className="text-xs text-gray-500 mt-1">Members must cancel this many hours before class starts.</p>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">No-Show Penalty</label>
        <select
          value={form.no_show_penalty}
          onChange={(e) => setForm({ ...form, no_show_penalty: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
        >
          <option value="fee">Charge a fee</option>
          <option value="credit_deduction">Deduct from credits</option>
          <option value="warning">Warning only</option>
          <option value="none">No penalty</option>
        </select>
      </div>
      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Saving...' : 'Save Policies'}
        </button>
        <SaveFeedback isPending={false} isSuccess={mutation.isSuccess} isError={mutation.isError} />
      </div>
    </form>
  );
}

function PlansSettings() {
  // TODO: Wire to a staff-facing plans management endpoint when available.
  // Currently no suitable staff-scoped endpoint exists for full plan CRUD.
  const plans = [
    { name: 'Premium Monthly', price: 'R 599.00', members: 145, status: 'active' },
    { name: 'Basic Monthly', price: 'R 399.00', members: 120, status: 'active' },
    { name: 'Premium Annual', price: 'R 5,400.00', members: 52, status: 'active' },
    { name: 'Class Pack (10)', price: 'R 250.00', members: 25, status: 'active' },
  ];
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
        Coming soon: plan management will be wired to the API once a staff-facing plans endpoint is available.
      </div>
      <button className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700" disabled>
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
                  <button className="text-gold-600 hover:text-gold-800 mr-3" disabled>Edit</button>
                  <button className="text-red-600 hover:text-red-800" disabled>Archive</button>
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
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['gym-spaces'],
    queryFn: async () => {
      const result = await gymsListMySpaces({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data ?? [];
    },
  });

  const createMutation = useMutation({
    mutationFn: async (payload: { name: string; description: string; capacity: number }) => {
      await gymsCreateMySpace({
        body: {
          name: payload.name,
          description: payload.description || null,
          capacity: payload.capacity,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setShowAddForm(false);
      queryClient.invalidateQueries({ queryKey: ['gym-spaces'] });
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: async (spaceId: string) => {
      await gymsDeactivateMySpace({
        path: { space_id: spaceId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gym-spaces'] });
    },
  });

  const handleCreateSpace = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const name = String(formData.get('name') ?? '').trim();
    const description = String(formData.get('description') ?? '').trim();
    const capacity = parseInt(String(formData.get('capacity') ?? '0'), 10);
    if (!name || capacity <= 0) return;
    createMutation.mutate({ name, description, capacity });
  };

  if (isLoading) return <LoadingState label="spaces" />;
  if (error) return <ErrorState message="Could not load spaces." />;

  const spaces = data ?? [];

  return (
    <div className="space-y-4">
      <button
        onClick={() => setShowAddForm((v) => !v)}
        className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700"
      >
        {showAddForm ? 'Cancel' : 'Add Space'}
      </button>

      {showAddForm && (
        <form className="border border-gray-200 rounded-lg p-4 space-y-3" onSubmit={handleCreateSpace}>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              name="name"
              type="text"
              required
              placeholder="e.g. Studio A"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              name="description"
              type="text"
              placeholder="Group Fitness, Yoga, etc."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Capacity</label>
            <input
              name="capacity"
              type="number"
              min={1}
              required
              placeholder="20"
              className="w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
            />
          </div>
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Space'}
            </button>
            {createMutation.isError && <span className="text-sm text-red-600">Failed to create space.</span>}
          </div>
        </form>
      )}

      {spaces.length === 0 ? (
        <div className="border border-gray-200 rounded-lg p-6 text-center text-sm text-gray-500">
          No spaces configured. Add a space to get started.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {spaces.map((space) => (
            <div key={space.id} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900">{space.name}</h3>
              <p className="text-sm text-gray-500">Capacity: {space.capacity}</p>
              {space.description && (
                <p className="text-sm text-gray-500">{space.description}</p>
              )}
              <p className="text-sm text-gray-500">
                Bookable: {space.is_bookable ? 'Yes' : 'No'}
              </p>
              <div className="mt-2 flex gap-3">
                <button
                  onClick={() => deactivateMutation.mutate(space.id)}
                  disabled={deactivateMutation.isPending}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Deactivate
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MarketplaceSettings() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['gym-marketplace-toggle'],
    queryFn: async () => {
      const result = await gymsGetMyMarketplaceToggle({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  const [localEnabled, setLocalEnabled] = useState<boolean | null>(null);
  const enabled = localEnabled ?? (data as Record<string, unknown>)?.marketplace_enabled as boolean ?? false;

  const mutation = useMutation({
    mutationFn: async (marketplaceEnabled: boolean) => {
      await gymsUpdateMyMarketplaceToggle({
        body: { marketplace_enabled: marketplaceEnabled },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gym-marketplace-toggle'] });
    },
  });

  const handleToggle = () => {
    const newValue = !enabled;
    setLocalEnabled(newValue);
    mutation.mutate(newValue);
  };

  if (isLoading) return <LoadingState label="marketplace settings" />;
  if (error) return <ErrorState message="Could not load marketplace settings." />;

  return (
    <div className="space-y-4 max-w-lg">
      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
        <div>
          <p className="font-medium text-gray-900">Marketplace Listing</p>
          <p className="text-sm text-gray-500">Show your gym on the StudioLoop marketplace</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={enabled}
            onChange={handleToggle}
            disabled={mutation.isPending}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-gold-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gold-600"></div>
        </label>
      </div>
      <SaveFeedback isPending={mutation.isPending} isSuccess={mutation.isSuccess} isError={mutation.isError} />
    </div>
  );
}

function WebhooksSettings() {
  return (
    <div className="space-y-4 max-w-lg">
      <p className="text-sm text-gray-500">
        Configure webhook endpoints to receive real-time notifications about events in your gym.
      </p>
      <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
        Coming soon — webhook management is not yet available.
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
          {settingsTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-gold-500 text-gold-600'
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
