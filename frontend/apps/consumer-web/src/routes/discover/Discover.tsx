/**
 * Discover classes screen (Story 13.5).
 *
 * Browse marketplace classes with filters for type, date, location, and price.
 */

import { useState } from 'react';
import { Link } from 'react-router';

interface ClassSession {
  id: string;
  name: string;
  gym_name: string;
  instructor_name: string;
  class_type: string;
  start_time: string;
  end_time: string;
  location: string;
  price_zar: number;
  spots_remaining: number;
  total_spots: number;
  image_url?: string;
}

// Placeholder data for development
const PLACEHOLDER_CLASSES: ClassSession[] = [
  {
    id: 'cls-1',
    name: 'Morning Yoga Flow',
    gym_name: 'ZenFit Studio',
    instructor_name: 'Thandi Nkosi',
    class_type: 'Yoga',
    start_time: '2026-02-19T07:00:00',
    end_time: '2026-02-19T08:00:00',
    location: 'Sandton, Johannesburg',
    price_zar: 150,
    spots_remaining: 8,
    total_spots: 20,
  },
  {
    id: 'cls-2',
    name: 'HIIT Blast',
    gym_name: 'PowerHouse Gym',
    instructor_name: 'Sipho Dlamini',
    class_type: 'HIIT',
    start_time: '2026-02-19T17:30:00',
    end_time: '2026-02-19T18:15:00',
    location: 'Rosebank, Johannesburg',
    price_zar: 120,
    spots_remaining: 3,
    total_spots: 15,
  },
  {
    id: 'cls-3',
    name: 'Pilates Reformer',
    gym_name: 'Body Balance',
    instructor_name: 'Lerato Molefe',
    class_type: 'Pilates',
    start_time: '2026-02-20T09:00:00',
    end_time: '2026-02-20T10:00:00',
    location: 'Melrose, Johannesburg',
    price_zar: 200,
    spots_remaining: 5,
    total_spots: 12,
  },
  {
    id: 'cls-4',
    name: 'Spin & Burn',
    gym_name: 'CycleFit',
    instructor_name: 'Kabelo Mokoena',
    class_type: 'Cycling',
    start_time: '2026-02-20T06:00:00',
    end_time: '2026-02-20T06:45:00',
    location: 'Braamfontein, Johannesburg',
    price_zar: 100,
    spots_remaining: 12,
    total_spots: 30,
  },
  {
    id: 'cls-5',
    name: 'Boxing Basics',
    gym_name: 'Fight Club SA',
    instructor_name: 'Nomsa Khumalo',
    class_type: 'Boxing',
    start_time: '2026-02-21T18:00:00',
    end_time: '2026-02-21T19:00:00',
    location: 'Greenside, Johannesburg',
    price_zar: 180,
    spots_remaining: 0,
    total_spots: 16,
  },
  {
    id: 'cls-6',
    name: 'Aqua Aerobics',
    gym_name: 'BluWave Wellness',
    instructor_name: 'Fatima Patel',
    class_type: 'Aqua',
    start_time: '2026-02-21T10:00:00',
    end_time: '2026-02-21T11:00:00',
    location: 'Parkhurst, Johannesburg',
    price_zar: 130,
    spots_remaining: 10,
    total_spots: 20,
  },
];

const CLASS_TYPES = ['All', 'Yoga', 'HIIT', 'Pilates', 'Cycling', 'Boxing', 'Aqua'];

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

function formatPrice(zar: number): string {
  return `R ${zar.toFixed(2)}`;
}

export function Discover() {
  const [selectedType, setSelectedType] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // TODO: Replace with TanStack Query for real API data
  const filteredClasses = PLACEHOLDER_CLASSES.filter((cls) => {
    const matchesType = selectedType === 'All' || cls.class_type === selectedType;
    const matchesSearch =
      !searchQuery ||
      cls.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cls.gym_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cls.instructor_name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Discover Classes</h1>

      {/* Search bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search classes, studios, or instructors..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
        />
      </div>

      {/* Type filter chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-6 -mx-4 px-4 scrollbar-hide">
        {CLASS_TYPES.map((type) => (
          <button
            key={type}
            onClick={() => setSelectedType(type)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              selectedType === type
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Results */}
      {filteredClasses.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No classes found matching your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClasses.map((cls) => (
            <Link
              key={cls.id}
              to={`/discover/${cls.id}`}
              className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Color banner based on type */}
              <div className="h-2 bg-indigo-500" />
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                    {cls.class_type}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {formatPrice(cls.price_zar)}
                  </span>
                </div>

                <h3 className="font-semibold text-gray-900 mb-1">{cls.name}</h3>
                <p className="text-sm text-gray-600">{cls.gym_name}</p>
                <p className="text-sm text-gray-500">with {cls.instructor_name}</p>

                <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                  <span>{formatDate(cls.start_time)}</span>
                  <span>{formatTime(cls.start_time)} - {formatTime(cls.end_time)}</span>
                </div>

                <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                  </svg>
                  {cls.location}
                </div>

                <div className="mt-3 flex items-center justify-between">
                  <span
                    className={`text-xs font-medium ${
                      cls.spots_remaining === 0
                        ? 'text-red-600'
                        : cls.spots_remaining <= 3
                          ? 'text-amber-600'
                          : 'text-green-600'
                    }`}
                  >
                    {cls.spots_remaining === 0
                      ? 'Full'
                      : `${cls.spots_remaining} spots left`}
                  </span>
                  <span className="text-xs text-indigo-600 font-medium">View details &rarr;</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default Discover;
