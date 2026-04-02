import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  adminListComplaints,
  adminCreateComplaint,
  adminUpdateComplaint,
} from '@sl/api-client';
import type { ComplaintPublic, ComplaintStatus } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type FilterStatus = 'all' | ComplaintStatus;

const PAGE_SIZE = 20;

const STATUS_OPTIONS: { label: string; value: FilterStatus }[] = [
  { label: 'All', value: 'all' },
  { label: 'Open', value: 'open' },
  { label: 'Assigned', value: 'assigned' },
  { label: 'Resolved', value: 'resolved' },
  { label: 'Closed', value: 'closed' },
];

function ComplaintDetailPanel({
  complaint,
  onClose,
}: {
  complaint: ComplaintPublic;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<ComplaintStatus>(complaint.status);
  const [assignedTo, setAssignedTo] = useState(complaint.assigned_to || '');
  const [resolution, setResolution] = useState(complaint.resolution || '');
  const [note, setNote] = useState('');

  const [assignError, setAssignError] = useState('');
  const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  const updateMutation = useMutation({
    mutationFn: async () => {
      // Validate assigned_to is a valid UUID if provided (backend requires UUID FK)
      if (assignedTo && !UUID_RE.test(assignedTo)) {
        throw new Error('Assigned To must be a valid user UUID');
      }
      setAssignError('');
      await adminUpdateComplaint({
        path: { complaint_id: complaint.id },
        body: {
          status: status !== complaint.status ? status : null,
          assigned_to: assignedTo || null,
          resolution: resolution || null,
          note: note || null,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminListComplaints'] });
      onClose();
    },
    onError: (err: Error) => {
      if (err.message.includes('UUID')) {
        setAssignError(err.message);
      }
    },
  });

  return (
    <tr>
      <td colSpan={5} className="px-6 py-4 bg-gray-50">
        <div className="space-y-4 max-w-2xl">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Complaint Details</h3>
            <button
              onClick={onClose}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>

          <div className="text-sm text-gray-700">
            <p className="font-medium">Description:</p>
            <p className="mt-1">{complaint.description}</p>
          </div>

          {complaint.notes && complaint.notes.length > 0 && (
            <div className="text-sm">
              <p className="font-medium text-gray-700">Notes:</p>
              <ul className="mt-1 space-y-1">
                {complaint.notes.map((n, i) => (
                  <li key={i} className="text-gray-600 bg-white rounded p-2 border border-gray-200">
                    {JSON.stringify(n)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as ComplaintStatus)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
              >
                <option value="open">Open</option>
                <option value="assigned">Assigned</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Assigned To (Admin UUID)</label>
              <input
                type="text"
                value={assignedTo}
                onChange={(e) => { setAssignedTo(e.target.value); setAssignError(''); }}
                placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm font-mono ${assignError ? 'border-red-300' : 'border-gray-300'}`}
              />
              {assignError && <p className="mt-1 text-xs text-red-600">{assignError}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Resolution</label>
            <textarea
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              rows={2}
              placeholder="Describe the resolution..."
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Add Note</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              placeholder="Add a note..."
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => updateMutation.mutate()}
              disabled={updateMutation.isPending}
              className="px-4 py-2 text-sm font-medium rounded-md bg-gray-700 text-white hover:bg-gray-800 disabled:opacity-50"
            >
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>

          {updateMutation.isError && (
            <p className="text-sm text-red-600">Failed to update complaint. Please try again.</p>
          )}
        </div>
      </td>
    </tr>
  );
}

export function ComplaintList() {
  const queryClient = useQueryClient();
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [page, setPage] = useState(0);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newConsumerId, setNewConsumerId] = useState('');
  const [newDescription, setNewDescription] = useState('');

  const statusFilter = filterStatus === 'all' ? undefined : filterStatus;

  const { data, isLoading, error } = useQuery({
    queryKey: ['adminListComplaints', { statusFilter, page }],
    queryFn: async () => {
      const response = await adminListComplaints({
        query: {
          skip: page * PAGE_SIZE,
          limit: PAGE_SIZE,
          status: statusFilter ?? null,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      await adminCreateComplaint({
        body: {
          consumer_id: newConsumerId,
          description: newDescription,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminListComplaints'] });
      setShowCreateForm(false);
      setNewConsumerId('');
      setNewDescription('');
    },
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  const statusColor = (status: ComplaintStatus) => {
    switch (status) {
      case 'open':
        return 'bg-yellow-100 text-yellow-800';
      case 'assigned':
        return 'bg-blue-100 text-blue-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Complaints</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 text-sm font-medium rounded-md bg-gray-700 text-white hover:bg-gray-800"
        >
          {showCreateForm ? 'Cancel' : 'Create Complaint'}
        </button>
      </div>

      {/* Create form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">New Complaint</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Consumer ID</label>
              <input
                type="text"
                value={newConsumerId}
                onChange={(e) => setNewConsumerId(e.target.value)}
                placeholder="UUID of the consumer"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              rows={3}
              placeholder="Describe the complaint..."
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gray-500 focus:border-gray-500 sm:text-sm"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => createMutation.mutate()}
              disabled={createMutation.isPending || !newConsumerId || !newDescription}
              className="px-4 py-2 text-sm font-medium rounded-md bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </button>
            <button
              onClick={() => {
                setShowCreateForm(false);
                setNewConsumerId('');
                setNewDescription('');
              }}
              className="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
          {createMutation.isError && (
            <p className="text-sm text-red-600">Failed to create complaint. Please try again.</p>
          )}
        </div>
      )}

      {/* Filter chips */}
      <div className="flex gap-2">
        {STATUS_OPTIONS.map((chip) => (
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

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700">Failed to load complaints. Please try again.</p>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <p className="text-gray-500">Loading complaints...</p>
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
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Consumer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.items.map((complaint) => (
                    <>
                      <tr
                        key={complaint.id}
                        onClick={() =>
                          setExpandedId(expandedId === complaint.id ? null : complaint.id)
                        }
                        className="hover:bg-gray-50 cursor-pointer"
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                          {complaint.id.slice(0, 8)}...
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                          {complaint.consumer_id.slice(0, 8)}...
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                          {complaint.description}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusColor(complaint.status)}`}
                          >
                            {complaint.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(complaint.created_at).toLocaleDateString('en-ZA')}
                        </td>
                      </tr>
                      {expandedId === complaint.id && (
                        <ComplaintDetailPanel
                          key={`detail-${complaint.id}`}
                          complaint={complaint}
                          onClose={() => setExpandedId(null)}
                        />
                      )}
                    </>
                  ))}
                  {data.items.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-sm text-gray-500">
                        No complaints found.
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
                {data.total} complaints
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
