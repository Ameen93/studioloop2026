/**
 * Schedule tab - today's classes with times, instructors, and booking counts.
 *
 * Displays the gym's class schedule for the current day
 * with instructor assignments and booking numbers.
 */

import { View, Text, FlatList, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';

interface ScheduleClass {
  id: string;
  name: string;
  instructorName: string;
  startTime: string;
  endTime: string;
  currentBookings: number;
  maxCapacity: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  room: string;
}

const STATUS_STYLES = {
  scheduled: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Scheduled' },
  in_progress: { bg: 'bg-green-100', text: 'text-green-800', label: 'In Progress' },
  completed: { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Completed' },
  cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelled' },
} as const;

export default function ScheduleTab() {
  const scheduleQuery = useQuery<ScheduleClass[]>({
    queryKey: ['gym', 'schedule', 'today'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // e.g., gymScheduleListToday({ path: { gym_id: gymId } })
      return [];
    },
  });

  const formatTime = (dateStr: string) =>
    new Date(dateStr).toLocaleTimeString('en-ZA', {
      hour: '2-digit',
      minute: '2-digit',
    });

  const renderClass = ({ item }: { item: ScheduleClass }) => {
    const statusStyle = STATUS_STYLES[item.status];
    const isFull = item.currentBookings >= item.maxCapacity;

    return (
      <View className="bg-white rounded-lg p-4 mb-3 border border-gray-200">
        <View className="flex-row justify-between items-start">
          <View className="flex-1 mr-3">
            <Text className="text-lg font-semibold text-gray-900">{item.name}</Text>
            <View className="flex-row items-center mt-1">
              <Ionicons name="person-outline" size={14} color="#6b7280" />
              <Text className="text-sm text-gray-600 ml-1">{item.instructorName}</Text>
            </View>
          </View>
          <View className={`${statusStyle.bg} px-3 py-1 rounded-full`}>
            <Text className={`${statusStyle.text} text-xs font-medium`}>{statusStyle.label}</Text>
          </View>
        </View>

        <View className="flex-row mt-3 pt-3 border-t border-gray-100">
          <View className="flex-row items-center flex-1">
            <Ionicons name="time-outline" size={16} color="#6b7280" />
            <Text className="text-sm text-gray-600 ml-1">
              {formatTime(item.startTime)} - {formatTime(item.endTime)}
            </Text>
          </View>

          {item.room && (
            <View className="flex-row items-center mr-4">
              <Ionicons name="location-outline" size={16} color="#6b7280" />
              <Text className="text-sm text-gray-600 ml-1">{item.room}</Text>
            </View>
          )}

          <View className="flex-row items-center">
            <Ionicons name="people-outline" size={16} color={isFull ? '#ef4444' : '#6b7280'} />
            <Text className={`text-sm ml-1 font-medium ${isFull ? 'text-red-600' : 'text-gray-600'}`}>
              {item.currentBookings}/{item.maxCapacity}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const today = new Date().toLocaleDateString('en-ZA', {
    weekday: 'long',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });

  return (
    <View className="flex-1 bg-gray-50">
      <FlatList
        data={scheduleQuery.data ?? []}
        renderItem={renderClass}
        keyExtractor={(item) => item.id}
        contentContainerClassName="px-4 pt-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={scheduleQuery.isRefetching}
            onRefresh={() => scheduleQuery.refetch()}
          />
        }
        ListHeaderComponent={
          <View className="mb-4">
            <Text className="text-sm text-gray-500">{today}</Text>
            <Text className="text-xl font-bold text-gray-900 mt-1">Today's Schedule</Text>
          </View>
        }
        ListEmptyComponent={
          scheduleQuery.isLoading ? (
            <ActivityIndicator size="large" color="#059669" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Ionicons name="calendar-outline" size={48} color="#d1d5db" />
              <Text className="text-gray-500 text-lg mt-4 mb-2">No classes today</Text>
              <Text className="text-gray-400 text-center">
                There are no classes scheduled for today
              </Text>
            </View>
          )
        }
      />
    </View>
  );
}
