import { useQuery } from '@tanstack/react-query';
import {
  analyticsGymOwnerDashboard,
  paymentsFailedPaymentActionItems,
  type FailedPaymentActionItem,
} from '@sl/api-client';
import { getAuthHeaders, getStoredStaffInfo } from '../lib/apiAuth';

type DashboardActionItem = {
  id: string;
  type: 'info' | 'warning';
  message: string;
};

function toTitleCase(input: string): string {
  return input
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export function Dashboard() {
  const staffInfo = getStoredStaffInfo();
  const gymId = staffInfo?.gym_id ?? null;

  const dashboardQuery = useQuery({
    queryKey: ['gym-owner-dashboard', gymId],
    queryFn: async () => {
      if (!gymId) {
        return null;
      }

      const result = await analyticsGymOwnerDashboard({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return result.data;
    },
  });

  const failedPaymentsQuery = useQuery({
    queryKey: ['failed-payment-items', gymId],
    queryFn: async () => {
      if (!gymId) {
        return [] as FailedPaymentActionItem[];
      }

      const result = await paymentsFailedPaymentActionItems({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return result.data ?? [];
    },
  });

  const dashboardData = dashboardQuery.data;
  const summary = dashboardData?.today_summary ?? {};
  const quickMetrics = dashboardData?.quick_metrics ?? {};
  const actionItems = dashboardData?.action_items ?? {};

  const mappedActionItems: DashboardActionItem[] = [
    ...Object.entries(actionItems).map(([key, value], index) => ({
      id: `${key}-${index}`,
      type: value > 0 ? ('warning' as const) : ('info' as const),
      message: `${toTitleCase(key)}: ${value}`,
    })),
    ...(failedPaymentsQuery.data ?? []).map((item) => ({
      id: item.payment_id,
      type: 'warning' as const,
      message: `Failed payment: ${item.member_name}${item.failure_reason ? ` (${item.failure_reason})` : ''}`,
    })),
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">
          {new Date().toLocaleDateString('en-ZA', {
            weekday: 'long',
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          })}
        </p>
      </div>

      {!gymId && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          Missing staff session context. Please sign in again.
        </div>
      )}

      {(dashboardQuery.isLoading || failedPaymentsQuery.isLoading) && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading dashboard data...
        </div>
      )}

      {(dashboardQuery.error || failedPaymentsQuery.error) && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load full dashboard data.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-500">Total Revenue</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {quickMetrics.total_revenue ?? 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-500">Today Check-ins</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {summary.today_check_ins ?? 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-500">Today Bookings</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {summary.today_bookings ?? 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm font-medium text-gray-500">Active Members</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {quickMetrics.active_memberships ?? 0}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Action Items</h2>
        </div>
        {mappedActionItems.length === 0 ? (
          <div className="p-6 text-sm text-gray-500">No current action items.</div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {mappedActionItems.map((item) => (
              <li key={item.id} className="px-6 py-4 flex items-center gap-3">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    item.type === 'warning'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {item.type}
                </span>
                <span className="text-sm text-gray-900">{item.message}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
