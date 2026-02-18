/**
 * Class detail screen (Story 13.5 + 13.6).
 *
 * Shows full class details with booking options:
 * - Book with membership
 * - Book with marketplace subscription
 * - Pay per class
 */

import { useState } from 'react';
import { useParams, Link } from 'react-router';

type BookingMethod = 'membership' | 'subscription' | 'pay_per_class';

interface ClassDetail {
  id: string;
  name: string;
  description: string;
  gym_name: string;
  gym_id: string;
  instructor_name: string;
  instructor_bio: string;
  class_type: string;
  start_time: string;
  end_time: string;
  location: string;
  address: string;
  price_zar: number;
  spots_remaining: number;
  total_spots: number;
  difficulty: string;
  equipment_needed: string[];
}

// Placeholder class detail
const PLACEHOLDER_CLASS: ClassDetail = {
  id: 'cls-1',
  name: 'Morning Yoga Flow',
  description:
    'Start your day with an energising yoga flow that combines breath work, sun salutations, and gentle stretching. Suitable for all levels. This class focuses on building strength, flexibility, and mindfulness through a carefully sequenced vinyasa practice.',
  gym_name: 'ZenFit Studio',
  gym_id: 'gym-1',
  instructor_name: 'Thandi Nkosi',
  instructor_bio: 'Certified 500hr yoga instructor with 8 years of teaching experience. Specialises in Vinyasa and Yin yoga.',
  class_type: 'Yoga',
  start_time: '2026-02-19T07:00:00',
  end_time: '2026-02-19T08:00:00',
  location: 'Studio A',
  address: '123 Sandton Drive, Sandton, Johannesburg',
  price_zar: 150,
  spots_remaining: 8,
  total_spots: 20,
  difficulty: 'All Levels',
  equipment_needed: ['Yoga mat', 'Water bottle'],
};

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('en-ZA', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

export function ClassDetail() {
  const { classId } = useParams();
  const [bookingMethod, setBookingMethod] = useState<BookingMethod>('pay_per_class');
  const [isBooking, setIsBooking] = useState(false);
  const [booked, setBooked] = useState(false);

  // TODO: Replace with TanStack Query to fetch real class details
  const classDetail = { ...PLACEHOLDER_CLASS, id: classId ?? PLACEHOLDER_CLASS.id };

  const handleBook = async () => {
    setIsBooking(true);
    // TODO: Wire up to actual booking API based on bookingMethod
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsBooking(false);
    setBooked(true);
  };

  const isFull = classDetail.spots_remaining === 0;

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <Link
        to="/discover"
        className="inline-flex items-center text-sm text-indigo-600 hover:text-indigo-500 font-medium mb-6"
      >
        &larr; Back to classes
      </Link>

      {/* Header */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="h-3 bg-indigo-500" />
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 mb-2">
                {classDetail.class_type}
              </span>
              <h1 className="text-2xl font-bold text-gray-900">{classDetail.name}</h1>
            </div>
            <Link
              to={`/discover/${classDetail.id}/share`}
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
            >
              <svg className="w-3.5 h-3.5 mr-1" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 100 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186l9.566-5.314m-9.566 7.5l9.566 5.314m0 0a2.25 2.25 0 103.935 2.186 2.25 2.25 0 00-3.935-2.186zm0-12.814a2.25 2.25 0 103.933-2.185 2.25 2.25 0 00-3.933 2.185z" />
              </svg>
              Share
            </Link>
          </div>

          <p className="text-gray-600 leading-relaxed mb-6">{classDetail.description}</p>

          {/* Details grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Studio</p>
              <p className="font-medium text-gray-900">{classDetail.gym_name}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Instructor</p>
              <p className="font-medium text-gray-900">{classDetail.instructor_name}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Date & Time</p>
              <p className="font-medium text-gray-900">{formatDate(classDetail.start_time)}</p>
              <p className="text-sm text-gray-600">{formatTime(classDetail.start_time)} - {formatTime(classDetail.end_time)}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Location</p>
              <p className="font-medium text-gray-900">{classDetail.location}</p>
              <p className="text-sm text-gray-600">{classDetail.address}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Difficulty</p>
              <p className="font-medium text-gray-900">{classDetail.difficulty}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Availability</p>
              <p className={`font-medium ${isFull ? 'text-red-600' : 'text-green-600'}`}>
                {isFull ? 'Full' : `${classDetail.spots_remaining} of ${classDetail.total_spots} spots`}
              </p>
            </div>
          </div>

          {/* Equipment */}
          {classDetail.equipment_needed.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">What to bring</h3>
              <div className="flex flex-wrap gap-2">
                {classDetail.equipment_needed.map((item) => (
                  <span
                    key={item}
                    className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Instructor bio */}
          <div className="mb-6 border-t border-gray-100 pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-1">About {classDetail.instructor_name}</h3>
            <p className="text-sm text-gray-600">{classDetail.instructor_bio}</p>
          </div>

          {/* Booking section */}
          {booked ? (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
              <svg className="mx-auto w-10 h-10 text-green-600 mb-2" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-lg font-semibold text-green-800">Booking confirmed!</h3>
              <p className="text-sm text-green-600 mt-1">You&apos;re all set for {classDetail.name}.</p>
              <Link
                to="/"
                className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
              >
                View my bookings
              </Link>
            </div>
          ) : (
            <div className="border-t border-gray-100 pt-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Book this class</h3>

              {/* Booking method selection */}
              <div className="space-y-2 mb-4">
                <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="booking_method"
                    value="membership"
                    checked={bookingMethod === 'membership'}
                    onChange={() => setBookingMethod('membership')}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Use gym membership</p>
                    <p className="text-xs text-gray-500">Book using your existing membership at {classDetail.gym_name}</p>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="booking_method"
                    value="subscription"
                    checked={bookingMethod === 'subscription'}
                    onChange={() => setBookingMethod('subscription')}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Use marketplace subscription</p>
                    <p className="text-xs text-gray-500">Use a class credit from your StudioLoop subscription</p>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="booking_method"
                    value="pay_per_class"
                    checked={bookingMethod === 'pay_per_class'}
                    onChange={() => setBookingMethod('pay_per_class')}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Pay per class</p>
                    <p className="text-xs text-gray-500">R {classDetail.price_zar.toFixed(2)} - single session payment</p>
                  </div>
                </label>
              </div>

              <button
                onClick={handleBook}
                disabled={isFull || isBooking}
                className="w-full py-3 px-4 border border-transparent text-sm font-medium rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isBooking
                  ? 'Booking...'
                  : isFull
                    ? 'Class is full - Join waitlist'
                    : bookingMethod === 'pay_per_class'
                      ? `Book for R ${classDetail.price_zar.toFixed(2)}`
                      : 'Confirm booking'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ClassDetail;
