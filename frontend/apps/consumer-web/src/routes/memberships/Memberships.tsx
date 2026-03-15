import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  marketplaceViewMarketplaceSubscriptionStatus,
  staffMembershipsListConsumerMemberships,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type TabType = 'gym' | 'marketplace';

function formatDate(dateStr: string | null): string {
  if (!dateStr) {
    return '-';
  }

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

export function Memberships() {
  const [activeTab, setActiveTab] = useState<TabType>('gym');

  const gymMembershipsQuery = useQuery({
    queryKey: ['consumer-gym-memberships'],
    queryFn: async () => {
      const response = await staffMembershipsListConsumerMemberships({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const marketplaceSubscriptionQuery = useQuery({
    queryKey: ['consumer-marketplace-subscription'],
    queryFn: async () => {
      const response = await marketplaceViewMarketplaceSubscriptionStatus({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? null;
    },
  });

  const gymMemberships = gymMembershipsQuery.data ?? [];
  const marketplaceSubscription = marketplaceSubscriptionQuery.data;

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Memberships</h1>

      <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl mb-6">
        <button
          onClick={() => setActiveTab('gym')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'gym'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Gym Memberships
        </button>
        <button
          onClick={() => setActiveTab('marketplace')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'marketplace'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Marketplace Subscription
        </button>
      </div>

      {(gymMembershipsQuery.isLoading || marketplaceSubscriptionQuery.isLoading) && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading memberships...
        </div>
      )}

      {(gymMembershipsQuery.error || marketplaceSubscriptionQuery.error) && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load all membership data.
        </div>
      )}

      {activeTab === 'gym' && (
        <div className="space-y-4">
          {gymMemberships.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No gym memberships yet.</p>
            </div>
          ) : (
            gymMemberships.map((mem) => (
              <div key={mem.id} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{mem.plan_name ?? 'Gym Membership'}</h3>
                    <p className="text-sm text-gray-600 capitalize">{mem.membership_tier}</p>
                  </div>
                  <StatusBadge status={mem.status} />
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-gray-500">Gym</p>
                    <p className="font-medium text-gray-900">{mem.gym_name ?? 'Unknown gym'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Tier</p>
                    <p className="font-medium text-gray-900 capitalize">{mem.membership_tier}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Payment Method</p>
                    <p className="font-medium text-gray-900">{mem.payment_method_last4 ? `•••• ${mem.payment_method_last4}` : '-'}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'marketplace' && (
        <div className="space-y-4">
          {!marketplaceSubscription ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No marketplace subscription.</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900 capitalize">
                    {marketplaceSubscription.plan_tier} plan
                  </h3>
                  <p className="text-sm text-gray-600">StudioLoop Marketplace</p>
                </div>
                <StatusBadge status={marketplaceSubscription.status} />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-gray-500">Classes Remaining</p>
                  <p className="font-medium text-gray-900">
                    {marketplaceSubscription.classes_remaining} / {marketplaceSubscription.classes_total}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Reset Date</p>
                  <p className="font-medium text-gray-900">
                    {formatDate(marketplaceSubscription.reset_at)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Status</p>
                  <p className="font-medium text-gray-900 capitalize">
                    {marketplaceSubscription.status}
                  </p>
                </div>
              </div>

              <div className="mt-3">
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="bg-coral-500 rounded-full h-2 transition-all"
                    style={{
                      width: `${(marketplaceSubscription.classes_remaining / Math.max(1, marketplaceSubscription.classes_total)) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Memberships;
