/**
 * Memberships tab - view active gym memberships and marketplace subscription.
 */

import { useState } from 'react';
import { View, Text, FlatList, ActivityIndicator, RefreshControl, Pressable } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import {
  marketplaceViewMarketplaceSubscriptionStatus,
  staffMembershipsListConsumerMemberships,
} from '@sl/api-client';
import type { MembershipPublic } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type TabType = 'gym' | 'marketplace';

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  active: { bg: 'bg-green-100', text: 'text-green-800' },
  inactive: { bg: 'bg-gray-100', text: 'text-gray-800' },
  cancelled: { bg: 'bg-red-100', text: 'text-red-800' },
  paused: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
};

export default function MembershipsTab() {
  const [activeTab, setActiveTab] = useState<TabType>('gym');

  const gymMembershipsQuery = useQuery({
    queryKey: ['consumer', 'memberships'],
    queryFn: async () => {
      const response = await staffMembershipsListConsumerMemberships({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const marketplaceSubscriptionQuery = useQuery({
    queryKey: ['consumer', 'marketplace-subscription'],
    queryFn: async () => {
      const response = await marketplaceViewMarketplaceSubscriptionStatus({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? null;
    },
  });

  const renderMembership = ({ item }: { item: MembershipPublic }) => {
    const style = STATUS_STYLES[item.status] ?? STATUS_STYLES.inactive;

    return (
      <View className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a]">
        <View className="flex-row justify-between items-start">
          <View className="flex-1 mr-3">
            <Text className="text-lg font-semibold text-gray-50">{item.membership_tier}</Text>
            <Text className="text-sm text-gray-600 mt-1">Gym ID: {item.gym_id}</Text>
          </View>
          <View className={`${style.bg} px-3 py-1 rounded-full`}>
            <Text className={`${style.text} text-xs font-medium`}>{item.status}</Text>
          </View>
        </View>

        <View className="mt-3 pt-3 border-t border-gray-100">
          <Text className="text-sm text-gray-500">Plan: {item.membership_plan_id ?? 'Default plan'}</Text>
        </View>
      </View>
    );
  };

  return (
    <View className="flex-1 bg-[#0a0a0a]">
      <View className="px-4 pt-4 pb-2">
        <View className="flex-row bg-gray-100 rounded-lg p-1">
          <Pressable
            className={`flex-1 py-2 rounded-md ${activeTab === 'gym' ? 'bg-[#1a1a1a]' : ''}`}
            onPress={() => setActiveTab('gym')}
          >
            <Text className="text-center text-sm font-medium text-gray-50">Gym</Text>
          </Pressable>
          <Pressable
            className={`flex-1 py-2 rounded-md ${activeTab === 'marketplace' ? 'bg-[#1a1a1a]' : ''}`}
            onPress={() => setActiveTab('marketplace')}
          >
            <Text className="text-center text-sm font-medium text-gray-50">Marketplace</Text>
          </Pressable>
        </View>
      </View>

      {activeTab === 'gym' ? (
        <FlatList
          data={gymMembershipsQuery.data ?? []}
          renderItem={renderMembership}
          keyExtractor={(item) => item.id}
          contentContainerClassName="px-4 pb-8"
          refreshControl={
            <RefreshControl
              refreshing={gymMembershipsQuery.isRefetching}
              onRefresh={() => gymMembershipsQuery.refetch()}
            />
          }
          ListEmptyComponent={
            gymMembershipsQuery.isLoading ? (
              <ActivityIndicator size="large" color="#FF6B4A" className="mt-8" />
            ) : (
              <View className="items-center py-12">
                <Ionicons name="card-outline" size={48} color="#d1d5db" />
                <Text className="text-gray-500 text-lg mt-4 mb-2">No memberships yet</Text>
              </View>
            )
          }
        />
      ) : (
        <View className="px-4 pt-2">
          {marketplaceSubscriptionQuery.isLoading ? (
            <ActivityIndicator size="large" color="#FF6B4A" className="mt-8" />
          ) : !marketplaceSubscriptionQuery.data ? (
            <View className="items-center py-12">
              <Ionicons name="layers-outline" size={48} color="#d1d5db" />
              <Text className="text-gray-500 text-lg mt-4 mb-2">No marketplace subscription</Text>
            </View>
          ) : (
            <View className="bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a]">
              <Text className="text-lg font-semibold text-gray-50 capitalize">
                {marketplaceSubscriptionQuery.data.plan_tier} plan
              </Text>
              <Text className="text-sm text-gray-600 mt-1">
                Classes: {marketplaceSubscriptionQuery.data.classes_remaining} / {marketplaceSubscriptionQuery.data.classes_total}
              </Text>
              <Text className="text-sm text-gray-600 mt-1">
                Status: {marketplaceSubscriptionQuery.data.status}
              </Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
}
