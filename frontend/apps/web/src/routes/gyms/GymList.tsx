import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import {
  adminListGyms,
  adminApproveGym,
  adminRejectGym,
  adminSuspendGym,
  adminReactivateGym,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type FilterStatus = 'all' | 'active' | 'inactive';

const PAGE_SIZE = 20;

export function GymList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [page, setPage] = useState(0);

  const isActiveFilter = filterStatus === 'all' ? undefined : filterStatus === 'active';

  const { data, isLoading, error } = useQuery({
    queryKey: ['adminListGyms', { search, isActiveFilter, page }],
    queryFn: async () => {
      const response = await adminListGyms({
        query: {
          skip: page * PAGE_SIZE,
          limit: PAGE_SIZE,
          search: search || undefined,
          is_active: isActiveFilter ?? null,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const invalidateGyms = () => {
    queryClient.invalidateQueries({ queryKey: ['adminListGyms'] });
  };

  const approveMutation = useMutation({
    mutationFn: async (gymId: string) => {
      await adminApproveGym({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: invalidateGyms,
  });

  const rejectMutation = useMutation({
    mutationFn: async ({ gymId, reason }: { gymId: string; reason: string }) => {
      await adminRejectGym({
        path: { gym_id: gymId },
        query: { reason },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: invalidateGyms,
  });

  const suspendMutation = useMutation({
    mutationFn: async ({ gymId, reason }: { gymId: string; reason: string }) => {
      await adminSuspendGym({
        path: { gym_id: gymId },
        query: { reason },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: invalidateGyms,
  });

  const reactivateMutation = useMutation({
    mutationFn: async (gymId: string) => {
      await adminReactivateGym({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: invalidateGyms,
  });

  const handleApprove = (gymId: string) => {
    if (window.confirm('Approve this gym?')) {
      approveMutation.mutate(gymId);
    }
  };

  const handleReject = (gymId: string) => {
    const reason = window.prompt('Enter rejection reason:');
    if (reason) {
      rejectMutation.mutate({ gymId, reason });
    }
  };

  const handleSuspend = (gymId: string) => {
    const reason = window.prompt('Enter suspension reason:');
    if (reason) {
      suspendMutation.mutate({ gymId, reason });
    }
  };

  const handleReactivate = (gymId: string) => {
    if (window.confirm('Reactivate this gym?')) {
      reactivateMutation.mutate(gymId);
    }
  };

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  const filterChips: { label: string; value: FilterStatus }[] = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Gyms</h1>

      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <input
          type="text"
          placeholder="Search gyms..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm w-full sm:w-72"
        />
        <div className="flex gap-2">
          {filterChips.map((chip) => (
            <button
              key={chip.value}
              onClick={() => {
                setFilterStatus(chip.value);
                setPage(0);
              }}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                filterStatus === chip.value
                  ? 'bg-gray-700 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700">Failed to load gyms. Please try again.</p>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <p className="text-gray-500">Loading gyms...</p>
        </div>
      )}

      {/* Table */}
      {data && (
        <>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Province
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tier
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Marketplace
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.items.map((gym) => (
                    <tr
                      key={gym.id}
                      onClick={() => navigate(`/gyms/${gym.id}`)}
                      className="hover:bg-gray-50 cursor-pointer"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{gym.name}</div>
                        <div className="text-xs text-gray-500">{gym.slug}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {gym.province || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                          {gym.subscription_tier}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            gym.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {gym.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {gym.is_marketplace_enabled ? 'Yes' : 'No'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(gym.created_at).toLocaleDateString('en-ZA')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <div className="flex justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                          {!gym.is_active && (
                            <>
                              <button
                                onClick={() => handleApprove(gym.id)}
                                disabled={approveMutation.isPending}
                                className="px-2 py-1 text-xs font-medium rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleReject(gym.id)}
                                disabled={rejectMutation.isPending}
                                className="px-2 py-1 text-xs font-medium rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
                              >
                                Reject
                              </button>
                              <button
                                onClick={() => handleReactivate(gym.id)}
                                disabled={reactivateMutation.isPending}
                                className="px-2 py-1 text-xs font-medium rounded bg-gray-700 text-white hover:bg-gray-800 disabled:opacity-50"
                              >
                                Reactivate
                              </button>
                            </>
                          )}
                          {gym.is_active && (
                            <button
                              onClick={() => handleSuspend(gym.id)}
                              disabled={suspendMutation.isPending}
                              className="px-2 py-1 text-xs font-medium rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
                            >
                              Suspend
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {data.items.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-sm text-gray-500">
                        No gyms found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Showing {data.skip + 1} to {Math.min(data.skip + data.limit, data.total)} of{' '}
                {data.total} gyms
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
