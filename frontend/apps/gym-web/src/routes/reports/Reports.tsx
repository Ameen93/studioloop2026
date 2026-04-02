/**
 * Reports page (Story 12.7).
 *
 * Tabbed report views: Revenue, Attendance, Membership,
 * Class Performance, and Staff reports — all wired to real API endpoints.
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  analyticsRevenueReport,
  analyticsAttendanceReport,
  analyticsMembershipHealthReport,
  analyticsClassPerformanceReport,
  analyticsStaffPerformanceReport,
} from '@sl/api-client';
import { getAuthHeaders, getStoredStaffInfo } from '../../lib/apiAuth';

type ReportTab = 'revenue' | 'attendance' | 'membership' | 'class_performance' | 'staff';

const tabs: { key: ReportTab; label: string }[] = [
  { key: 'revenue', label: 'Revenue' },
  { key: 'attendance', label: 'Attendance' },
  { key: 'membership', label: 'Membership' },
  { key: 'class_performance', label: 'Class Performance' },
  { key: 'staff', label: 'Staff' },
];

function formatZar(cents: number): string {
  return `R ${(cents / 100).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
}

function LoadingState() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-600">
      Loading report data...
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {message}
    </div>
  );
}

function RevenueReport({ gymId }: { gymId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['report-revenue', gymId],
    queryFn: async () => {
      const result = await analyticsRevenueReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message="Could not load revenue report." />;
  if (!data) return <ErrorState message="No revenue data available." />;

  const growthSign = data.growth_percent >= 0 ? '+' : '';

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500">This Period</p>
          <p className="text-2xl font-bold text-gray-900">{formatZar(data.total_revenue_cents)}</p>
          <p className={`text-sm ${data.growth_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {growthSign}{data.growth_percent.toFixed(1)}% vs previous period
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500">Previous Period</p>
          <p className="text-2xl font-bold text-gray-900">{formatZar(data.previous_period_total_cents)}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-500">Period</p>
          <p className="text-lg font-semibold text-gray-900">{data.period}</p>
          <p className="text-xs text-gray-500">{data.start_date} to {data.end_date}</p>
        </div>
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.source_breakdown && (
              <>
                <tr>
                  <td className="px-6 py-3 text-sm text-gray-900">Memberships</td>
                  <td className="px-6 py-3 text-sm text-gray-700 text-right">{formatZar(data.source_breakdown.memberships_cents)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-3 text-sm text-gray-900">Classes</td>
                  <td className="px-6 py-3 text-sm text-gray-700 text-right">{formatZar(data.source_breakdown.classes_cents)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-3 text-sm text-gray-900">Marketplace</td>
                  <td className="px-6 py-3 text-sm text-gray-700 text-right">{formatZar(data.source_breakdown.marketplace_cents)}</td>
                </tr>
              </>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AttendanceReport({ gymId }: { gymId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['report-attendance', gymId],
    queryFn: async () => {
      const result = await analyticsAttendanceReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message="Could not load attendance report." />;
  if (!data) return <ErrorState message="No attendance data available." />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Check-ins', value: data.total_check_ins.toLocaleString() },
          { label: 'Avg Daily', value: data.average_daily_attendance.toFixed(0) },
          { label: 'Avg Weekly', value: data.average_weekly_attendance.toFixed(0) },
          { label: 'Peak Hour', value: data.peak_hour !== null ? `${String(data.peak_hour).padStart(2, '0')}:00` : '-' },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
      {data.by_day_of_week && data.by_day_of_week.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Day</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Check-ins</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.by_day_of_week.map((row, i) => (
                <tr key={i}>
                  <td className="px-6 py-3 text-sm text-gray-900">{row.day ?? row.day_of_week ?? `Day ${i}`}</td>
                  <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.count ?? row.check_ins ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function MembershipReport({ gymId }: { gymId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['report-membership', gymId],
    queryFn: async () => {
      const result = await analyticsMembershipHealthReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message="Could not load membership report." />;
  if (!data) return <ErrorState message="No membership data available." />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Active Members', value: data.total_active_members.toLocaleString() },
          { label: 'New This Period', value: data.new_this_period.toLocaleString() },
          { label: 'Cancelled', value: data.cancelled_this_period.toLocaleString() },
          { label: 'Retention Rate', value: `${data.retention_rate_percent.toFixed(1)}%` },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
      {data.tier_breakdown && data.tier_breakdown.length > 0 && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan / Tier</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Active</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.tier_breakdown.map((row, i) => (
                <tr key={i}>
                  <td className="px-6 py-3 text-sm text-gray-900">{row.tier ?? row.plan_name ?? row.name ?? `Tier ${i + 1}`}</td>
                  <td className="px-6 py-3 text-sm text-gray-700 text-right">{row.count ?? row.active ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="text-sm text-gray-500">
        Churn rate: {data.churn_rate_percent.toFixed(1)}% | Expiring soon: {data.expiring_soon_member_count}
      </div>
    </div>
  );
}

function ClassPerformanceReport({ gymId }: { gymId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['report-class-performance', gymId],
    queryFn: async () => {
      const result = await analyticsClassPerformanceReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message="Could not load class performance report." />;
  if (!data) return <ErrorState message="No class performance data available." />;

  return (
    <div className="space-y-6">
      {data.popular_classes && data.popular_classes.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-500 mb-1">Popular Classes</p>
          <p className="text-sm text-gray-900">{data.popular_classes.join(', ')}</p>
        </div>
      )}
      {data.underperforming_sessions && data.underperforming_sessions.length > 0 && (
        <div className="bg-yellow-50 rounded-lg p-4">
          <p className="text-sm font-medium text-yellow-700 mb-1">Underperforming Sessions</p>
          <p className="text-sm text-yellow-800">{data.underperforming_sessions.join(', ')}</p>
        </div>
      )}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Class</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Bookings</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Capacity</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Fill Rate</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">No-Show Rate</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {(data.items ?? []).map((item) => (
              <tr key={item.session_id}>
                <td className="px-6 py-3 text-sm text-gray-900">{item.class_name}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{item.bookings}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{item.capacity}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{item.fill_rate_percent.toFixed(0)}%</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">{item.no_show_rate_percent.toFixed(0)}%</td>
              </tr>
            ))}
            {(!data.items || data.items.length === 0) && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-sm text-gray-500">
                  No class performance data for this period.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StaffReport({ gymId }: { gymId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['report-staff-performance', gymId],
    queryFn: async () => {
      const result = await analyticsStaffPerformanceReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      // Response is an array directly
      return result.data ?? [];
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message="Could not load staff performance report." />;

  const staffItems = data ?? [];

  return (
    <div className="space-y-6">
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Staff Member</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Classes Taught</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Fill Rate</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Hours Worked</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Est. Earnings</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {staffItems.map((item) => (
              <tr key={item.staff_id}>
                <td className="px-6 py-3 text-sm text-gray-900">{item.full_name}</td>
                <td className="px-6 py-3 text-sm text-gray-500 capitalize">{item.role.replace('_', ' ')}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{item.classes_taught}</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{item.avg_fill_rate_percent.toFixed(0)}%</td>
                <td className="px-6 py-3 text-sm text-gray-700 text-right">{item.total_hours_worked.toFixed(1)}</td>
                <td className="px-6 py-3 text-sm text-gray-500 text-right">
                  {item.estimated_earnings_cents !== null ? formatZar(item.estimated_earnings_cents) : '-'}
                </td>
              </tr>
            ))}
            {staffItems.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">
                  No staff performance data for this period.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function Reports() {
  const [activeTab, setActiveTab] = useState<ReportTab>('revenue');
  const staffInfo = getStoredStaffInfo();
  const gymId = staffInfo?.gym_id ?? null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <button className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors">
          Export CSV
        </button>
      </div>

      {!gymId && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          Missing staff session context. Please sign in again.
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-gold-500 text-gold-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {!gymId ? (
          <div className="text-sm text-gray-500">Sign in to view reports.</div>
        ) : (
          <>
            {activeTab === 'revenue' && <RevenueReport gymId={gymId} />}
            {activeTab === 'attendance' && <AttendanceReport gymId={gymId} />}
            {activeTab === 'membership' && <MembershipReport gymId={gymId} />}
            {activeTab === 'class_performance' && <ClassPerformanceReport gymId={gymId} />}
            {activeTab === 'staff' && <StaffReport gymId={gymId} />}
          </>
        )}
      </div>
    </div>
  );
}
