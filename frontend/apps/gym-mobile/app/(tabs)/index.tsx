/**
 * Dashboard tab - today's metrics and quick actions for gym staff.
 */

import { View, Text, ScrollView, Pressable, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { MetricCard } from '@sl/ui';
import { analyticsGymOwnerDashboard } from '@sl/api-client';
import { getStaffProfile } from '../../lib/auth';
import { getAuthHeaders } from '../../lib/apiAuth';

interface DashboardMetrics {
  checkinsToday: number;
  activeMembers: number;
  upcomingClasses: number;
  revenueToday: number;
  pendingCheckins: number;
}

function toNumber(value: number | string | undefined): number {
  if (typeof value === 'number') {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

export default function DashboardTab() {
  const staff = getStaffProfile();

  const metricsQuery = useQuery<DashboardMetrics>({
    queryKey: ['gym', 'dashboard', 'metrics', staff?.gymId],
    queryFn: async () => {
      if (!staff?.gymId) {
        return {
          checkinsToday: 0,
          activeMembers: 0,
          upcomingClasses: 0,
          revenueToday: 0,
          pendingCheckins: 0,
        };
      }

      const response = await analyticsGymOwnerDashboard({
        path: { gym_id: staff.gymId },
        headers: getAuthHeaders(),
        throwOnError: true,
      });

      const dashboard = response.data;
      if (!dashboard) {
        return {
          checkinsToday: 0,
          activeMembers: 0,
          upcomingClasses: 0,
          revenueToday: 0,
          pendingCheckins: 0,
        };
      }

      return {
        checkinsToday: toNumber(dashboard.today_summary.check_ins_today),
        activeMembers: toNumber(dashboard.quick_metrics.active_members),
        upcomingClasses: toNumber(dashboard.today_summary.classes_today),
        revenueToday: toNumber(dashboard.today_summary.revenue_today_cents),
        pendingCheckins: toNumber(dashboard.action_items.pending_offline_checkins),
      };
    },
  });

  const metrics = metricsQuery.data;

  const formatCurrency = (amountCents: number) =>
    `R ${(amountCents / 100).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  return (
    <ScrollView
      className="flex-1 bg-[#0a0a0a]"
      contentContainerClassName="pb-8"
      refreshControl={
        <RefreshControl
          refreshing={metricsQuery.isRefetching}
          onRefresh={() => metricsQuery.refetch()}
        />
      }
    >
      <View className="bg-gold-600 px-4 pt-6 pb-8">
        <Text className="text-white text-sm opacity-80">
          {new Date().toLocaleDateString('en-ZA', {
            weekday: 'long',
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          })}
        </Text>
        <Text className="text-white text-2xl font-bold mt-1">
          {staff?.gymName ?? 'StudioLoop Gym'}
        </Text>
        <Text className="text-white opacity-80 mt-1">
          Welcome, {staff?.name?.split(' ')[0] ?? 'Staff'}
        </Text>
      </View>

      <View className="px-4 -mt-4">
        <View className="flex-row flex-wrap -mx-1.5">
          <View className="w-1/2 px-1.5 mb-3">
            <MetricCard
              icon={<Ionicons name="people" size={24} color="#d4a855" />}
              label="Check-ins Today"
              value={metrics?.checkinsToday ?? 0}
            />
          </View>
          <View className="w-1/2 px-1.5 mb-3">
            <MetricCard
              icon={<Ionicons name="person" size={24} color="#d4a855" />}
              label="Active Members"
              value={metrics?.activeMembers ?? 0}
            />
          </View>
          <View className="w-1/2 px-1.5 mb-3">
            <MetricCard
              icon={<Ionicons name="calendar" size={24} color="#f59e0b" />}
              label="Classes Today"
              value={metrics?.upcomingClasses ?? 0}
            />
          </View>
          <View className="w-1/2 px-1.5 mb-3">
            <MetricCard
              icon={<Ionicons name="cash" size={24} color="#ef4444" />}
              label="Revenue Today"
              value={formatCurrency(metrics?.revenueToday ?? 0)}
            />
          </View>
        </View>
      </View>

      {metrics && metrics.pendingCheckins > 0 && (
        <View className="mx-4 mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <View className="flex-row items-center">
            <Ionicons name="cloud-offline-outline" size={20} color="#d97706" />
            <Text className="text-yellow-800 font-medium ml-2">
              {metrics.pendingCheckins} offline check-in{metrics.pendingCheckins > 1 ? 's' : ''}{' '}
              pending sync
            </Text>
          </View>
        </View>
      )}

      <View className="px-4 mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
          Quick Actions
        </Text>

        <Pressable
          className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a] flex-row items-center"
          onPress={() => router.push('/(tabs)/checkin')}
        >
          <View className="w-10 h-10 rounded-lg bg-gold-100 items-center justify-center">
            <Ionicons name="qr-code" size={22} color="#d4a855" />
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-50 font-semibold">Scan QR Check-in</Text>
            <Text className="text-gray-500 text-sm">Scan a member's QR code</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#d1d5db" />
        </Pressable>

        <Pressable
          className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a] flex-row items-center"
          onPress={() => router.push('/(tabs)/members')}
        >
          <View className="w-10 h-10 rounded-lg bg-gold-100 items-center justify-center">
            <Ionicons name="people" size={22} color="#d4a855" />
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-50 font-semibold">View Members</Text>
            <Text className="text-gray-500 text-sm">Search membership roster</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#d1d5db" />
        </Pressable>

        <Pressable
          className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a] flex-row items-center"
          onPress={() => router.push('/reports')}
        >
          <View className="w-10 h-10 rounded-lg bg-amber-100 items-center justify-center">
            <Ionicons name="bar-chart" size={22} color="#f59e0b" />
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-50 font-semibold">Reports</Text>
            <Text className="text-gray-500 text-sm">Revenue, attendance, memberships</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#d1d5db" />
        </Pressable>
      </View>
    </ScrollView>
  );
}
