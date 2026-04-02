/**
 * Member detail page (Story 12.4).
 *
 * Shows detailed information about a single member including
 * membership status. Attendance and payment history endpoints
 * are not yet available — placeholders shown instead.
 */

import { useParams, Link } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { staffMembershipsGetMemberDetail } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

function formatZar(cents: number): string {
  return `R ${(cents / 100).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short', year: 'numeric' });
}

export function MemberDetail() {
  const { memberId } = useParams<{ memberId: string }>();

  const memberQuery = useQuery({
    queryKey: ['member-detail', memberId],
    queryFn: async () => {
      if (!memberId) return null;
      const result = await staffMembershipsGetMemberDetail({
        path: { membership_id: memberId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return result.data;
    },
    enabled: !!memberId,
  });

  if (memberQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Link to="/members" className="text-sm text-gold-600 hover:text-gold-800">
          &larr; Back to Members
        </Link>
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-600">
          Loading member details...
        </div>
      </div>
    );
  }

  if (memberQuery.error) {
    return (
      <div className="space-y-6">
        <Link to="/members" className="text-sm text-gold-600 hover:text-gold-800">
          &larr; Back to Members
        </Link>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-700">
          Could not load member details. The member may not exist or you may not have access.
        </div>
      </div>
    );
  }

  const data = memberQuery.data as Record<string, unknown> | null;
  if (!data) {
    return (
      <div className="space-y-6">
        <Link to="/members" className="text-sm text-gold-600 hover:text-gold-800">
          &larr; Back to Members
        </Link>
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-500">
          No member data found.
        </div>
      </div>
    );
  }

  // Extract nested objects from the flexible response
  const consumer = (data.consumer as Record<string, unknown>) ?? {};
  const membership = (data.membership as Record<string, unknown>) ?? {};
  const plan = (data.plan as Record<string, unknown>) ?? {};

  const fullName = [consumer.first_name, consumer.last_name].filter(Boolean).join(' ') || 'Unknown';
  const email = (consumer.email as string) ?? '-';
  const phone = (consumer.phone as string) ?? '-';
  const planName = (plan.name as string) ?? 'N/A';
  const status = (membership.status as string) ?? 'unknown';
  const startDate = formatDate(membership.start_date as string | undefined);
  const endDate = formatDate(membership.end_date as string | undefined);
  const priceCents = typeof plan.price_cents === 'number' ? plan.price_cents : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/members" className="text-sm text-gold-600 hover:text-gold-800">
          &larr; Back to Members
        </Link>
      </div>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{fullName}</h1>
            <p className="text-sm text-gray-500 mt-1">{email} | {phone}</p>
          </div>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
              Edit
            </button>
            <button className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700">
              Check In
            </button>
          </div>
        </div>
      </div>

      {/* Membership info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Membership</h2>
          <p className="text-lg font-semibold text-gray-900">{planName}</p>
          <span className={`inline-flex items-center mt-2 px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
            status === 'active' ? 'bg-green-100 text-green-800' :
            status === 'cancelled' ? 'bg-red-100 text-red-800' :
            status === 'frozen' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {status}
          </span>
          <div className="mt-3 text-sm text-gray-500">
            <p>Start: {startDate}</p>
            <p>End: {endDate}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Plan</h2>
          {priceCents !== null ? (
            <>
              <p className="text-3xl font-bold text-gray-900">{formatZar(priceCents)}</p>
              <p className="text-sm text-gray-500 mt-1">per billing cycle</p>
            </>
          ) : (
            <p className="text-sm text-gray-500">No pricing info available</p>
          )}
          {plan.tier && (
            <p className="text-sm text-gray-500 mt-2">Tier: {String(plan.tier)}</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Contact</h2>
          <p className="text-sm text-gray-900">{email}</p>
          <p className="text-sm text-gray-500 mt-1">{phone}</p>
        </div>
      </div>

      {/* Attendance history — coming soon */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Attendance</h2>
        </div>
        <div className="px-6 py-8 text-center text-sm text-gray-500">
          Coming soon — member-specific attendance history is not yet available.
        </div>
      </div>

      {/* Payment history — coming soon */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Payment History</h2>
        </div>
        <div className="px-6 py-8 text-center text-sm text-gray-500">
          Coming soon — member-specific payment history is not yet available.
        </div>
      </div>
    </div>
  );
}
