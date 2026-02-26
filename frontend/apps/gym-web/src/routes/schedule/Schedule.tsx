import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAuthHeaders } from '../../lib/apiAuth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

type CalendarSession = {
  id: string;
  space_id: string;
  instructor_staff_id: string | null;
  title: string;
  class_type: string | null;
  start_time: string;
  end_time: string;
  status: string;
  capacity: number;
  spots_booked: number;
  price_cents: number;
  approval_status: string;
  color: string | null;
};

type CalendarDayGroup = {
  date: string;
  sessions: CalendarSession[];
};

type ClassTemplate = {
  id: string;
  name: string;
  class_type: string;
  color: string;
};

const CLASS_TYPE_COLORS: Record<string, string> = {
  yoga: '#10B981',
  pilates: '#EC4899',
  hiit: '#EF4444',
  crossfit: '#F97316',
  cycling: '#06B6D4',
  boxing: '#DC2626',
  strength: '#8B5CF6',
  swimming: '#3B82F6',
  dance: '#F59E0B',
  martial_arts: '#6366F1',
  other: '#6B7280',
};

function getMonday(d: Date): Date {
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(d);
  monday.setDate(diff);
  monday.setHours(0, 0, 0, 0);
  return monday;
}

function addDays(d: Date, n: number): Date {
  const result = new Date(d);
  result.setDate(result.getDate() + n);
  return result;
}

function formatDate(d: Date): string {
  return d.toISOString().split('T')[0];
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' });
}

function formatShortDate(d: Date): string {
  return d.toLocaleDateString('en-ZA', { weekday: 'short', day: 'numeric', month: 'short' });
}

function formatPrice(cents: number): string {
  if (cents === 0) return 'Free';
  return `R ${(cents / 100).toFixed(2)}`;
}

export function Schedule() {
  const [weekStart, setWeekStart] = useState(() => getMonday(new Date()));
  const [selectedSession, setSelectedSession] = useState<CalendarSession | null>(null);
  const [filterClassType, setFilterClassType] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');

  const weekEnd = useMemo(() => addDays(weekStart, 6), [weekStart]);
  const weekDays = useMemo(
    () => Array.from({ length: 7 }, (_, i) => addDays(weekStart, i)),
    [weekStart],
  );

  const calendarQuery = useQuery({
    queryKey: ['class-calendar', formatDate(weekStart), formatDate(weekEnd), filterClassType, filterStatus],
    queryFn: async () => {
      const params = new URLSearchParams({
        start_date: formatDate(weekStart),
        end_date: formatDate(weekEnd),
      });
      if (filterClassType) params.set('class_type', filterClassType);
      if (filterStatus) params.set('status', filterStatus);

      const resp = await fetch(`${API_BASE}/api/v1/gyms/me/class_sessions/calendar?${params}`, {
        headers: getAuthHeaders(),
      });
      if (!resp.ok) throw new Error('Failed to fetch calendar');
      return (await resp.json()) as CalendarDayGroup[];
    },
  });

  const templatesQuery = useQuery({
    queryKey: ['class-templates'],
    queryFn: async () => {
      const resp = await fetch(`${API_BASE}/api/v1/gyms/me/class_templates`, {
        headers: getAuthHeaders(),
      });
      if (!resp.ok) throw new Error('Failed to fetch templates');
      return (await resp.json()) as ClassTemplate[];
    },
  });

  const sessionsByDate = useMemo(() => {
    const map: Record<string, CalendarSession[]> = {};
    for (const group of calendarQuery.data ?? []) {
      map[group.date] = group.sessions;
    }
    return map;
  }, [calendarQuery.data]);

  const templateColorMap = useMemo(() => {
    const map: Record<string, string> = {};
    for (const t of templatesQuery.data ?? []) {
      map[t.id] = t.color;
    }
    return map;
  }, [templatesQuery.data]);

  function getSessionColor(s: CalendarSession): string {
    if (s.color) return s.color;
    if (s.class_type && CLASS_TYPE_COLORS[s.class_type]) return CLASS_TYPE_COLORS[s.class_type];
    return '#3B82F6';
  }

  function prevWeek() {
    setWeekStart((w) => addDays(w, -7));
  }

  function nextWeek() {
    setWeekStart((w) => addDays(w, 7));
  }

  function goToday() {
    setWeekStart(getMonday(new Date()));
  }

  const isToday = (d: Date) => formatDate(d) === formatDate(new Date());

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Class Schedule</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={prevWeek}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Prev
          </button>
          <button
            onClick={goToday}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Today
          </button>
          <button
            onClick={nextWeek}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>

      {/* Week range display */}
      <p className="text-sm text-gray-500">
        {formatShortDate(weekStart)} &mdash; {formatShortDate(weekEnd)}
      </p>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={filterClassType}
          onChange={(e) => setFilterClassType(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700"
        >
          <option value="">All class types</option>
          {Object.keys(CLASS_TYPE_COLORS).map((ct) => (
            <option key={ct} value={ct}>
              {ct.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
            </option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700"
        >
          <option value="">All statuses</option>
          <option value="scheduled">Scheduled</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Loading / error */}
      {calendarQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading calendar...
        </div>
      )}
      {calendarQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load calendar. Please try again.
        </div>
      )}

      {/* Weekly calendar grid */}
      {!calendarQuery.isLoading && !calendarQuery.error && (
        <div className="grid grid-cols-7 gap-px rounded-lg border border-gray-200 bg-gray-200 overflow-hidden">
          {weekDays.map((day) => {
            const dateStr = formatDate(day);
            const sessions = sessionsByDate[dateStr] ?? [];
            const today = isToday(day);

            return (
              <div
                key={dateStr}
                className={`min-h-[200px] bg-white p-2 ${today ? 'ring-2 ring-inset ring-blue-500' : ''}`}
              >
                {/* Day header */}
                <div className="mb-2 text-center">
                  <div className="text-xs font-medium text-gray-500 uppercase">
                    {day.toLocaleDateString('en-ZA', { weekday: 'short' })}
                  </div>
                  <div
                    className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-semibold ${
                      today ? 'bg-blue-600 text-white' : 'text-gray-900'
                    }`}
                  >
                    {day.getDate()}
                  </div>
                </div>

                {/* Session blocks */}
                <div className="space-y-1">
                  {sessions.map((s) => {
                    const color = getSessionColor(s);
                    const isCancelled = s.status === 'cancelled';
                    const isPending = s.approval_status === 'pending_approval';

                    return (
                      <button
                        key={s.id}
                        onClick={() => setSelectedSession(s)}
                        className="w-full rounded px-1.5 py-1 text-left text-xs transition-opacity hover:opacity-80"
                        style={{
                          backgroundColor: isCancelled ? '#F3F4F6' : `${color}18`,
                          borderLeft: `3px solid ${isCancelled ? '#9CA3AF' : color}`,
                          opacity: isCancelled ? 0.6 : 1,
                        }}
                      >
                        <div
                          className="truncate font-medium"
                          style={{ color: isCancelled ? '#6B7280' : color }}
                        >
                          {s.title}
                          {isPending && (
                            <span className="ml-1 inline-block h-1.5 w-1.5 rounded-full bg-amber-400" />
                          )}
                        </div>
                        <div className="text-gray-500">
                          {formatTime(s.start_time)} - {formatTime(s.end_time)}
                        </div>
                        {isCancelled && (
                          <span className="text-[10px] font-medium uppercase text-gray-400">
                            Cancelled
                          </span>
                        )}
                      </button>
                    );
                  })}
                  {sessions.length === 0 && (
                    <p className="py-4 text-center text-[10px] text-gray-300">No classes</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Session detail modal */}
      {selectedSession && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => setSelectedSession(null)}
        >
          <div
            className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">{selectedSession.title}</h2>
                {selectedSession.class_type && (
                  <span
                    className="mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium text-white"
                    style={{
                      backgroundColor:
                        CLASS_TYPE_COLORS[selectedSession.class_type] ?? '#6B7280',
                    }}
                  >
                    {selectedSession.class_type.replace('_', ' ')}
                  </span>
                )}
              </div>
              <button
                onClick={() => setSelectedSession(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>

            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Time</dt>
                <dd className="font-medium text-gray-900">
                  {formatTime(selectedSession.start_time)} &ndash;{' '}
                  {formatTime(selectedSession.end_time)}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Date</dt>
                <dd className="font-medium text-gray-900">
                  {new Date(selectedSession.start_time).toLocaleDateString('en-ZA', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Status</dt>
                <dd>
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                      selectedSession.status === 'scheduled'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {selectedSession.status}
                  </span>
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Approval</dt>
                <dd>
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                      selectedSession.approval_status === 'approved' ||
                      selectedSession.approval_status === 'auto_approved'
                        ? 'bg-green-100 text-green-800'
                        : selectedSession.approval_status === 'pending_approval'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {selectedSession.approval_status.replace('_', ' ')}
                  </span>
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Capacity</dt>
                <dd className="font-medium text-gray-900">
                  {selectedSession.spots_booked} / {selectedSession.capacity}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Price</dt>
                <dd className="font-medium text-gray-900">
                  {formatPrice(selectedSession.price_cents)}
                </dd>
              </div>
            </dl>

            <div className="mt-6">
              <button
                onClick={() => setSelectedSession(null)}
                className="w-full rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
