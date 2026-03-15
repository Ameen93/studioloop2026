/**
 * Discover tab - browse marketplace classes and gyms.
 */

import { useMemo, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  Pressable,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { marketplaceBrowseMarketplaceClasses } from '@sl/api-client';
import type { MarketplaceClassItem } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

export default function DiscoverTab() {
  const [searchQuery, setSearchQuery] = useState('');

  const classesQuery = useQuery({
    queryKey: ['marketplace', 'classes'],
    queryFn: async () => {
      const response = await marketplaceBrowseMarketplaceClasses({
        headers: getAuthHeaders(),
        query: { limit: 100 },
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const filteredClasses = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    const classes = classesQuery.data ?? [];
    if (!q) {
      return classes;
    }

    return classes.filter((item) => {
      return (
        item.title.toLowerCase().includes(q) ||
        item.gym_name.toLowerCase().includes(q) ||
        (item.city ?? '').toLowerCase().includes(q) ||
        (item.province ?? '').toLowerCase().includes(q)
      );
    });
  }, [classesQuery.data, searchQuery]);

  const formatCurrency = (amountCents: number) =>
    `R ${(amountCents / 100).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  const renderClass = ({ item }: { item: MarketplaceClassItem }) => {
    const spotsAvailable = Math.max(0, item.capacity - item.spots_booked);

    return (
      <Pressable
        className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a]"
        onPress={() => router.push(`/class/${item.session_id}`)}
      >
        <View className="flex-row justify-between items-start">
          <View className="flex-1 mr-3">
            <Text className="text-lg font-semibold text-gray-50">{item.title}</Text>
            <Text className="text-sm text-gray-600 mt-1">{item.gym_name}</Text>
          </View>
          <Text className="text-sm font-semibold text-gray-50">{formatCurrency(item.price_cents)}</Text>
        </View>

        <View className="flex-row justify-between items-center mt-3 pt-3 border-t border-gray-100">
          <View className="flex-row items-center">
            <Ionicons name="time-outline" size={14} color="#6b7280" />
            <Text className="text-sm text-gray-500 ml-1">
              {new Date(item.start_time).toLocaleDateString('en-ZA', {
                day: '2-digit',
                month: 'short',
              })}{' '}
              {new Date(item.start_time).toLocaleTimeString('en-ZA', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
          </View>
          <Text
            className={`text-xs font-medium ${spotsAvailable > 3 ? 'text-green-600' : 'text-orange-600'}`}
          >
            {spotsAvailable} / {item.capacity} spots left
          </Text>
        </View>
      </Pressable>
    );
  };

  return (
    <View className="flex-1 bg-[#0a0a0a]">
      <View className="px-4 pt-4 pb-2">
        <View className="flex-row items-center bg-[#1a1a1a] border border-gray-300 rounded-lg px-3">
          <Ionicons name="search" size={20} color="#9ca3af" />
          <TextInput
            className="flex-1 py-3 px-2 text-gray-50"
            placeholder="Search classes, gyms, instructors..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCapitalize="none"
            returnKeyType="search"
          />
          {searchQuery.length > 0 && (
            <Pressable onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={20} color="#9ca3af" />
            </Pressable>
          )}
        </View>
      </View>

      <FlatList
        data={filteredClasses}
        renderItem={renderClass}
        keyExtractor={(item) => item.session_id}
        contentContainerClassName="px-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={classesQuery.isRefetching}
            onRefresh={() => classesQuery.refetch()}
          />
        }
        ListEmptyComponent={
          classesQuery.isLoading ? (
            <ActivityIndicator size="large" color="#FF6B4A" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Ionicons name="search" size={48} color="#d1d5db" />
              <Text className="text-gray-500 text-lg mt-4 mb-2">
                {searchQuery ? 'No classes found' : 'Discover fitness classes'}
              </Text>
              <Text className="text-gray-400 text-center px-8">
                {searchQuery
                  ? 'Try adjusting your search terms'
                  : 'Search for classes, gyms, or instructors to get started'}
              </Text>
            </View>
          )
        }
      />
    </View>
  );
}
