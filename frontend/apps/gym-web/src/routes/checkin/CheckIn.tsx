import { useState, type FormEvent } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  bookingsManualCheckIn,
  bookingsSearchMembersForCheckIn,
  type SearchResult,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type RecentCheckIn = {
  id: string;
  memberName: string;
  time: string;
};

export function CheckIn() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [checkInError, setCheckInError] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [recentCheckIns, setRecentCheckIns] = useState<RecentCheckIn[]>([]);
  const [checkedInConsumerIds, setCheckedInConsumerIds] = useState<Set<string>>(
    new Set(),
  );

  const searchMutation = useMutation({
    mutationFn: async (q: string) => {
      const response = await bookingsSearchMembersForCheckIn({
        query: { q },
        headers: getAuthHeaders(),
      });
      return response.data ?? [];
    },
    onSuccess: (data) => {
      setSearchError(null);
      setResults(data);
      setHasSearched(true);
    },
    onError: () => {
      setSearchError('Could not search members. Please try again.');
      setResults([]);
      setHasSearched(true);
    },
  });

  const checkInMutation = useMutation({
    mutationFn: async ({ consumerId }: { consumerId: string }) => {
      const response = await bookingsManualCheckIn({
        body: { consumer_id: consumerId },
        headers: getAuthHeaders(),
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      setCheckInError(null);
      const match = results.find((item) => item.consumer_id === variables.consumerId);
      const memberName = match
        ? `${match.first_name} ${match.last_name}`.trim()
        : variables.consumerId;

      setCheckedInConsumerIds((prev) => new Set(prev).add(variables.consumerId));
      setRecentCheckIns((prev) => [
        {
          id: `${variables.consumerId}-${Date.now()}`,
          memberName,
          time: new Date().toLocaleTimeString('en-ZA', {
            hour: '2-digit',
            minute: '2-digit',
          }),
        },
        ...prev,
      ]);
    },
    onError: () => {
      setCheckInError('Check-in failed. Ensure the member has an active membership.');
    },
  });

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) {
      return;
    }
    searchMutation.mutate(q);
  };

  const handleCheckIn = (consumerId: string) => {
    checkInMutation.mutate({ consumerId });
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Member Check-in</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <input
            type="text"
            placeholder="Search by name or phone number..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 px-4 py-3 text-lg border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            autoFocus
          />
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            disabled={searchMutation.isPending}
          >
            {searchMutation.isPending ? 'Searching...' : 'Search'}
          </button>
        </form>

        {searchError && <p className="mt-4 text-sm text-red-600">{searchError}</p>}
        {checkInError && <p className="mt-2 text-sm text-red-600">{checkInError}</p>}

        {hasSearched && (
          <div className="mt-6">
            {results.length === 0 ? (
              <p className="text-sm text-gray-500">No members found for "{query}"</p>
            ) : (
              <div className="space-y-3">
                {results.map((member) => {
                  const fullName = `${member.first_name} ${member.last_name}`.trim();
                  const checkedIn = checkedInConsumerIds.has(member.consumer_id);

                  return (
                    <div
                      key={member.consumer_id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-md"
                    >
                      <div>
                        <p className="font-medium text-gray-900">{fullName}</p>
                        <p className="text-sm text-gray-500">{member.phone ?? 'No phone'}</p>
                      </div>
                      <div>
                        {checkedIn ? (
                          <span className="inline-flex items-center px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-md">
                            Checked In
                          </span>
                        ) : (
                          <button
                            onClick={() => handleCheckIn(member.consumer_id)}
                            className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
                            disabled={checkInMutation.isPending}
                          >
                            Check In
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Recent Check-ins ({recentCheckIns.length})
          </h2>
        </div>
        {recentCheckIns.length === 0 ? (
          <div className="p-6 text-sm text-gray-500">
            No check-ins recorded in this session yet.
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {recentCheckIns.map((ci) => (
                <tr key={ci.id}>
                  <td className="px-6 py-3 text-sm font-medium text-gray-900">
                    {ci.memberName}
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-500">{ci.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
