/**
 * Check-in page (Story 12.6).
 *
 * Allows staff to search for members by phone or name and
 * perform a check-in. Shows recent check-ins for the day.
 */

import { useState, type FormEvent } from 'react';

interface SearchResult {
  id: string;
  full_name: string;
  phone: string;
  membership_plan: string;
  membership_status: 'active' | 'expired' | 'frozen';
  last_check_in: string | null;
}

interface RecentCheckIn {
  id: string;
  member_name: string;
  time: string;
  method: string;
}

const mockSearchResults: SearchResult[] = [
  { id: '1', full_name: 'Thabo Mokoena', phone: '+27 82 123 4567', membership_plan: 'Premium Monthly', membership_status: 'active', last_check_in: '17 Feb 2026, 07:15' },
  { id: '2', full_name: 'Thandi Mokoena', phone: '+27 83 234 5678', membership_plan: 'Basic Monthly', membership_status: 'active', last_check_in: '16 Feb 2026, 08:00' },
];

const mockRecentCheckIns: RecentCheckIn[] = [
  { id: '1', member_name: 'Sarah Khumalo', time: '07:45', method: 'Staff check-in' },
  { id: '2', member_name: 'John Daniels', time: '07:30', method: 'QR scan' },
  { id: '3', member_name: 'David Louw', time: '07:15', method: 'Staff check-in' },
  { id: '4', member_name: 'Amahle Nkosi', time: '06:55', method: 'QR scan' },
  { id: '5', member_name: 'Naledi Phiri', time: '06:30', method: 'Staff check-in' },
];

const statusStyles: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  expired: 'bg-red-100 text-red-800',
  frozen: 'bg-blue-100 text-blue-800',
};

export function CheckIn() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [checkedIn, setCheckedIn] = useState<Set<string>>(new Set());

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Mock search - filter by name or phone
    const filtered = mockSearchResults.filter(
      (m) =>
        m.full_name.toLowerCase().includes(query.toLowerCase()) ||
        m.phone.includes(query),
    );
    setResults(filtered);
    setHasSearched(true);
  };

  const handleCheckIn = (memberId: string) => {
    setCheckedIn((prev) => new Set(prev).add(memberId));
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Member Check-in</h1>

      {/* Search */}
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
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </form>

        {/* Search results */}
        {hasSearched && (
          <div className="mt-6">
            {results.length === 0 ? (
              <p className="text-sm text-gray-500">No members found for "{query}"</p>
            ) : (
              <div className="space-y-3">
                {results.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-md"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{member.full_name}</p>
                      <p className="text-sm text-gray-500">{member.phone}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">{member.membership_plan}</span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize ${statusStyles[member.membership_status]}`}>
                          {member.membership_status}
                        </span>
                      </div>
                      {member.last_check_in && (
                        <p className="text-xs text-gray-400 mt-1">Last check-in: {member.last_check_in}</p>
                      )}
                    </div>
                    <div>
                      {checkedIn.has(member.id) ? (
                        <span className="inline-flex items-center px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-md">
                          Checked In
                        </span>
                      ) : member.membership_status === 'active' ? (
                        <button
                          onClick={() => handleCheckIn(member.id)}
                          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors"
                        >
                          Check In
                        </button>
                      ) : (
                        <span className="inline-flex items-center px-4 py-2 text-sm font-medium text-red-700 bg-red-100 rounded-md">
                          Membership {member.membership_status}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recent check-ins */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Today's Check-ins ({mockRecentCheckIns.length})
          </h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Member</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {mockRecentCheckIns.map((ci) => (
              <tr key={ci.id}>
                <td className="px-6 py-3 text-sm font-medium text-gray-900">{ci.member_name}</td>
                <td className="px-6 py-3 text-sm text-gray-500">{ci.time}</td>
                <td className="px-6 py-3 text-sm text-gray-500">{ci.method}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
