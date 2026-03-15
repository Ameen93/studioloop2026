import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  bookingsCancelBooking,
  bookingsListConsumerBookings,
  type BookingStatus,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type TabType = 'upcoming' | 'past' | 'cancelled';

const tabToStatus: Record<TabType, BookingStatus> = {
  upcoming: 'booked',
  past: 'checked_in',
  cancelled: 'cancelled',
};

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    booked: 'bg-blue-100 text-blue-700',
    checked_in: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
  };

  const labels: Record<string, string> = {
    booked: 'Upcoming',
    checked_in: 'Attended',
    cancelled: 'Cancelled',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
        styles[status] ?? 'bg-gray-100 text-gray-600'
      }`}
    >
      {labels[status] ?? status}
    </span>
  );
}

export function Bookings() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('upcoming');

  const bookingsQuery = useQuery({
    queryKey: ['consumer-bookings', activeTab],
    queryFn: async () => {
      const response = await bookingsListConsumerBookings({
        query: { status: tabToStatus[activeTab], limit: 50 },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const cancelMutation = useMutation({
    mutationFn: async (bookingId: string) => {
      await bookingsCancelBooking({
        path: { booking_id: bookingId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['consumer-bookings'] });
    },
  });

  const items = bookingsQuery.data?.items ?? [];
  const tabs: { key: TabType; label: string }[] = [
    { key: 'upcoming', label: 'Upcoming' },
    { key: 'past', label: 'Past' },
    { key: 'cancelled', label: 'Cancelled' },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Bookings</h1>

      <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 py-2 px-4 text-sm font-medium rounded-lg transition-colors ${
              activeTab === tab.key
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {bookingsQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading bookings...
        </div>
      )}

      {bookingsQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load bookings.
        </div>
      )}

      {cancelMutation.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 mb-4">
          Could not cancel booking. Please try again.
        </div>
      )}

      <div className="space-y-4">
        {items.length === 0 && !bookingsQuery.isLoading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">
              {activeTab === 'upcoming'
                ? 'No upcoming bookings.'
                : activeTab === 'past'
                  ? 'No past bookings yet.'
                  : 'No cancelled bookings.'}
            </p>
          </div>
        ) : (
          items.map((booking) => (
            <div
              key={booking.id}
              className="bg-white rounded-xl border border-gray-200 p-5"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {booking.class_name}
                  </h3>
                  <p className="text-sm text-gray-600">{booking.gym_name}</p>
                </div>
                <StatusBadge status={booking.status} />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-gray-500">Date & Time</p>
                  <p className="font-medium text-gray-900">
                    {formatDateTime(booking.start_time)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Type</p>
                  <p className="font-medium text-gray-900 capitalize">
                    {booking.booking_type.replace('_', ' ')}
                  </p>
                </div>
                {booking.price_paid_cents != null && (
                  <div>
                    <p className="text-gray-500">Price</p>
                    <p className="font-medium text-gray-900">
                      R {(booking.price_paid_cents / 100).toFixed(2)}
                    </p>
                  </div>
                )}
              </div>

              {activeTab === 'upcoming' && (
                <div className="mt-4 pt-3 border-t border-gray-100">
                  <button
                    onClick={() => cancelMutation.mutate(booking.id)}
                    disabled={cancelMutation.isPending}
                    className="text-sm text-red-600 hover:text-red-800 font-medium disabled:opacity-50"
                  >
                    {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Booking'}
                  </button>
                </div>
              )}

              {booking.status === 'cancelled' && booking.cancellation_refunded && (
                <div className="mt-3">
                  <span className="text-xs text-green-600 font-medium">Refunded</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Bookings;
