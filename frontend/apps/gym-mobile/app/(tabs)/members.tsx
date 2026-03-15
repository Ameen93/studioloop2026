/**
 * Members tab - search and browse gym members.
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
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { staffMembershipsListGymMembers } from '@sl/api-client';
import type { GymMemberListItem } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

export default function MembersTab() {
  const [searchQuery, setSearchQuery] = useState('');

  const membersQuery = useQuery({
    queryKey: ['gym', 'members'],
    queryFn: async () => {
      const response = await staffMembershipsListGymMembers({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const filteredMembers = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    const rows = membersQuery.data ?? [];
    if (!q) {
      return rows;
    }

    return rows.filter((item) => {
      return (
        item.consumer_email.toLowerCase().includes(q) ||
        item.consumer_id.toLowerCase().includes(q) ||
        (item.membership_plan_name ?? '').toLowerCase().includes(q)
      );
    });
  }, [membersQuery.data, searchQuery]);

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'active':
        return { bg: 'bg-green-100', text: 'text-green-800' };
      case 'cancelled':
        return { bg: 'bg-red-100', text: 'text-red-800' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-600' };
    }
  };

  const renderMember = ({ item }: { item: GymMemberListItem }) => {
    const nameFromEmail = item.consumer_email.split('@')[0] || item.consumer_id.slice(0, 8);
    const initials = nameFromEmail.slice(0, 2).toUpperCase();
    const statusStyle = getStatusStyle(item.status);

    return (
      <Pressable className="bg-[#1a1a1a] rounded-lg p-4 mb-2 border border-[#2a2a2a]">
        <View className="flex-row items-center">
          <View className="w-12 h-12 rounded-full bg-gold-100 items-center justify-center">
            <Text className="text-gold-700 font-bold">{initials}</Text>
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-50 font-semibold">{nameFromEmail}</Text>
            <Text className="text-gray-500 text-sm mt-0.5">{item.consumer_email}</Text>
          </View>
          <View className={`${statusStyle.bg} px-2.5 py-1 rounded-full`}>
            <Text className={`${statusStyle.text} text-xs font-medium`}>{item.status}</Text>
          </View>
        </View>

        <View className="flex-row mt-3 pt-3 border-t border-gray-100">
          <View className="flex-row items-center flex-1">
            <Ionicons name="card-outline" size={14} color="#6b7280" />
            <Text className="text-xs text-gray-500 ml-1">{item.membership_tier}</Text>
          </View>
          <View className="flex-row items-center">
            <Ionicons name="id-card-outline" size={14} color="#6b7280" />
            <Text className="text-xs text-gray-500 ml-1">
              {item.membership_plan_name ?? 'Default Plan'}
            </Text>
          </View>
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
        data={filteredMembers}
        renderItem={renderMember}
        keyExtractor={(item) => item.membership_id}
        contentContainerClassName="px-4 pb-8"
        refreshControl={
          <RefreshControl
            refreshing={membersQuery.isRefetching}
            onRefresh={() => membersQuery.refetch()}
          />
        }
        ListEmptyComponent={
          membersQuery.isLoading ? (
            <ActivityIndicator size="large" color="#d4a855" className="mt-8" />
          ) : (
            <View className="items-center py-12">
              <Ionicons name="people-outline" size={48} color="#d1d5db" />
              <Text className="text-gray-500 text-lg mt-4 mb-2">
                {searchQuery ? 'No members found' : 'No members yet'}
              </Text>
            </View>
          )
        }
      />
    </View>
  );
}
