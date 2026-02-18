/**
 * Memberships screen (Story 13.7).
 *
 * View gym memberships and marketplace subscriptions.
 */

import { useState } from 'react';

type TabType = 'gym' | 'marketplace';

interface GymMembership {
  id: string;
  gym_name: string;
  plan_name: string;
  status: 'active' | 'paused' | 'expired';
  start_date: string;
  next_billing_date: string;
  price_zar: number;
  classes_remaining: number | null;
  classes_total: number | null;
}

interface MarketplaceSubscription {
  id: string;
  plan_name: string;
  status: 'active' | 'cancelled';
  start_date: string;
  next_billing_date: string;
  price_zar: number;
  credits_remaining: number;
  credits_total: number;
}

// Placeholder data
const PLACEHOLDER_GYM_MEMBERSHIPS: GymMembership[] = [
  {
    id: 'mem-1',
    gym_name: 'ZenFit Studio',
    plan_name: 'Unlimited Monthly',
    status: 'active',
    start_date: '2025-12-01',
    next_billing_date: '2026-03-01',
    price_zar: 799,
    classes_remaining: null,
    classes_total: null,
  },
  {
    id: 'mem-2',
    gym_name: 'PowerHouse Gym',
    plan_name: '10 Class Pack',
    status: 'active',
    start_date: '2026-01-15',
    next_billing_date: '2026-04-15',
    price_zar: 950,
    classes_remaining: 6,
    classes_total: 10,
  },
];

const PLACEHOLDER_MARKETPLACE_SUBS: MarketplaceSubscription[] = [
  {
    id: 'sub-1',
    plan_name: 'StudioLoop Explorer',
    status: 'active',
    start_date: '2026-01-01',
    next_billing_date: '2026-03-01',
    price_zar: 499,
    credits_remaining: 3,
    credits_total: 5,
  },
];

function formatDate(dateStr: string): string {
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
    expired: 'bg-gray-100 text-gray-600',
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

  // TODO: Replace with TanStack Query calls
  const gymMemberships = PLACEHOLDER_GYM_MEMBERSHIPS;
  const marketplaceSubs = PLACEHOLDER_MARKETPLACE_SUBS;

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Memberships</h1>

      {/* Tabs */}
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
          Marketplace Subscriptions
        </button>
      </div>

      {/* Gym memberships */}
      {activeTab === 'gym' && (
        <div className="space-y-4">
          {gymMemberships.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No gym memberships yet.</p>
              <p className="text-sm text-gray-400 mt-1">Visit a studio to purchase a membership.</p>
            </div>
          ) : (
            gymMemberships.map((mem) => (
              <div key={mem.id} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{mem.gym_name}</h3>
                    <p className="text-sm text-gray-600">{mem.plan_name}</p>
                  </div>
                  <StatusBadge status={mem.status} />
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-gray-500">Monthly price</p>
                    <p className="font-medium text-gray-900">R {mem.price_zar.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Next billing</p>
                    <p className="font-medium text-gray-900">{formatDate(mem.next_billing_date)}</p>
                  </div>
                  {mem.classes_remaining !== null && (
                    <div>
                      <p className="text-gray-500">Classes remaining</p>
                      <p className="font-medium text-gray-900">
                        {mem.classes_remaining} / {mem.classes_total}
                      </p>
                    </div>
                  )}
                </div>

                {/* Progress bar for class packs */}
                {mem.classes_remaining !== null && mem.classes_total !== null && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-indigo-500 rounded-full h-2 transition-all"
                        style={{
                          width: `${(mem.classes_remaining / mem.classes_total) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Marketplace subscriptions */}
      {activeTab === 'marketplace' && (
        <div className="space-y-4">
          {marketplaceSubs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No marketplace subscriptions.</p>
              <p className="text-sm text-gray-400 mt-1">
                Subscribe to access classes across multiple studios.
              </p>
            </div>
          ) : (
            marketplaceSubs.map((sub) => (
              <div key={sub.id} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{sub.plan_name}</h3>
                    <p className="text-sm text-gray-600">StudioLoop Marketplace</p>
                  </div>
                  <StatusBadge status={sub.status} />
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-gray-500">Monthly price</p>
                    <p className="font-medium text-gray-900">R {sub.price_zar.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Next billing</p>
                    <p className="font-medium text-gray-900">{formatDate(sub.next_billing_date)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Credits remaining</p>
                    <p className="font-medium text-gray-900">
                      {sub.credits_remaining} / {sub.credits_total}
                    </p>
                  </div>
                </div>

                <div className="mt-3">
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-indigo-500 rounded-full h-2 transition-all"
                      style={{
                        width: `${(sub.credits_remaining / sub.credits_total) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default Memberships;
