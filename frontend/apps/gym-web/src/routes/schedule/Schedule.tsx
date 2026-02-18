/**
 * Class scheduling page (Story 12.5).
 *
 * Displays a weekly calendar view of class sessions with day/week toggle.
 * Shows class details including instructor, time, and booking status.
 */

import { useState } from 'react';

interface ClassSession {
  id: string;
  name: string;
  instructor: string;
  time: string;
  duration: string;
  booked: number;
  capacity: number;
  space: string;
}

type DayOfWeek = 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun';

const mockSchedule: Record<DayOfWeek, ClassSession[]> = {
  Mon: [
    { id: '1', name: 'Morning HIIT', instructor: 'Coach Sipho', time: '06:00', duration: '45 min', booked: 18, capacity: 20, space: 'Studio A' },
    { id: '2', name: 'Yoga Flow', instructor: 'Lerato M.', time: '08:00', duration: '60 min', booked: 12, capacity: 15, space: 'Studio B' },
    { id: '3', name: 'Spin Class', instructor: 'Coach David', time: '12:00', duration: '45 min', booked: 22, capacity: 25, space: 'Spin Room' },
    { id: '4', name: 'Pilates', instructor: 'Zanele K.', time: '17:00', duration: '50 min', booked: 8, capacity: 12, space: 'Studio B' },
  ],
  Tue: [
    { id: '5', name: 'CrossFit', instructor: 'Coach Sipho', time: '06:00', duration: '60 min', booked: 15, capacity: 20, space: 'Main Floor' },
    { id: '6', name: 'Barre', instructor: 'Lerato M.', time: '09:00', duration: '45 min', booked: 10, capacity: 12, space: 'Studio A' },
    { id: '7', name: 'Boxing Fitness', instructor: 'Coach David', time: '17:30', duration: '45 min', booked: 16, capacity: 20, space: 'Studio A' },
  ],
  Wed: [
    { id: '8', name: 'Morning HIIT', instructor: 'Coach Sipho', time: '06:00', duration: '45 min', booked: 17, capacity: 20, space: 'Studio A' },
    { id: '9', name: 'Yoga Flow', instructor: 'Lerato M.', time: '08:00', duration: '60 min', booked: 14, capacity: 15, space: 'Studio B' },
    { id: '10', name: 'Spin Class', instructor: 'Coach David', time: '12:00', duration: '45 min', booked: 20, capacity: 25, space: 'Spin Room' },
  ],
  Thu: [
    { id: '11', name: 'CrossFit', instructor: 'Coach Sipho', time: '06:00', duration: '60 min', booked: 14, capacity: 20, space: 'Main Floor' },
    { id: '12', name: 'Pilates', instructor: 'Zanele K.', time: '09:00', duration: '50 min', booked: 11, capacity: 12, space: 'Studio B' },
    { id: '13', name: 'Boxing Fitness', instructor: 'Coach David', time: '17:30', duration: '45 min', booked: 18, capacity: 20, space: 'Studio A' },
  ],
  Fri: [
    { id: '14', name: 'Morning HIIT', instructor: 'Coach Sipho', time: '06:00', duration: '45 min', booked: 16, capacity: 20, space: 'Studio A' },
    { id: '15', name: 'Yoga Flow', instructor: 'Lerato M.', time: '08:00', duration: '60 min', booked: 13, capacity: 15, space: 'Studio B' },
  ],
  Sat: [
    { id: '16', name: 'Weekend Bootcamp', instructor: 'Coach Sipho', time: '08:00', duration: '60 min', booked: 22, capacity: 30, space: 'Main Floor' },
    { id: '17', name: 'Gentle Yoga', instructor: 'Lerato M.', time: '10:00', duration: '60 min', booked: 10, capacity: 15, space: 'Studio B' },
  ],
  Sun: [
    { id: '18', name: 'Recovery Stretch', instructor: 'Zanele K.', time: '09:00', duration: '45 min', booked: 8, capacity: 15, space: 'Studio B' },
  ],
};

const days: DayOfWeek[] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function Schedule() {
  const [view, setView] = useState<'week' | 'day'>('week');
  const [selectedDay, setSelectedDay] = useState<DayOfWeek>('Mon');

  const visibleDays = view === 'week' ? days : [selectedDay];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Class Schedule</h1>
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors">
            Add Class
          </button>
          <div className="flex rounded-md shadow-sm">
            <button
              onClick={() => setView('week')}
              className={`px-3 py-1.5 text-sm font-medium rounded-l-md border ${
                view === 'week'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Week
            </button>
            <button
              onClick={() => setView('day')}
              className={`px-3 py-1.5 text-sm font-medium rounded-r-md border-t border-r border-b ${
                view === 'day'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Day
            </button>
          </div>
        </div>
      </div>

      {view === 'day' && (
        <div className="flex gap-2">
          {days.map((day) => (
            <button
              key={day}
              onClick={() => setSelectedDay(day)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                selectedDay === day
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {day}
            </button>
          ))}
        </div>
      )}

      <div className={`grid gap-6 ${view === 'week' ? 'grid-cols-1 lg:grid-cols-7' : 'grid-cols-1 max-w-xl'}`}>
        {visibleDays.map((day) => (
          <div key={day} className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <h3 className="text-sm font-semibold text-gray-900">{day}</h3>
            </div>
            <div className="p-2 space-y-2">
              {(mockSchedule[day] || []).map((cls) => {
                const utilization = cls.booked / cls.capacity;
                return (
                  <div
                    key={cls.id}
                    className={`p-3 rounded-md border text-sm ${
                      utilization >= 0.9
                        ? 'border-red-200 bg-red-50'
                        : utilization >= 0.7
                          ? 'border-yellow-200 bg-yellow-50'
                          : 'border-gray-200 bg-white'
                    }`}
                  >
                    <p className="font-medium text-gray-900">{cls.name}</p>
                    <p className="text-xs text-gray-500">{cls.time} | {cls.duration}</p>
                    <p className="text-xs text-gray-500">{cls.instructor}</p>
                    <p className="text-xs text-gray-500">{cls.space}</p>
                    <p className="text-xs mt-1 font-medium">
                      <span className={utilization >= 0.9 ? 'text-red-600' : 'text-gray-600'}>
                        {cls.booked}/{cls.capacity} booked
                      </span>
                    </p>
                  </div>
                );
              })}
              {(!mockSchedule[day] || mockSchedule[day].length === 0) && (
                <p className="text-xs text-gray-400 p-3 text-center">No classes</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
