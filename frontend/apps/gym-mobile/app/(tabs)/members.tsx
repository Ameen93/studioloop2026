/**
 * Members tab - search and browse gym members.
 *
 * Allows staff to search members by name, phone, or email
 * and view member details including membership status.
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
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';

interface Member {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  membershipStatus: 'active' | 'expired' | 'none';
  membershipPlan: string | null;
  lastCheckin: string | null;
}

export default function MembersTab() {
  const [searchQuery, setSearchQuery] = useState('');

  const membersQuery = useQuery<Member[]>({
    queryKey: ['gym', 'members', searchQuery],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // e.g., gymMembersList({ path: { gym_id: gymId }, query: { search: searchQuery } })
      return [];
    },
  });

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'active':
        return { bg: 'bg-green-100', text: 'text-green-800' };
      case 'expired':
        return { bg: 'bg-red-100', text: 'text-red-800' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-600' };
    }
  };

  const renderMember = ({ item }: { item: Member }) => {
    const fullName = `${item.firstName} ${item.lastName}`;
    const initials = `${item.firstName[0]}${item.lastName[0]}`.toUpperCase();
    const statusStyle = getStatusStyle(item.membershipStatus);

    return (
      <Pressable className="bg-white rounded-lg p-4 mb-2 border border-gray-200">
        <View className="flex-row items-center">
          <View className="w-12 h-12 rounded-full bg-emerald-100 items-center justify-center">
            <Text className="text-emerald-700 font-bold">{initials}</Text>
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-900 font-semibold">{fullName}</Text>
            <Text className="text-gray-500 text-sm mt-0.5">{item.phone || item.email}</Text>
          </View>
          <View className={`${statusStyle.bg} px-2.5 py-1 rounded-full`}>
            <Text className={`${statusStyle.text} text-xs font-medium`}>
              {item.membershipStatus.charAt(0).toUpperCase() + item.membershipStatus.slice(1)}
            </Text>
          </View>
        </View>

        {/* Additional details */}
        <View className="flex-row mt-3 pt-3 border-t border-gray-100">
          {item.membershipPlan && (
            <View className="flex-row items-center flex-1">
              <Ionicons name="card-outline" size={14} color="#6b7280" />
              <Text className="text-xs text-gray-500 ml-1">{item.membershipPlan}</Text>
            </View>
          )}
          {item.lastCheckin && (
            <View className="flex-row items-center">
              <Ionicons name="time-outline" size={14} color="#6b7280" />
              <Text className="text-xs text-gray-500 ml-1">
                Last visit:{' '}
                {new Date(item.lastCheckin).toLocaleDateString('en-ZA', {
                  day: '2-digit',
                  month: 'short',
                })}
              </Text>
            </View>
          )}
        </View>
      </Pressable>
    );
  };

  return (
    <View className="flex-1 bg-gray-50">
      {/* Search bar */}
      <View className="px-4 pt-4 pb-2">
        <View className="flex-row items-center bg-white border border-gray-300 rounded-lg px-3">
          <Ionicons name="search" size={20} color="#9ca3af" />
          <TextInput
            className="flex-1 py-3 px-2 text-gray-900"
            placeholder="Search by name, phone, or email..."
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
        data={membersQuery.data ?? []}
        renderItem={renderMember}
        keyExtractor={(item) => item.id}
        contentContainerClassName="px-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={membersQuery.isRefetching}
            onRefresh={() => membersQuery.refetch()}
          />
        }
        ListEmptyComponent={
          membersQuery.isLoading ? (
            <ActivityIndicator size="large" color="#059669" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Ionicons name="people-outline" size={48} color="#d1d5db" />
              <Text className="text-gray-500 text-lg mt-4 mb-2">
                {searchQuery ? 'No members found' : 'Search for members'}
              </Text>
              <Text className="text-gray-400 text-center px-8">
                {searchQuery
                  ? 'Try a different name, phone number, or email'
                  : 'Search by name, phone number, or email address'}
              </Text>
            </View>
          )
        }
      />
    </View>
  );
}
