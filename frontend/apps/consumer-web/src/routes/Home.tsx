import { Link } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import {
  analyticsConsumerClassHistory,
  analyticsConsumerStats,
  bookingsGetConsumerQr,
} from '@sl/api-client';
import { getAuthHeaders } from '../lib/apiAuth';

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}

export function Home() {
  const statsQuery = useQuery({
    queryKey: ['consumer-stats'],
    queryFn: async () => {
      const response = await analyticsConsumerStats({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const classHistoryQuery = useQuery({
    queryKey: ['consumer-class-history'],
    queryFn: async () => {
      const response = await analyticsConsumerClassHistory({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const qrQuery = useQuery({
    queryKey: ['consumer-qr-info'],
    queryFn: async () => {
      const response = await bookingsGetConsumerQr({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const classHistoryItems = classHistoryQuery.data?.items ?? [];
  const todaysBookingIds = qrQuery.data?.todays_booking_ids ?? [];

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Activity</h1>
        <Link
          to="/discover"
          className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-coral-600 hover:bg-coral-700 transition-colors"
        >
          Find a class
        </Link>
      </div>

      {(statsQuery.isLoading || classHistoryQuery.isLoading || qrQuery.isLoading) && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading your activity...
        </div>
      )}

      {(statsQuery.error || classHistoryQuery.error || qrQuery.error) && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load your full activity data.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Classes This Month</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">
            {statsQuery.data?.total_classes_this_month ?? 0}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Current Streak (Weeks)</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">
            {statsQuery.data?.current_streak_weeks ?? 0}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Today&apos;s Booking IDs</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{todaysBookingIds.length}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Recent Class History
          </h2>
          <Link to="/bookings" className="text-xs font-medium text-coral-600 hover:text-coral-500">
            View all bookings
          </Link>
        </div>

        {classHistoryItems.length === 0 ? (
          <p className="text-sm text-gray-500">No class history yet.</p>
        ) : (
          <div className="space-y-3">
            {classHistoryItems.slice(0, 6).map((item) => (
              <div
                key={item.session_id}
                className="border border-gray-100 rounded-lg px-3 py-2 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">{item.class_name}</p>
                  <p className="text-xs text-gray-500">{item.gym_name ?? item.gym_id}</p>
                </div>
                <p className="text-xs text-gray-500">{formatDate(item.attended_at)}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Check-in QR
        </h2>
        <p className="text-sm text-gray-600 mb-3">
          Generate your live check-in QR token before class.
        </p>
        <Link
          to="/qr-code"
          className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg bg-coral-50 text-coral-700 hover:bg-coral-100 transition-colors"
        >
          Open QR Code
        </Link>
      </div>
    </div>
  );
}

export default Home;
