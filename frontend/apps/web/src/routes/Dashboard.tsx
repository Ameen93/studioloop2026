import { useQuery } from '@tanstack/react-query';
import { adminPlatformHealth } from '@sl/api-client';
import { getAuthHeaders } from '../lib/apiAuth';

interface MetricCardProps {
  label: string;
  value: string | number;
  color?: string;
}

function MetricCard({ label, value, color = 'text-gray-900' }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${color}`}>{value}</p>
    </div>
  );
}

export function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['adminPlatformHealth'],
    queryFn: async () => {
      const response = await adminPlatformHealth({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-24 mb-3" />
              <div className="h-8 bg-gray-200 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-sm text-red-700">
            Failed to load platform health data. Please try again.
          </p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">
          Last updated: {new Date(data.timestamp).toLocaleString('en-ZA', { timeZone: 'Africa/Johannesburg' })}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard label="Total Gyms" value={data.total_gyms} />
        <MetricCard label="Active Gyms" value={data.active_gyms} color="text-green-700" />
        <MetricCard label="Inactive Gyms" value={data.inactive_gyms} color="text-red-700" />
        <MetricCard label="Total Consumers" value={data.total_consumers} />
        <MetricCard label="Total Staff" value={data.total_staff} />
        <MetricCard label="Total Bookings" value={data.total_bookings} />
        <MetricCard label="Active Subscriptions" value={data.active_marketplace_subscriptions} />
        <MetricCard label="Open Complaints" value={data.open_complaints} color={data.open_complaints > 0 ? 'text-orange-600' : 'text-gray-900'} />
        <MetricCard label="Completed Payments" value={data.total_payments_completed} />
      </div>
    </div>
  );
}
