/**
 * Schedule tab - today's upcoming classes.
 */

import { View, Text, FlatList, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { marketplaceBrowseMarketplaceClasses } from '@sl/api-client';
import type { MarketplaceClassItem } from '@sl/api-client';
import { getStaffProfile } from '../../lib/auth';
import { getAuthHeaders } from '../../lib/apiAuth';

export default function ScheduleTab() {
  const staff = getStaffProfile();

  const scheduleQuery = useQuery({
    queryKey: ['gym', 'schedule', 'today', staff?.gymId],
    queryFn: async () => {
      const response = await marketplaceBrowseMarketplaceClasses({
        headers: getAuthHeaders(),
        query: {
          start_date: new Date().toISOString().slice(0, 10),
          end_date: new Date().toISOString().slice(0, 10),
          limit: 200,
        },
      });

      const rows = response.data ?? [];
      if (!staff?.gymId) {
        return rows;
      }

      return rows.filter((item) => item.gym_id === staff.gymId);
    },
  });

  const formatTime = (dateStr: string) =>
    new Date(dateStr).toLocaleTimeString('en-ZA', {
      hour: '2-digit',
      minute: '2-digit',
    });

  const renderClass = ({ item }: { item: MarketplaceClassItem }) => {
    const isFull = item.spots_booked >= item.capacity;

    return (
      <View className="bg-white rounded-lg p-4 mb-3 border border-gray-200">
        <View className="flex-row justify-between items-start">
          <View className="flex-1 mr-3">
            <Text className="text-lg font-semibold text-gray-900">{item.title}</Text>
            <View className="flex-row items-center mt-1">
              <Ionicons name="business-outline" size={14} color="#6b7280" />
              <Text className="text-sm text-gray-600 ml-1">{item.gym_name}</Text>
            </View>
          </View>
          <View className="bg-blue-100 px-3 py-1 rounded-full">
            <Text className="text-blue-800 text-xs font-medium">Scheduled</Text>
          </View>
        </View>

        <View className="flex-row mt-3 pt-3 border-t border-gray-100">
          <View className="flex-row items-center flex-1">
            <Ionicons name="time-outline" size={16} color="#6b7280" />
            <Text className="text-sm text-gray-600 ml-1">
              {formatTime(item.start_time)} - {formatTime(item.end_time)}
            </Text>
          </View>

          <View className="flex-row items-center">
            <Ionicons name="people-outline" size={16} color={isFull ? '#ef4444' : '#6b7280'} />
            <Text className={`text-sm ml-1 font-medium ${isFull ? 'text-red-600' : 'text-gray-600'}`}>
              {item.spots_booked}/{item.capacity}
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
        keyExtractor={(item) => item.session_id}
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
            </View>
          )
        }
      />
    </View>
  );
}
