import { useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  marketplaceViewMarketplaceGymProfile,
  staffMembershipsListConsumerMemberships,
  staffMembershipsListPublicMembershipPlans,
  staffMembershipsEnrollMembership,
  staffMembershipsAcceptDigitalWaiver,
} from '@sl/api-client';
import type { MembershipPlanPublic } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

function formatPrice(cents: number): string {
  return `R ${(cents / 100).toFixed(2)}`;
}

function billingLabel(cycle: string): string {
  return cycle === 'weekly' ? '/week' : '/month';
}

export function StudioProfile() {
  const { gymId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedPlan, setSelectedPlan] = useState<MembershipPlanPublic | null>(null);
  const [waiverAccepted, setWaiverAccepted] = useState(false);
  const [enrollError, setEnrollError] = useState<string | null>(null);
  const [enrolled, setEnrolled] = useState(false);

  const profileQuery = useQuery({
    queryKey: ['gym-profile', gymId],
    queryFn: async () => {
      if (!gymId) return null;
      const response = await marketplaceViewMarketplaceGymProfile({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
    enabled: Boolean(gymId),
  });

  const gymSlug = (profileQuery.data as Record<string, unknown>)?.slug as string | undefined;

  const plansQuery = useQuery({
    queryKey: ['gym-membership-plans', gymSlug],
    queryFn: async () => {
      if (!gymSlug) return [];
      const response = await staffMembershipsListPublicMembershipPlans({
        path: { gym_slug: gymSlug },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
    enabled: Boolean(gymSlug),
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

  const existingMembership = (myMembershipsQuery.data ?? []).find(
    (m) => m.gym_id === gymId && m.status === 'active',
  );

  const enrollMutation = useMutation({
    mutationFn: async (plan: MembershipPlanPublic) => {
      if (plan.waiver_text && !waiverAccepted) {
        throw new Error('Please accept the waiver first');
      }

      const enrollResponse = await staffMembershipsEnrollMembership({
        body: {
          gym_id: plan.gym_id,
          membership_plan_id: plan.id,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });

      if (plan.waiver_text && enrollResponse.data) {
        await staffMembershipsAcceptDigitalWaiver({
          body: {
            gym_membership_id: enrollResponse.data.id,
          },
          headers: getAuthHeaders(),
          throwOnError: true,
        });
      }

      return enrollResponse.data;
    },
    onSuccess: () => {
      setEnrollError(null);
      setEnrolled(true);
      setSelectedPlan(null);
      void queryClient.invalidateQueries({ queryKey: ['consumer-memberships'] });
      void queryClient.invalidateQueries({ queryKey: ['consumer-gym-memberships'] });
    },
    onError: () => {
      setEnrollError('Enrollment failed. Please try again.');
    },
  });

  const profile = profileQuery.data;
  const plans = (plansQuery.data ?? []).filter((p) => p.is_active);

  if (enrolled) {
    return (
      <div className="max-w-lg mx-auto px-4 py-12 text-center">
        <div className="bg-green-50 border border-green-200 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-green-800 mb-2">
            You're now a member of {profile?.name}!
          </h2>
          <p className="text-green-600 mb-6">
            Your membership is active. You can now book classes directly.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link
              to="/"
              className="px-5 py-2.5 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors"
            >
              Go to Home
            </Link>
            <Link
              to="/discover"
              className="px-5 py-2.5 text-sm font-medium rounded-lg bg-white text-green-700 border border-green-300 hover:bg-green-50 transition-colors"
            >
              Keep Exploring
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <Link
        to="/discover"
        className="inline-flex items-center text-sm text-coral-600 hover:text-coral-500 font-medium mb-6"
      >
        &larr; Back to Discover
      </Link>

      {profileQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading studio profile...
        </div>
      )}

      {profileQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load studio profile.
        </div>
      )}

      {!profile ? null : (
        <>
          {/* Studio Header */}
          <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden mb-6">
            <div className="h-3 bg-coral-500" />
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{profile.name}</h1>
                  {profile.tagline && (
                    <p className="text-sm text-gray-500 mt-1">{profile.tagline}</p>
                  )}
                </div>
                {existingMembership && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                    Member
                  </span>
                )}
              </div>

              {profile.description && (
                <p className="text-gray-600 leading-relaxed mb-4">{profile.description}</p>
              )}

              <div className="grid grid-cols-2 gap-3 text-sm">
                {profile.address_line1 && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500 uppercase tracking-wider">Location</p>
                    <p className="font-medium text-gray-900">
                      {[profile.address_line1, profile.city, profile.province]
                        .filter(Boolean)
                        .join(', ')}
                    </p>
                  </div>
                )}
                {profile.amenities.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500 uppercase tracking-wider">Amenities</p>
                    <p className="font-medium text-gray-900">
                      {profile.amenities.slice(0, 4).join(', ')}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Membership Plans Section */}
          {plans.length > 0 && !existingMembership && (
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Membership Plans</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {plans.map((plan) => (
                  <div
                    key={plan.id}
                    className={`bg-white rounded-xl border-2 p-5 cursor-pointer transition-all ${
                      selectedPlan?.id === plan.id
                        ? 'border-coral-500 shadow-md'
                        : 'border-gray-200 hover:border-coral-300'
                    }`}
                    onClick={() => {
                      setSelectedPlan(plan);
                      setWaiverAccepted(false);
                      setEnrollError(null);
                    }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{plan.name}</h3>
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-coral-50 text-coral-700 capitalize">
                        {plan.tier}
                      </span>
                    </div>

                    <p className="text-2xl font-bold text-gray-900 mb-1">
                      {formatPrice(plan.price_cents)}
                      <span className="text-sm font-normal text-gray-500">
                        {billingLabel(plan.billing_cycle)}
                      </span>
                    </p>

                    {plan.description && (
                      <p className="text-sm text-gray-600 mb-3">{plan.description}</p>
                    )}

                    {plan.benefits.length > 0 && (
                      <ul className="space-y-1">
                        {plan.benefits.map((benefit, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start gap-1.5">
                            <span className="text-green-500 mt-0.5">&#10003;</span>
                            {benefit}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Enroll Panel */}
          {selectedPlan && !existingMembership && (
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Enroll in {selectedPlan.name}
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                {formatPrice(selectedPlan.price_cents)}
                {billingLabel(selectedPlan.billing_cycle)} &mdash; {selectedPlan.tier} tier
              </p>

              {selectedPlan.waiver_text && (
                <div className="mb-4 bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Terms & Waiver</h4>
                  <p className="text-xs text-gray-600 mb-3 max-h-32 overflow-y-auto leading-relaxed">
                    {selectedPlan.waiver_text}
                  </p>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={waiverAccepted}
                      onChange={(e) => setWaiverAccepted(e.target.checked)}
                      className="text-coral-600 focus:ring-coral-500 rounded"
                    />
                    <span className="text-sm text-gray-700">I agree to the terms</span>
                  </label>
                </div>
              )}

              {enrollError && <p className="mb-3 text-sm text-red-600">{enrollError}</p>}

              <button
                onClick={() => enrollMutation.mutate(selectedPlan)}
                disabled={
                  enrollMutation.isPending ||
                  (Boolean(selectedPlan.waiver_text) && !waiverAccepted)
                }
                className="w-full py-3 px-4 text-sm font-medium rounded-xl text-white bg-coral-600 hover:bg-coral-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-coral-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {enrollMutation.isPending
                  ? 'Processing...'
                  : `Enroll — ${formatPrice(selectedPlan.price_cents)}${billingLabel(selectedPlan.billing_cycle)}`}
              </button>
            </div>
          )}

          {/* Already a member */}
          {existingMembership && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-5 mb-6">
              <p className="text-green-800 font-medium">
                You're a member of {profile.name}
              </p>
              <p className="text-sm text-green-600 mt-1">
                Your {existingMembership.membership_tier} membership is active.
              </p>
            </div>
          )}

          {/* Upcoming Classes */}
          {profile.upcoming_marketplace_classes.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Classes</h2>
              <div className="space-y-3">
                {profile.upcoming_marketplace_classes.map((cls) => (
                  <Link
                    key={cls.session_id}
                    to={`/discover/${cls.session_id}`}
                    className="block bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{cls.title}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(cls.start_time).toLocaleDateString('en-ZA', {
                            weekday: 'short',
                            day: 'numeric',
                            month: 'short',
                          })}{' '}
                          at{' '}
                          {new Date(cls.start_time).toLocaleTimeString('en-ZA', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false,
                          })}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-900">
                          {formatPrice(cls.price_cents)}
                        </p>
                        <p className="text-xs text-green-600">
                          {cls.spots_remaining} spots left
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default StudioProfile;
