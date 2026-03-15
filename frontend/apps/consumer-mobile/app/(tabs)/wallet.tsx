/**
 * Wallet tab - subscription status, classes remaining, bookings overview, and quick actions.
 */

import { View, Text, ScrollView, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import {
  marketplaceViewMarketplaceSubscriptionStatus,
  marketplaceManageMarketplaceSubscription,
  staffMembershipsListConsumerMemberships,
  analyticsConsumerClassHistory,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export default function WalletTab() {
  const subscriptionQuery = useQuery({
    queryKey: ['consumer', 'marketplace-subscription'],
    queryFn: async () => {
      const response = await marketplaceViewMarketplaceSubscriptionStatus({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? null;
    },
  });

  const membershipsQuery = useQuery({
    queryKey: ['consumer', 'memberships'],
    queryFn: async () => {
      const response = await staffMembershipsListConsumerMemberships({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const historyQuery = useQuery({
    queryKey: ['consumer', 'class-history'],
    queryFn: async () => {
      const response = await analyticsConsumerClassHistory({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data?.items ?? [];
    },
  });

  const subscription = subscriptionQuery.data;
  const memberships = membershipsQuery.data ?? [];
  const activeMemberships = memberships.filter((m) => m.status === 'active');
  const recentActivity = (historyQuery.data ?? []).slice(0, 5);

  const isRefreshing =
    subscriptionQuery.isRefetching ||
    membershipsQuery.isRefetching ||
    historyQuery.isRefetching;

  const handleRefresh = () => {
    void subscriptionQuery.refetch();
    void membershipsQuery.refetch();
    void historyQuery.refetch();
  };

  const isLoading =
    subscriptionQuery.isLoading || membershipsQuery.isLoading || historyQuery.isLoading;

  if (isLoading) {
    return (
      <View className="flex-1 bg-[#0a0a0a] items-center justify-center">
        <ActivityIndicator size="large" color="#FF6B4A" />
      </View>
    );
  }

  return (
    <View className="flex-1 bg-[#0a0a0a]">
      <ScrollView
        contentContainerClassName="px-4 pt-4 pb-8"
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Subscription Card */}
        <View className="bg-[#1a1a1a] rounded-xl p-5 border border-[#2a2a2a] mb-4">
          <View className="flex-row justify-between items-start mb-3">
            <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              Marketplace Plan
            </Text>
            {subscription && (
              <View
                className={`px-2.5 py-0.5 rounded-full ${
                  subscription.status === 'active' ? 'bg-green-900' : 'bg-gray-800'
                }`}
              >
                <Text
                  className={`text-xs font-medium ${
                    subscription.status === 'active' ? 'text-green-300' : 'text-gray-400'
                  }`}
                >
                  {subscription.status}
                </Text>
              </View>
            )}
          </View>

          {subscription ? (
            <>
              <Text className="text-2xl font-bold text-gray-50 capitalize mb-1">
                {subscription.plan_tier} Plan
              </Text>

              {/* Classes balance */}
              <View className="flex-row items-end mb-3">
                <Text className="text-4xl font-bold text-coral-500">
                  {subscription.classes_remaining}
                </Text>
                <Text className="text-lg text-gray-500 ml-1 mb-1">
                  / {subscription.classes_total} classes
                </Text>
              </View>

              {/* Progress bar */}
              <View className="h-2 bg-gray-800 rounded-full mb-3">
                <View
                  className="h-2 bg-coral-500 rounded-full"
                  style={{
                    width: `${(subscription.classes_remaining / Math.max(1, subscription.classes_total)) * 100}%`,
                  }}
                />
              </View>

              <Text className="text-sm text-gray-500">
                Resets {formatDate(subscription.reset_at)}
              </Text>
            </>
          ) : (
            <View className="items-center py-4">
              <Ionicons name="layers-outline" size={36} color="#6b7280" />
              <Text className="text-gray-500 mt-2">No marketplace subscription</Text>
              <Pressable
                className="mt-3 bg-coral-600 rounded-lg py-2.5 px-5"
                onPress={() => router.push('/(tabs)/memberships')}
              >
                <Text className="text-white font-semibold">Subscribe</Text>
              </Pressable>
            </View>
          )}
        </View>

        {/* Studio Memberships */}
        {activeMemberships.length > 0 && (
          <View className="mb-4">
            <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
              Studio Memberships
            </Text>
            {activeMemberships.map((mem) => (
              <View
                key={mem.id}
                className="bg-[#1a1a1a] rounded-lg p-4 mb-2 border border-[#2a2a2a]"
              >
                <View className="flex-row justify-between items-center">
                  <View className="flex-1 mr-3">
                    <Text className="font-semibold text-gray-50">
                      {mem.plan_name ?? mem.gym_name ?? 'Gym Membership'}
                    </Text>
                    <Text className="text-sm text-gray-500 capitalize">{mem.membership_tier}</Text>
                  </View>
                  <View className="bg-green-900 px-2.5 py-0.5 rounded-full">
                    <Text className="text-green-300 text-xs font-medium">Active</Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Quick Actions */}
        <View className="flex-row mb-4">
          <Pressable
            className="flex-1 bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a] mr-2 items-center"
            onPress={() => router.push('/(tabs)/discover')}
          >
            <Ionicons name="search-outline" size={24} color="#FF6B4A" />
            <Text className="text-gray-50 text-sm font-medium mt-2">Find Classes</Text>
          </Pressable>
          <Pressable
            className="flex-1 bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a] mx-1 items-center"
            onPress={() => router.push('/(tabs)/memberships')}
          >
            <Ionicons name="swap-vertical-outline" size={24} color="#FF6B4A" />
            <Text className="text-gray-50 text-sm font-medium mt-2">Manage Plan</Text>
          </Pressable>
          <Pressable
            className="flex-1 bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a] ml-2 items-center"
            onPress={() => router.push('/(tabs)/qr-code')}
          >
            <Ionicons name="qr-code-outline" size={24} color="#FF6B4A" />
            <Text className="text-gray-50 text-sm font-medium mt-2">QR Code</Text>
          </Pressable>
        </View>

        {/* Recent Activity */}
        <View>
          <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
            Recent Activity
          </Text>
          {recentActivity.length === 0 ? (
            <View className="bg-[#1a1a1a] rounded-lg p-6 border border-[#2a2a2a] items-center">
              <Text className="text-gray-500">No recent activity</Text>
            </View>
          ) : (
            recentActivity.map((item, i) => (
              <Pressable
                key={`${item.session_id}-${item.attended_at}-${i}`}
                className="bg-[#1a1a1a] rounded-lg p-4 mb-2 border border-[#2a2a2a]"
                onPress={() => router.push(`/class/${item.session_id}`)}
              >
                <View className="flex-row justify-between items-center">
                  <View className="flex-1 mr-3">
                    <Text className="font-medium text-gray-50">{item.class_name}</Text>
                    <Text className="text-sm text-gray-500">
                      {item.gym_name ?? item.gym_id}
                    </Text>
                  </View>
                  <Text className="text-sm text-gray-500">
                    {new Date(item.attended_at).toLocaleDateString('en-ZA', {
                      day: '2-digit',
                      month: 'short',
                    })}
                  </Text>
                </View>
              </Pressable>
            ))
          )}
        </View>
      </ScrollView>
    </View>
  );
}
