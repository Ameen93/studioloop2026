/**
 * Discover tab - browse marketplace classes and gyms.
 *
 * Allows consumers to search for and browse available
 * fitness classes from various gyms in the marketplace.
 */

import { useState } from 'react';
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

// Placeholder type until API client types are generated
interface MarketplaceClass {
  id: string;
  name: string;
  description: string;
  gymName: string;
  instructorName: string;
  startTime: string;
  duration: number;
  spotsAvailable: number;
  totalSpots: number;
  priceZar: number;
  category: string;
}

export default function DiscoverTab() {
  const [searchQuery, setSearchQuery] = useState('');

  const classesQuery = useQuery<MarketplaceClass[]>({
    queryKey: ['marketplace', 'classes', searchQuery],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // e.g., marketplaceListClasses({ query: { search: searchQuery } })
      return [];
    },
  });

  const formatCurrency = (amount: number) =>
    `R ${amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  const renderClass = ({ item }: { item: MarketplaceClass }) => (
    <Pressable
      className="bg-white rounded-lg p-4 mb-3 border border-gray-200"
      onPress={() => router.push(`/class/${item.id}`)}
    >
      <View className="flex-row justify-between items-start">
        <View className="flex-1 mr-3">
          <Text className="text-lg font-semibold text-gray-900">{item.name}</Text>
          <Text className="text-sm text-gray-600 mt-1">{item.gymName}</Text>
        </View>
        <View className="bg-indigo-50 px-3 py-1 rounded-full">
          <Text className="text-indigo-700 text-sm font-medium">{item.category}</Text>
        </View>
      </View>

      <Text className="text-sm text-gray-500 mt-2" numberOfLines={2}>
        {item.description}
      </Text>

      <View className="flex-row justify-between items-center mt-3 pt-3 border-t border-gray-100">
        <View className="flex-row items-center">
          <Ionicons name="person-outline" size={14} color="#6b7280" />
          <Text className="text-sm text-gray-500 ml-1">{item.instructorName}</Text>
        </View>
        <View className="flex-row items-center">
          <Ionicons name="time-outline" size={14} color="#6b7280" />
          <Text className="text-sm text-gray-500 ml-1">{item.duration} min</Text>
        </View>
        <Text className="text-sm font-semibold text-gray-900">{formatCurrency(item.priceZar)}</Text>
      </View>

      <View className="flex-row justify-between items-center mt-2">
        <Text className="text-xs text-gray-400">
          {new Date(item.startTime).toLocaleDateString('en-ZA', {
            day: '2-digit',
            month: 'short',
          })}{' '}
          at{' '}
          {new Date(item.startTime).toLocaleTimeString('en-ZA', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Text>
        <Text
          className={`text-xs font-medium ${
            item.spotsAvailable > 3 ? 'text-green-600' : 'text-orange-600'
          }`}
        >
          {item.spotsAvailable} / {item.totalSpots} spots left
        </Text>
      </View>
    </Pressable>
  );

  return (
    <View className="flex-1 bg-gray-50">
      {/* Search bar */}
      <View className="px-4 pt-4 pb-2">
        <View className="flex-row items-center bg-white border border-gray-300 rounded-lg px-3">
          <Ionicons name="search" size={20} color="#9ca3af" />
          <TextInput
            className="flex-1 py-3 px-2 text-gray-900"
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
        data={classesQuery.data ?? []}
        renderItem={renderClass}
        keyExtractor={(item) => item.id}
        contentContainerClassName="px-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={classesQuery.isRefetching}
            onRefresh={() => classesQuery.refetch()}
          />
        }
        ListEmptyComponent={
          classesQuery.isLoading ? (
            <ActivityIndicator size="large" color="#6366f1" className="mt-8" />
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
