/**
 * Reports screen - simplified mobile reports for gym staff.
 */

import { useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import {
  analyticsAttendanceReport,
  analyticsMembershipHealthReport,
  analyticsRevenueReport,
} from '@sl/api-client';
import { getGymId } from '../lib/auth';
import { getAuthHeaders } from '../lib/apiAuth';

type ReportTab = 'revenue' | 'attendance' | 'memberships';

export default function ReportsScreen() {
  const [activeTab, setActiveTab] = useState<ReportTab>('revenue');
  const gymId = getGymId();

  const revenueQuery = useQuery({
    queryKey: ['gym', 'reports', 'revenue', gymId],
    queryFn: async () => {
      if (!gymId) return null;

      const response = await analyticsRevenueReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return response.data ?? null;
    },
    enabled: activeTab === 'revenue',
  });

  const attendanceQuery = useQuery({
    queryKey: ['gym', 'reports', 'attendance', gymId],
    queryFn: async () => {
      if (!gymId) return null;

      const response = await analyticsAttendanceReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return response.data ?? null;
    },
    enabled: activeTab === 'attendance',
  });

  const membershipQuery = useQuery({
    queryKey: ['gym', 'reports', 'memberships', gymId],
    queryFn: async () => {
      if (!gymId) return null;

      const response = await analyticsMembershipHealthReport({
        path: { gym_id: gymId },
        headers: getAuthHeaders(),
      });
      return response.data ?? null;
    },
    enabled: activeTab === 'memberships',
  });

  const formatCurrency = (amountCents: number) =>
    `R ${(amountCents / 100).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  const isLoading =
    (activeTab === 'revenue' && revenueQuery.isLoading) ||
    (activeTab === 'attendance' && attendanceQuery.isLoading) ||
    (activeTab === 'memberships' && membershipQuery.isLoading);

  const refetch = () => {
    if (activeTab === 'revenue') void revenueQuery.refetch();
    if (activeTab === 'attendance') void attendanceQuery.refetch();
    if (activeTab === 'memberships') void membershipQuery.refetch();
  };

  return (
    <ScrollView
      className="flex-1 bg-[#0a0a0a]"
      contentContainerClassName="pb-8"
      refreshControl={<RefreshControl refreshing={false} onRefresh={refetch} />}
    >
      <View className="flex-row bg-[#1a1a1a] border-b border-[#2a2a2a] px-4 py-2">
        {(['revenue', 'attendance', 'memberships'] as const).map((tab) => (
          <Pressable
            key={tab}
            className={`flex-1 py-2 rounded-lg mx-0.5 ${activeTab === tab ? 'bg-gold-600' : 'bg-gray-100'}`}
            onPress={() => setActiveTab(tab)}
          >
            <Text
              className={`text-center text-sm font-medium ${activeTab === tab ? 'text-white' : 'text-gray-600'}`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Text>
          </Pressable>
        ))}
      </View>

      {isLoading ? (
        <ActivityIndicator size="large" color="#d4a855" className="mt-12" />
      ) : (
        <View className="px-4 pt-4">
          {activeTab === 'revenue' && revenueQuery.data && (
            <View>
              <View className="flex-row mb-3">
                <StatCard
                  label="Total Revenue"
                  value={formatCurrency(revenueQuery.data.total_revenue_cents)}
                  icon="cash"
                  color="#d4a855"
                />
                <StatCard
                  label="Growth"
                  value={`${revenueQuery.data.growth_percent.toFixed(1)}%`}
                  icon="trending-up"
                  color="#6366f1"
                />
              </View>

              <View className="bg-[#1a1a1a] rounded-lg p-4 mb-2 border border-[#2a2a2a]">
                <Text className="text-sm text-gray-500">Memberships</Text>
                <Text className="text-lg font-semibold text-gray-50">
                  {formatCurrency(revenueQuery.data.source_breakdown.memberships_cents)}
                </Text>
              </View>
              <View className="bg-[#1a1a1a] rounded-lg p-4 mb-2 border border-[#2a2a2a]">
                <Text className="text-sm text-gray-500">Classes</Text>
                <Text className="text-lg font-semibold text-gray-50">
                  {formatCurrency(revenueQuery.data.source_breakdown.classes_cents)}
                </Text>
              </View>
            </View>
          )}

          {activeTab === 'attendance' && attendanceQuery.data && (
            <View>
              <View className="flex-row mb-3">
                <StatCard
                  label="Total Check-ins"
                  value={String(attendanceQuery.data.total_check_ins)}
                  icon="people"
                  color="#d4a855"
                />
                <StatCard
                  label="Avg Daily"
                  value={attendanceQuery.data.average_daily_attendance.toFixed(1)}
                  icon="bar-chart"
                  color="#f59e0b"
                />
              </View>
              <View className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a]">
                <View className="flex-row items-center">
                  <Ionicons name="time" size={20} color="#6366f1" />
                  <Text className="text-gray-500 ml-2">Peak Hour</Text>
                  <Text className="text-gray-50 font-semibold ml-auto">
                    {attendanceQuery.data.peak_hour ?? '--'}:00
                  </Text>
                </View>
              </View>
            </View>
          )}

          {activeTab === 'memberships' && membershipQuery.data && (
            <View>
              <View className="flex-row mb-3">
                <StatCard
                  label="Active Members"
                  value={String(membershipQuery.data.total_active_members)}
                  icon="person"
                  color="#d4a855"
                />
                <StatCard
                  label="New This Period"
                  value={String(membershipQuery.data.new_this_period)}
                  icon="add-circle"
                  color="#6366f1"
                />
              </View>

              <View className="flex-row mb-3">
                <StatCard
                  label="Expiring Soon"
                  value={String(membershipQuery.data.expiring_soon_member_count)}
                  icon="warning"
                  color="#f59e0b"
                />
                <StatCard
                  label="Churn Rate"
                  value={`${membershipQuery.data.churn_rate_percent.toFixed(1)}%`}
                  icon="trending-down"
                  color="#ef4444"
                />
              </View>
            </View>
          )}

          {((activeTab === 'revenue' && !revenueQuery.data) ||
            (activeTab === 'attendance' && !attendanceQuery.data) ||
            (activeTab === 'memberships' && !membershipQuery.data)) && (
            <EmptyState message="No report data available yet" />
          )}
        </View>
      )}
    </ScrollView>
  );
}

function StatCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: string;
  icon: keyof typeof Ionicons.glyphMap;
  color: string;
}) {
  return (
    <View className="flex-1 mx-1">
      <View className="bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a]">
        <Ionicons name={icon} size={24} color={color} />
        <Text className="text-xl font-bold text-gray-50 mt-2">{value}</Text>
        <Text className="text-xs text-gray-500 mt-1">{label}</Text>
      </View>
    </View>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <View className="bg-[#1a1a1a] rounded-lg p-6 border border-[#2a2a2a] items-center">
      <Ionicons name="analytics-outline" size={32} color="#d1d5db" />
      <Text className="text-gray-400 mt-2">{message}</Text>
    </View>
  );
}
