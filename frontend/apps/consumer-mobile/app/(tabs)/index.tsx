/**
 * Home tab - consumer activity overview.
 */

import { View, Text, FlatList, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { MetricCard } from '@sl/ui';
import { analyticsConsumerClassHistory, analyticsConsumerStats } from '@sl/api-client';
import type { ConsumerClassHistoryItem } from '@sl/api-client';
import { getConsumerProfile } from '../../lib/auth';
import { getAuthHeaders } from '../../lib/apiAuth';

export default function HomeTab() {
  const profile = getConsumerProfile();

  const statsQuery = useQuery({
    queryKey: ['consumer', 'stats'],
    queryFn: async () => {
      const response = await analyticsConsumerStats({ headers: getAuthHeaders() });
      return response.data ?? null;
    },
  });

  const historyQuery = useQuery({
    queryKey: ['consumer', 'class-history'],
    queryFn: async () => {
      const response = await analyticsConsumerClassHistory({ headers: getAuthHeaders() });
      return response.data?.items ?? [];
    },
  });

  const renderHistory = ({ item }: { item: ConsumerClassHistoryItem }) => (
    <Pressable
      className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a]"
      onPress={() => router.push(`/class/${item.session_id}`)}
    >
      <Text className="text-lg font-semibold text-gray-50">{item.class_name}</Text>
      <Text className="text-sm text-gray-600 mt-1">Gym: {item.gym_id}</Text>
      <Text className="text-sm text-gray-500 mt-2">
        {new Date(item.attended_at).toLocaleDateString('en-ZA', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        })}
      </Text>
    </Pressable>
  );

  return (
    <View className="flex-1 bg-[#0a0a0a]">
      <FlatList
        data={historyQuery.data ?? []}
        renderItem={renderHistory}
        keyExtractor={(item) => `${item.session_id}-${item.attended_at}`}
        contentContainerClassName="px-4 pt-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={historyQuery.isRefetching || statsQuery.isRefetching}
            onRefresh={() => {
              void historyQuery.refetch();
              void statsQuery.refetch();
            }}
          />
        }
        ListHeaderComponent={
          <View className="mb-6">
            <Text className="text-2xl font-bold text-gray-50">
              Welcome{profile?.name ? `, ${profile.name.split(' ')[0]}` : ''}
            </Text>
            <Text className="text-gray-600 mt-1">Your activity overview</Text>

            <View className="flex-row mt-4">
              <View className="flex-1 mr-2">
                <MetricCard
                  label="Classes this month"
                  value={statsQuery.data?.total_classes_this_month ?? 0}
                />
              </View>
              <View className="flex-1 ml-2">
                <MetricCard
                  label="Current streak"
                  value={`${statsQuery.data?.current_streak_weeks ?? 0}w`}
                />
              </View>
            </View>

            <View className="flex-row mt-3">
              <Pressable
                className="flex-1 bg-coral-600 rounded-lg py-3 px-4 mr-2"
                onPress={() => router.push('/(tabs)/qr-code')}
              >
                <Text className="text-white text-center font-semibold">Show QR Code</Text>
              </Pressable>
              <Pressable
                className="flex-1 bg-[#1a1a1a] border border-gray-300 rounded-lg py-3 px-4 ml-2"
                onPress={() => router.push('/(tabs)/discover')}
              >
                <Text className="text-gray-700 text-center font-semibold">Browse Classes</Text>
              </Pressable>
            </View>
          </View>
        }
        ListEmptyComponent={
          historyQuery.isLoading ? (
            <ActivityIndicator size="large" color="#FF6B4A" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Text className="text-gray-500 text-lg mb-2">No recent class activity</Text>
              <Text className="text-gray-400 text-center mb-4">
                Browse the marketplace to find classes near you
              </Text>
              <Pressable
                className="bg-coral-600 rounded-lg py-3 px-6"
                onPress={() => router.push('/(tabs)/discover')}
              >
                <Text className="text-white font-semibold">Discover Classes</Text>
              </Pressable>
            </View>
          )
        }
      />
    </View>
  );
}
