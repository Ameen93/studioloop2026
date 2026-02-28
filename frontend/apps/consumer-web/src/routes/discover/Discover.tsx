import { useMemo, useState } from 'react';
import { Link } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { marketplaceBrowseMarketplaceClasses } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

const CLASS_TYPES = ['All', 'yoga', 'hiit', 'pilates', 'cycling', 'boxing', 'aqua'];

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('en-ZA', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

function formatPrice(cents: number): string {
  return `R ${(cents / 100).toFixed(2)}`;
}

export function Discover() {
  const [selectedType, setSelectedType] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const classesQuery = useQuery({
    queryKey: ['marketplace-classes', selectedType],
    queryFn: async () => {
      const response = await marketplaceBrowseMarketplaceClasses({
        headers: getAuthHeaders(),
        query: {
          limit: 100,
          class_type: selectedType === 'All' ? null : selectedType,
        },
      });
      return response.data ?? [];
    },
  });

  const filteredClasses = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    const classes = classesQuery.data ?? [];
    return classes.filter((cls) => {
      if (!q) {
        return true;
      }

      return (
        cls.title.toLowerCase().includes(q) ||
        cls.gym_name.toLowerCase().includes(q) ||
        (cls.city ?? '').toLowerCase().includes(q) ||
        (cls.province ?? '').toLowerCase().includes(q)
      );
    });
  }, [classesQuery.data, searchQuery]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Discover Classes</h1>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Search classes, studios, or location..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 text-sm"
        />
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-6 -mx-4 px-4 scrollbar-hide">
        {CLASS_TYPES.map((type) => (
          <button
            key={type}
            onClick={() => setSelectedType(type)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              selectedType === type
                ? 'bg-coral-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {type === 'All' ? type : type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {classesQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading classes...
        </div>
      )}

      {classesQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load classes.
        </div>
      )}

      {filteredClasses.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No classes found matching your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClasses.map((cls) => {
            const spotsRemaining = Math.max(0, cls.capacity - cls.spots_booked);
            return (
              <Link
                key={cls.session_id}
                to={`/discover/${cls.session_id}`}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                <div className="h-2 bg-coral-500" />
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-coral-50 text-coral-700">
                      Class
                    </span>
                    <span className="text-sm font-semibold text-gray-900">
                      {formatPrice(cls.price_cents)}
                    </span>
                  </div>

                  <h3 className="font-semibold text-gray-900 mb-1">{cls.title}</h3>
                  <p className="text-sm text-gray-600">{cls.gym_name}</p>

                  <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                    <span>{formatDate(cls.start_time)}</span>
                    <span>
                      {formatTime(cls.start_time)} - {formatTime(cls.end_time)}
                    </span>
                  </div>

                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                    {[cls.city, cls.province].filter(Boolean).join(', ')}
                  </div>

                  <div className="mt-3 flex items-center justify-between">
                    <span
                      className={`text-xs font-medium ${
                        spotsRemaining === 0
                          ? 'text-red-600'
                          : spotsRemaining <= 3
                            ? 'text-amber-600'
                            : 'text-green-600'
                      }`}
                    >
                      {spotsRemaining === 0 ? 'Full' : `${spotsRemaining} spots left`}
                    </span>
                    <span className="text-xs text-coral-600 font-medium">View details &rarr;</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Discover;
