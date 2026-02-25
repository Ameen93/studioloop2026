import { useQuery } from '@tanstack/react-query';
import { staffMembershipsGetInstructorSchedule } from '@sl/api-client';
import { getAuthHeaders, getStoredStaffInfo } from '../../lib/apiAuth';

function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return isoString;
  }
  return date.toLocaleString('en-ZA', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function Schedule() {
  const staffInfo = getStoredStaffInfo();
  const isInstructor = staffInfo?.role === 'instructor';

  const scheduleQuery = useQuery({
    queryKey: ['instructor-schedule'],
    queryFn: async () => {
      const response = await staffMembershipsGetInstructorSchedule({
        headers: getAuthHeaders(),
      });
      return response.data ?? [];
    },
    enabled: isInstructor,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Class Schedule</h1>
      </div>

      {!isInstructor && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          Instructor schedule is only available for staff users with the instructor role.
        </div>
      )}

      {isInstructor && scheduleQuery.isLoading && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
          Loading schedule...
        </div>
      )}

      {isInstructor && scheduleQuery.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load schedule.
        </div>
      )}

      {isInstructor && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Start
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  End
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {(scheduleQuery.data ?? []).map((item) => (
                <tr key={item.class_session_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.title}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {formatDateTime(item.start_time)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {formatDateTime(item.end_time)}
                  </td>
                </tr>
              ))}
              {(scheduleQuery.data ?? []).length === 0 && (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-sm text-gray-500">
                    No scheduled classes found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
