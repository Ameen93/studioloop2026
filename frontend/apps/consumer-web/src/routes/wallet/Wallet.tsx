import { Link } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import {
  marketplaceViewMarketplaceSubscriptionStatus,
  staffMembershipsListConsumerMemberships,
  analyticsConsumerClassHistory,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    paused: 'bg-amber-100 text-amber-700',
    inactive: 'bg-gray-100 text-gray-600',
    cancelled: 'bg-red-100 text-red-700',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize ${
        styles[status] ?? 'bg-gray-100 text-gray-600'
      }`}
    >
      {status}
    </span>
  );
}

export function Wallet() {
  const subscriptionQuery = useQuery({
    queryKey: ['consumer-marketplace-subscription'],
    queryFn: async () => {
      const response = await marketplaceViewMarketplaceSubscriptionStatus({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? null;
    },
  });

  const membershipsQuery = useQuery({
    queryKey: ['consumer-gym-memberships'],
    queryFn: async () => {
      const response = await staffMembershipsListConsumerMemberships({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const historyQuery = useQuery({
    queryKey: ['consumer-class-history'],
    queryFn: async () => {
      const response = await analyticsConsumerClassHistory({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data?.items ?? [];
    },
  });

  const subscription = subscriptionQuery.data;
  const memberships = membershipsQuery.data ?? [];
  const activeMemberships = memberships.filter((m) => m.status === 'active');
  const recentActivity = (historyQuery.data ?? []).slice(0, 5);
  const isLoading =
    subscriptionQuery.isLoading || membershipsQuery.isLoading || historyQuery.isLoading;

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Wallet</h1>
        <Link
          to="/discover"
          className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-coral-600 hover:bg-coral-700 transition-colors"
        >
          Find a class
        </Link>
      </div>

      {isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading wallet...
        </div>
      )}

      {/* Subscription Card */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="h-2 bg-coral-500" />
        <div className="p-6">
          <div className="flex items-start justify-between mb-2">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Marketplace Plan</p>
            {subscription && <StatusBadge status={subscription.status} />}
          </div>

          {subscription ? (
            <>
              <h2 className="text-xl font-bold text-gray-900 capitalize mb-4">
                {subscription.plan_tier} Plan
              </h2>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-3xl font-bold text-coral-600">
                    {subscription.classes_remaining}
                  </p>
                  <p className="text-sm text-gray-500">Classes left</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-900">
                    {subscription.classes_total}
                  </p>
                  <p className="text-sm text-gray-500">Total classes</p>
                </div>
                <div>
                  <p className="text-lg font-semibold text-gray-900 mt-1">
                    {formatDate(subscription.reset_at)}
                  </p>
                  <p className="text-sm text-gray-500">Resets</p>
                </div>
              </div>

              <div className="w-full bg-gray-100 rounded-full h-2.5 mb-4">
                <div
                  className="bg-coral-500 rounded-full h-2.5 transition-all"
                  style={{
                    width: `${(subscription.classes_remaining / Math.max(1, subscription.classes_total)) * 100}%`,
                  }}
                />
              </div>

              <Link
                to="/memberships"
                className="text-sm text-coral-600 font-medium hover:text-coral-500"
              >
                Manage subscription &rarr;
              </Link>
            </>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 mb-3">No marketplace subscription</p>
              <Link
                to="/memberships"
                className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-coral-600 hover:bg-coral-700 transition-colors"
              >
                Subscribe now
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-3">
        <Link
          to="/discover"
          className="bg-white rounded-xl border border-gray-200 p-4 text-center hover:shadow-md transition-shadow"
        >
          <div className="text-coral-600 text-2xl mb-1">&#128269;</div>
          <p className="text-sm font-medium text-gray-900">Find Classes</p>
        </Link>
        <Link
          to="/memberships"
          className="bg-white rounded-xl border border-gray-200 p-4 text-center hover:shadow-md transition-shadow"
        >
          <div className="text-coral-600 text-2xl mb-1">&#8693;</div>
          <p className="text-sm font-medium text-gray-900">Manage Plan</p>
        </Link>
        <Link
          to="/qr-code"
          className="bg-white rounded-xl border border-gray-200 p-4 text-center hover:shadow-md transition-shadow"
        >
          <div className="text-coral-600 text-2xl mb-1">&#9641;</div>
          <p className="text-sm font-medium text-gray-900">QR Code</p>
        </Link>
      </div>

      {/* Studio Memberships */}
      {activeMemberships.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Studio Memberships
          </h2>
          <div className="space-y-3">
            {activeMemberships.map((mem) => (
              <div key={mem.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">
                      {mem.plan_name ?? mem.gym_name ?? 'Gym Membership'}
                    </p>
                    <p className="text-sm text-gray-500 capitalize">{mem.membership_tier}</p>
                  </div>
                  <StatusBadge status={mem.status} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Recent Activity
          </h2>
          <Link
            to="/bookings"
            className="text-xs font-medium text-coral-600 hover:text-coral-500"
          >
            View all
          </Link>
        </div>

        {recentActivity.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
            <p className="text-gray-500">No recent activity</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {recentActivity.map((item, i) => (
              <div
                key={`${item.session_id}-${item.attended_at}-${i}`}
                className="px-4 py-3 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">{item.class_name}</p>
                  <p className="text-xs text-gray-500">{item.gym_name ?? item.gym_id}</p>
                </div>
                <p className="text-xs text-gray-500">
                  {new Date(item.attended_at).toLocaleDateString('en-ZA', {
                    day: '2-digit',
                    month: 'short',
                  })}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Wallet;
