/**
 * Home / My Bookings screen (Story 13.3).
 *
 * Shows the consumer's upcoming bookings with options to cancel
 * or view their QR code for check-in.
 */

import { useState } from 'react';
import { Link } from 'react-router';

interface Booking {
  id: string;
  class_name: string;
  gym_name: string;
  instructor_name: string;
  start_time: string;
  end_time: string;
  location: string;
  status: 'confirmed' | 'waitlisted' | 'cancelled';
}

// Placeholder bookings for development
const PLACEHOLDER_BOOKINGS: Booking[] = [
  {
    id: '1',
    class_name: 'Morning Yoga Flow',
    gym_name: 'ZenFit Studio',
    instructor_name: 'Thandi Nkosi',
    start_time: '2026-02-19T07:00:00',
    end_time: '2026-02-19T08:00:00',
    location: 'Studio A',
    status: 'confirmed',
  },
  {
    id: '2',
    class_name: 'HIIT Blast',
    gym_name: 'PowerHouse Gym',
    instructor_name: 'Sipho Dlamini',
    start_time: '2026-02-19T17:30:00',
    end_time: '2026-02-19T18:15:00',
    location: 'Main Floor',
    status: 'confirmed',
  },
  {
    id: '3',
    class_name: 'Pilates Reformer',
    gym_name: 'Body Balance',
    instructor_name: 'Lerato Molefe',
    start_time: '2026-02-20T09:00:00',
    end_time: '2026-02-20T10:00:00',
    location: 'Reformer Room',
    status: 'waitlisted',
  },
];

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-ZA', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-ZA', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

function BookingCard({ booking, onCancel }: { booking: Booking; onCancel: (id: string) => void }) {
  const isUpcoming = booking.status !== 'cancelled';

  return (
    <div className={`bg-white rounded-xl border p-4 ${booking.status === 'cancelled' ? 'opacity-50' : 'border-gray-200'}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-gray-900 truncate">{booking.class_name}</h3>
            {booking.status === 'waitlisted' && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                Waitlisted
              </span>
            )}
            {booking.status === 'cancelled' && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                Cancelled
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">{booking.gym_name}</p>
          <p className="text-sm text-gray-500">with {booking.instructor_name}</p>
          <div className="mt-2 flex items-center gap-3 text-sm text-gray-500">
            <span>{formatDate(booking.start_time)}</span>
            <span>{formatTime(booking.start_time)} - {formatTime(booking.end_time)}</span>
            <span>{booking.location}</span>
          </div>
        </div>

        {isUpcoming && (
          <div className="flex items-center gap-2 ml-4">
            <Link
              to="/qr-code"
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
            >
              QR Code
            </Link>
            <button
              onClick={() => onCancel(booking.id)}
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg bg-red-50 text-red-700 hover:bg-red-100 transition-colors"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export function Home() {
  const [bookings, setBookings] = useState<Booking[]>(PLACEHOLDER_BOOKINGS);

  // TODO: Replace with TanStack Query call to fetch real bookings
  // const { data: bookings, isLoading } = useQuery({
  //   queryKey: ['my-bookings'],
  //   queryFn: () => fetchMyBookings(),
  // });

  const handleCancel = (id: string) => {
    // TODO: Wire up to actual cancel booking API
    setBookings((prev) =>
      prev.map((b) => (b.id === id ? { ...b, status: 'cancelled' as const } : b)),
    );
  };

  const upcomingBookings = bookings.filter((b) => b.status !== 'cancelled');
  const cancelledBookings = bookings.filter((b) => b.status === 'cancelled');

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Bookings</h1>
        <Link
          to="/discover"
          className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
        >
          Find a class
        </Link>
      </div>

      {upcomingBookings.length === 0 && cancelledBookings.length === 0 ? (
        <div className="text-center py-12">
          <svg className="mx-auto w-12 h-12 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No bookings yet</h3>
          <p className="mt-1 text-sm text-gray-500">Browse classes and book your first session.</p>
          <Link
            to="/discover"
            className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
          >
            Discover classes
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {upcomingBookings.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Upcoming ({upcomingBookings.length})
              </h2>
              <div className="space-y-3">
                {upcomingBookings.map((booking) => (
                  <BookingCard key={booking.id} booking={booking} onCancel={handleCancel} />
                ))}
              </div>
            </section>
          )}

          {cancelledBookings.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Cancelled
              </h2>
              <div className="space-y-3">
                {cancelledBookings.map((booking) => (
                  <BookingCard key={booking.id} booking={booking} onCancel={handleCancel} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

export default Home;
