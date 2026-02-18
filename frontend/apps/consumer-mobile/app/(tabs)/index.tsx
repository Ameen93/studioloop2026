/**
 * Home tab - shows upcoming bookings and quick actions.
 *
 * Displays a welcome message, upcoming class bookings,
 * and a quick-access QR code button for check-in.
 */

import { View, Text, FlatList, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { getConsumerProfile } from '../../lib/auth';

// Placeholder type for bookings until API client types are available
interface Booking {
  id: string;
  className: string;
  gymName: string;
  startTime: string;
  endTime: string;
  status: string;
}

export default function HomeTab() {
  const profile = getConsumerProfile();

  const bookingsQuery = useQuery<Booking[]>({
    queryKey: ['consumer', 'bookings', 'upcoming'],
    queryFn: async () => {
      // TODO: Replace with actual API call when endpoint is wired up
      // e.g., consumerBookingsListMyBookings({ query: { status: 'upcoming' } })
      return [];
    },
  });

  const renderBooking = ({ item }: { item: Booking }) => (
    <Pressable
      className="bg-white rounded-lg p-4 mb-3 border border-gray-200"
      onPress={() => router.push(`/class/${item.id}`)}
    >
      <Text className="text-lg font-semibold text-gray-900">{item.className}</Text>
      <Text className="text-sm text-gray-600 mt-1">{item.gymName}</Text>
      <View className="flex-row justify-between mt-2">
        <Text className="text-sm text-gray-500">
          {new Date(item.startTime).toLocaleDateString('en-ZA', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          })}
        </Text>
        <Text className="text-sm text-gray-500">
          {new Date(item.startTime).toLocaleTimeString('en-ZA', {
            hour: '2-digit',
            minute: '2-digit',
          })}
          {' - '}
          {new Date(item.endTime).toLocaleTimeString('en-ZA', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Text>
      </View>
      <View className="mt-2">
        <Text
          className={`text-xs font-medium px-2 py-1 rounded-full self-start ${
            item.status === 'confirmed'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
        </Text>
      </View>
    </Pressable>
  );

  return (
    <View className="flex-1 bg-gray-50">
      <FlatList
        data={bookingsQuery.data ?? []}
        renderItem={renderBooking}
        keyExtractor={(item) => item.id}
        contentContainerClassName="px-4 pt-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={bookingsQuery.isRefetching}
            onRefresh={() => bookingsQuery.refetch()}
          />
        }
        ListHeaderComponent={
          <View className="mb-6">
            <Text className="text-2xl font-bold text-gray-900">
              Welcome{profile?.name ? `, ${profile.name.split(' ')[0]}` : ''}
            </Text>
            <Text className="text-gray-600 mt-1">Your upcoming bookings</Text>

            {/* Quick action buttons */}
            <View className="flex-row mt-4 space-x-3">
              <Pressable
                className="flex-1 bg-indigo-600 rounded-lg py-3 px-4"
                onPress={() => router.push('/(tabs)/qr-code')}
              >
                <Text className="text-white text-center font-semibold">Show QR Code</Text>
              </Pressable>
              <Pressable
                className="flex-1 bg-white border border-gray-300 rounded-lg py-3 px-4"
                onPress={() => router.push('/(tabs)/discover')}
              >
                <Text className="text-gray-700 text-center font-semibold">Browse Classes</Text>
              </Pressable>
            </View>
          </View>
        }
        ListEmptyComponent={
          bookingsQuery.isLoading ? (
            <ActivityIndicator size="large" color="#6366f1" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Text className="text-gray-500 text-lg mb-2">No upcoming bookings</Text>
              <Text className="text-gray-400 text-center mb-4">
                Browse the marketplace to find classes near you
              </Text>
              <Pressable
                className="bg-indigo-600 rounded-lg py-3 px-6"
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
