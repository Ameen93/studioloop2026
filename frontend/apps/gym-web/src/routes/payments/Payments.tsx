import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  paymentsFailedPaymentActionItems,
  paymentsGymPaymentDashboard,
  paymentsMarketplacePayoutReport,
  type PaymentItem,
} from '@sl/api-client';
import { getAuthHeaders, getStoredStaffInfo } from '../../lib/apiAuth';

type PaymentTab = 'all' | 'failed' | 'payouts';

const statusStyles: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  failed_permanent: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  refunded: 'bg-gray-100 text-gray-800',
};

function formatCents(amount: number): string {
  return `R ${(amount / 100).toFixed(2)}`;
}

function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return Number.isNaN(date.getTime()) ? isoString : date.toLocaleString('en-ZA');
}

export function Payments() {
  const [activeTab, setActiveTab] = useState<PaymentTab>('all');
  const gymId = getStoredStaffInfo()?.gym_id ?? null;

  const dashboardQuery = useQuery({
    queryKey: ['payments-dashboard', gymId],
    queryFn: async () => {
      if (!gymId) {
        return null;
      }

      const response = await paymentsGymPaymentDashboard({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return response.data;
    },
  });

  const failedItemsQuery = useQuery({
    queryKey: ['payments-failed-items', gymId],
    queryFn: async () => {
      if (!gymId) {
        return [];
      }

      const response = await paymentsFailedPaymentActionItems({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return response.data ?? [];
    },
  });

  const payoutsQuery = useQuery({
    queryKey: ['payments-payout-report', gymId],
    queryFn: async () => {
      if (!gymId) {
        return null;
      }

      const response = await paymentsMarketplacePayoutReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return response.data;
    },
  });

  const payments = dashboardQuery.data?.items ?? [];
  const failedActionItems = failedItemsQuery.data ?? [];
  const failedPayments = payments.filter(
    (payment) => payment.status === 'failed' || payment.status === 'failed_permanent',
  );
  const displayPayments: PaymentItem[] =
    activeTab === 'failed' ? failedPayments : payments;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
      </div>

      {!gymId && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          Missing staff session context. Please sign in again.
        </div>
      )}

      {(dashboardQuery.isLoading || failedItemsQuery.isLoading || payoutsQuery.isLoading) && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading payment data...
        </div>
      )}

      {(dashboardQuery.error || failedItemsQuery.error || payoutsQuery.error) && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load all payment data.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Received</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatCents(dashboardQuery.data?.summary.total_received_cents ?? 0)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Pending</p>
          <p className="text-2xl font-bold text-yellow-700">
            {formatCents(dashboardQuery.data?.summary.total_pending_cents ?? 0)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Failed</p>
          <p className="text-2xl font-bold text-red-600">
            {formatCents(dashboardQuery.data?.summary.total_failed_cents ?? 0)}
          </p>
          <p className="text-xs text-red-500">{failedActionItems.length} action item(s)</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Marketplace Net Payout</p>
          <p className="text-2xl font-bold text-blue-600">
            {formatCents(payoutsQuery.data?.net_payout_cents ?? 0)}
          </p>
          <p className="text-xs text-gray-500">{payoutsQuery.data?.payout_schedule ?? '-'}</p>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          {[
            { key: 'all' as PaymentTab, label: 'All Payments' },
            { key: 'failed' as PaymentTab, label: `Failed (${failedPayments.length})` },
            { key: 'payouts' as PaymentTab, label: 'Marketplace Payouts' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {activeTab !== 'payouts' ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Payment ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Member
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {displayPayments.map((payment) => (
                <tr key={payment.payment_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-700">{payment.payment_id}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {payment.member_name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700 text-right">
                    {formatCents(payment.amount_cents)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700 capitalize">
                    {payment.payment_type.replaceAll('_', ' ')}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                        statusStyles[payment.status] ?? 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {payment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(payment.created_at)}
                  </td>
                </tr>
              ))}
              {displayPayments.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">
                    No payments found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Payout Breakdown</h2>
          </div>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Class
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Bookings
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Gross Revenue
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {(payoutsQuery.data?.class_breakdown ?? []).map((item) => (
                <tr key={item.class_name} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.class_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-700 text-right">{item.bookings}</td>
                  <td className="px-6 py-4 text-sm text-gray-700 text-right">
                    {formatCents(item.gross_revenue_cents)}
                  </td>
                </tr>
              ))}
              {(payoutsQuery.data?.class_breakdown ?? []).length === 0 && (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                    No marketplace payout breakdown available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
