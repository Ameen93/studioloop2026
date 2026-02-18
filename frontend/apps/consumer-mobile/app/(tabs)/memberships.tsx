/**
 * Memberships tab - view active and past memberships.
 *
 * Displays the consumer's gym memberships with status,
 * expiration dates, and usage information.
 */

import { View, Text, FlatList, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';

// Placeholder type until API client types are generated
interface Membership {
  id: string;
  gymName: string;
  planName: string;
  status: 'active' | 'expired' | 'cancelled' | 'pending';
  startDate: string;
  endDate: string;
  priceZar: number;
  billingCycle: 'monthly' | 'annually' | 'once_off';
  classesUsed?: number;
  classesAllowed?: number;
}

const STATUS_STYLES = {
  active: { bg: 'bg-green-100', text: 'text-green-800' },
  expired: { bg: 'bg-gray-100', text: 'text-gray-800' },
  cancelled: { bg: 'bg-red-100', text: 'text-red-800' },
  pending: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
} as const;

export default function MembershipsTab() {
  const membershipsQuery = useQuery<Membership[]>({
    queryKey: ['consumer', 'memberships'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // e.g., consumerMembershipsListMyMemberships()
      return [];
    },
  });

  const formatCurrency = (amount: number) =>
    `R ${amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('en-ZA', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });

  const renderMembership = ({ item }: { item: Membership }) => {
    const statusStyle = STATUS_STYLES[item.status];

    return (
      <View className="bg-white rounded-lg p-4 mb-3 border border-gray-200">
        <View className="flex-row justify-between items-start">
          <View className="flex-1 mr-3">
            <Text className="text-lg font-semibold text-gray-900">{item.planName}</Text>
            <Text className="text-sm text-gray-600 mt-1">{item.gymName}</Text>
          </View>
          <View className={`${statusStyle.bg} px-3 py-1 rounded-full`}>
            <Text className={`${statusStyle.text} text-xs font-medium`}>
              {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
            </Text>
          </View>
        </View>

        <View className="mt-3 pt-3 border-t border-gray-100">
          <View className="flex-row justify-between mb-2">
            <Text className="text-sm text-gray-500">Period</Text>
            <Text className="text-sm text-gray-700">
              {formatDate(item.startDate)} - {formatDate(item.endDate)}
            </Text>
          </View>

          <View className="flex-row justify-between mb-2">
            <Text className="text-sm text-gray-500">Price</Text>
            <Text className="text-sm text-gray-700">
              {formatCurrency(item.priceZar)} / {item.billingCycle.replace('_', ' ')}
            </Text>
          </View>

          {item.classesAllowed && (
            <View className="flex-row justify-between">
              <Text className="text-sm text-gray-500">Classes</Text>
              <Text className="text-sm text-gray-700">
                {item.classesUsed ?? 0} / {item.classesAllowed} used
              </Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <View className="flex-1 bg-gray-50">
      <FlatList
        data={membershipsQuery.data ?? []}
        renderItem={renderMembership}
        keyExtractor={(item) => item.id}
        contentContainerClassName="px-4 pt-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={membershipsQuery.isRefetching}
            onRefresh={() => membershipsQuery.refetch()}
          />
        }
        ListEmptyComponent={
          membershipsQuery.isLoading ? (
            <ActivityIndicator size="large" color="#6366f1" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Ionicons name="card-outline" size={48} color="#d1d5db" />
              <Text className="text-gray-500 text-lg mt-4 mb-2">No memberships yet</Text>
              <Text className="text-gray-400 text-center px-8">
                Browse the marketplace to find a gym and membership plan that suits you
              </Text>
            </View>
          )
        }
      />
    </View>
  );
}
