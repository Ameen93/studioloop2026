import { useState } from 'react';
import { Link, useParams } from 'react-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  bookingsBookPayPerClass,
  bookingsBookWithMembership,
  bookingsJoinWaitlist,
  marketplaceBookMarketplaceClassWithSubscription,
  marketplaceViewMarketplaceClassDetails,
  staffMembershipsListConsumerMemberships,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type BookingMethod = 'membership' | 'subscription' | 'pay_per_class';

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
  const queryClient = useQueryClient();
  const [bookingMethod, setBookingMethod] = useState<BookingMethod>('pay_per_class');
  const [booked, setBooked] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);

  const classDetailQuery = useQuery({
    queryKey: ['marketplace-class-detail', classId],
    queryFn: async () => {
      if (!classId) {
        return null;
      }
      const response = await marketplaceViewMarketplaceClassDetails({
        path: { session_id: classId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
    enabled: Boolean(classId),
  });

  const bookingMutation = useMutation({
    mutationFn: async () => {
      const classDetail = classDetailQuery.data;
      if (!classDetail) {
        throw new Error('Class details missing');
      }

      const headers = getAuthHeaders();
      const sessionId = classDetail.session_id;

      if (classDetail.spots_remaining === 0) {
        const waitlistResponse = await bookingsJoinWaitlist({
          body: {
            gym_id: classDetail.gym_id,
            session_id: sessionId,
          },
          headers,
          throwOnError: true,
        });
        return waitlistResponse.data;
      }

      if (bookingMethod === 'membership') {
        const response = await bookingsBookWithMembership({
          body: {
            gym_id: classDetail.gym_id,
            session_id: sessionId,
          },
          headers,
          throwOnError: true,
        });
        return response.data;
      }

      if (bookingMethod === 'subscription') {
        const response = await marketplaceBookMarketplaceClassWithSubscription({
          body: {
            session_id: sessionId,
          },
          headers,
          throwOnError: true,
        });
        return response.data;
      }

      const response = await bookingsBookPayPerClass({
        body: {
          gym_id: classDetail.gym_id,
          session_id: sessionId,
          amount_cents: classDetail.price_cents,
        },
        headers,
        throwOnError: true,
      });
      return response.data;
    },
    onSuccess: () => {
      setBookingError(null);
      setBooked(true);
      void queryClient.invalidateQueries({ queryKey: ['consumer-bookings'] });
      void queryClient.invalidateQueries({ queryKey: ['consumer-class-history'] });
      void queryClient.invalidateQueries({ queryKey: ['consumer-qr-info'] });
    },
    onError: () => {
      setBookingError('Booking failed. Please verify your membership/subscription and try again.');
    },
  });

  const myMembershipsQuery = useQuery({
    queryKey: ['consumer-memberships'],
    queryFn: async () => {
      const response = await staffMembershipsListConsumerMemberships({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const classDetail = classDetailQuery.data;
  const isFull = (classDetail?.spots_remaining ?? 0) === 0;
  const hasMembershipAtGym = (myMembershipsQuery.data ?? []).some(
    (m) => m.gym_id === classDetail?.gym_id && m.status === 'active',
  );

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <Link
        to="/discover"
        className="inline-flex items-center text-sm text-coral-600 hover:text-coral-500 font-medium mb-6"
      >
        &larr; Back to classes
      </Link>

      {classDetailQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading class details...
        </div>
      )}

      {classDetailQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load class details.
        </div>
      )}

      {!classDetail ? null : (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="h-3 bg-coral-500" />
          <div className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-coral-50 text-coral-700 mb-2">
                  {classDetail.class_type}
                </span>
                <h1 className="text-2xl font-bold text-gray-900">{classDetail.title}</h1>
              </div>
              <Link
                to={`/discover/${classDetail.session_id}/share`}
                className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              >
                Share
              </Link>
            </div>

            <p className="text-gray-600 leading-relaxed mb-6">
              {classDetail.description ?? 'No class description provided.'}
            </p>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <Link
                to={`/discover/studio/${classDetail.gym_id}`}
                className="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors"
              >
                <p className="text-xs text-gray-500 uppercase tracking-wider">Studio</p>
                <p className="font-medium text-coral-600">{classDetail.gym_name}</p>
              </Link>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Instructor</p>
                <p className="font-medium text-gray-900">{classDetail.instructor_name ?? 'TBA'}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Date & Time</p>
                <p className="font-medium text-gray-900">{formatDate(classDetail.start_time)}</p>
                <p className="text-sm text-gray-600">
                  {formatTime(classDetail.start_time)} - {formatTime(classDetail.end_time)}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Location</p>
                <p className="font-medium text-gray-900">{classDetail.space_name ?? 'Studio'}</p>
                <p className="text-sm text-gray-600">
                  {[classDetail.address_line1, classDetail.city, classDetail.province]
                    .filter(Boolean)
                    .join(', ')}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Price</p>
                <p className="font-medium text-gray-900">
                  R {(classDetail.price_cents / 100).toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Availability</p>
                <p className={`font-medium ${isFull ? 'text-red-600' : 'text-green-600'}`}>
                  {isFull
                    ? 'Full'
                    : `${classDetail.spots_remaining} of ${classDetail.capacity} spots`}
                </p>
              </div>
            </div>

            {classDetail.instructor_bio && (
              <div className="mb-6 border-t border-gray-100 pt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  About {classDetail.instructor_name}
                </h3>
                <p className="text-sm text-gray-600">{classDetail.instructor_bio}</p>
              </div>
            )}

            {booked ? (
              <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
                <h3 className="text-lg font-semibold text-green-800">
                  {isFull ? 'Added to waitlist!' : 'Booking confirmed!'}
                </h3>
                <p className="text-sm text-green-600 mt-1">
                  {isFull
                    ? `We'll notify you if a spot opens for ${classDetail.title}.`
                    : `You're all set for ${classDetail.title}.`}
                </p>
                <div className="mt-4 flex items-center justify-center gap-3">
                  <Link
                    to="/"
                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
                  >
                    Go to Home
                  </Link>
                  {!hasMembershipAtGym && (
                    <Link
                      to={`/discover/studio/${classDetail.gym_id}`}
                      className="inline-flex items-center px-4 py-2 text-sm font-medium text-coral-700 bg-coral-50 rounded-lg hover:bg-coral-100 transition-colors"
                    >
                      Become a member at {classDetail.gym_name}
                    </Link>
                  )}
                </div>
              </div>
            ) : (
              <div className="border-t border-gray-100 pt-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Book this class</h3>
                <div className="space-y-2 mb-4">
                  <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="booking_method"
                      value="membership"
                      checked={bookingMethod === 'membership'}
                      onChange={() => setBookingMethod('membership')}
                      className="text-coral-600 focus:ring-coral-500"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Use gym membership</p>
                      <p className="text-xs text-gray-500">
                        Book using your existing membership at this gym
                      </p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="booking_method"
                      value="subscription"
                      checked={bookingMethod === 'subscription'}
                      onChange={() => setBookingMethod('subscription')}
                      className="text-coral-600 focus:ring-coral-500"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Use marketplace subscription
                      </p>
                      <p className="text-xs text-gray-500">
                        Use a class credit from your StudioLoop subscription
                      </p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="booking_method"
                      value="pay_per_class"
                      checked={bookingMethod === 'pay_per_class'}
                      onChange={() => setBookingMethod('pay_per_class')}
                      className="text-coral-600 focus:ring-coral-500"
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Pay per class</p>
                      <p className="text-xs text-gray-500">
                        R {(classDetail.price_cents / 100).toFixed(2)} single session
                      </p>
                    </div>
                  </label>
                </div>

                {bookingError && <p className="mb-3 text-sm text-red-600">{bookingError}</p>}

                <button
                  onClick={() => bookingMutation.mutate()}
                  disabled={bookingMutation.isPending}
                  className="w-full py-3 px-4 border border-transparent text-sm font-medium rounded-xl text-white bg-coral-600 hover:bg-coral-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-coral-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {bookingMutation.isPending
                    ? 'Processing...'
                    : isFull
                      ? 'Join waitlist'
                      : bookingMethod === 'pay_per_class'
                        ? `Book for R ${(classDetail.price_cents / 100).toFixed(2)}`
                        : 'Confirm booking'}
                </button>
              </div>
            )}

            {/* Membership CTA */}
            {!hasMembershipAtGym && (
              <div className="border-t border-gray-100 pt-4 mt-4">
                <Link
                  to={`/discover/studio/${classDetail.gym_id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-coral-50 hover:bg-coral-100 transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-coral-700">
                      Join {classDetail.gym_name} to book regularly
                    </p>
                    <p className="text-xs text-coral-600">
                      View membership plans &rarr;
                    </p>
                  </div>
                </Link>
              </div>
            )}
            {hasMembershipAtGym && (
              <div className="border-t border-gray-100 pt-4 mt-4">
                <div className="flex items-center gap-2 p-3 rounded-lg bg-green-50">
                  <span className="text-green-600 text-sm">&#10003;</span>
                  <p className="text-sm text-green-700 font-medium">
                    You're a member at {classDetail.gym_name}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ClassDetail;
