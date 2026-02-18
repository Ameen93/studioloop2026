/**
 * Dashboard tab - today's metrics and quick actions for gym staff.
 *
 * Shows key metrics: check-ins today, active members, upcoming classes,
 * revenue summary, and quick navigation to reports.
 */

import { View, Text, ScrollView, Pressable, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { getStaffProfile } from '../../lib/auth';

interface DashboardMetrics {
  checkinsToday: number;
  activeMembers: number;
  upcomingClasses: number;
  revenueToday: number;
  pendingCheckins: number;
}

export default function DashboardTab() {
  const staff = getStaffProfile();

  const metricsQuery = useQuery<DashboardMetrics>({
    queryKey: ['gym', 'dashboard', 'metrics'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // e.g., gymDashboardGetMetrics({ path: { gym_id: staff?.gymId } })
      return {
        checkinsToday: 0,
        activeMembers: 0,
        upcomingClasses: 0,
        revenueToday: 0,
        pendingCheckins: 0,
      };
    },
  });

  const metrics = metricsQuery.data;

  const formatCurrency = (amount: number) =>
    `R ${amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      contentContainerClassName="pb-8"
      refreshControl={
        <RefreshControl
          refreshing={metricsQuery.isRefetching}
          onRefresh={() => metricsQuery.refetch()}
        />
      }
    >
      {/* Header */}
      <View className="bg-emerald-600 px-4 pt-6 pb-8">
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

      {/* Metrics cards */}
      <View className="px-4 -mt-4">
        <View className="flex-row flex-wrap -mx-1.5">
          <MetricCard
            icon="people"
            label="Check-ins Today"
            value={String(metrics?.checkinsToday ?? 0)}
            color="#059669"
          />
          <MetricCard
            icon="person"
            label="Active Members"
            value={String(metrics?.activeMembers ?? 0)}
            color="#6366f1"
          />
          <MetricCard
            icon="calendar"
            label="Classes Today"
            value={String(metrics?.upcomingClasses ?? 0)}
            color="#f59e0b"
          />
          <MetricCard
            icon="cash"
            label="Revenue Today"
            value={formatCurrency(metrics?.revenueToday ?? 0)}
            color="#ef4444"
          />
        </View>
      </View>

      {/* Pending offline check-ins alert */}
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

      {/* Quick actions */}
      <View className="px-4 mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
          Quick Actions
        </Text>

        <Pressable
          className="bg-white rounded-lg p-4 mb-3 border border-gray-200 flex-row items-center"
          onPress={() => router.push('/(tabs)/checkin')}
        >
          <View className="w-10 h-10 rounded-lg bg-emerald-100 items-center justify-center">
            <Ionicons name="qr-code" size={22} color="#059669" />
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-900 font-semibold">Scan QR Check-in</Text>
            <Text className="text-gray-500 text-sm">Scan a member's QR code</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#d1d5db" />
        </Pressable>

        <Pressable
          className="bg-white rounded-lg p-4 mb-3 border border-gray-200 flex-row items-center"
          onPress={() => router.push('/(tabs)/schedule')}
        >
          <View className="w-10 h-10 rounded-lg bg-indigo-100 items-center justify-center">
            <Ionicons name="calendar" size={22} color="#6366f1" />
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-900 font-semibold">View Schedule</Text>
            <Text className="text-gray-500 text-sm">Today's classes and bookings</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#d1d5db" />
        </Pressable>

        <Pressable
          className="bg-white rounded-lg p-4 mb-3 border border-gray-200 flex-row items-center"
          onPress={() => router.push('/reports')}
        >
          <View className="w-10 h-10 rounded-lg bg-amber-100 items-center justify-center">
            <Ionicons name="bar-chart" size={22} color="#f59e0b" />
          </View>
          <View className="flex-1 ml-3">
            <Text className="text-gray-900 font-semibold">Reports</Text>
            <Text className="text-gray-500 text-sm">Revenue, attendance, memberships</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#d1d5db" />
        </Pressable>
      </View>
    </ScrollView>
  );
}

function MetricCard({
  icon,
  label,
  value,
  color,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <View className="w-1/2 px-1.5 mb-3">
      <View className="bg-white rounded-lg p-4 border border-gray-200">
        <Ionicons name={icon} size={24} color={color} />
        <Text className="text-2xl font-bold text-gray-900 mt-2">{value}</Text>
        <Text className="text-xs text-gray-500 mt-1">{label}</Text>
      </View>
    </View>
  );
}
