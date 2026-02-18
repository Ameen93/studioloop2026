/**
 * Reports screen - simplified mobile reports for gym staff.
 *
 * Shows key reports: Revenue, Attendance, Membership Health.
 * Provides a high-level overview suitable for mobile viewing.
 */

import { useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';

type ReportTab = 'revenue' | 'attendance' | 'memberships';

interface RevenueData {
  totalRevenue: number;
  monthlyRevenue: number;
  topPlans: { name: string; revenue: number; count: number }[];
}

interface AttendanceData {
  totalCheckins: number;
  avgDaily: number;
  peakHour: string;
  topClasses: { name: string; attendance: number }[];
}

interface MembershipData {
  totalActive: number;
  newThisMonth: number;
  expiringThisMonth: number;
  churnRate: number;
  breakdown: { plan: string; count: number; percentage: number }[];
}

export default function ReportsScreen() {
  const [activeTab, setActiveTab] = useState<ReportTab>('revenue');

  const revenueQuery = useQuery<RevenueData>({
    queryKey: ['gym', 'reports', 'revenue'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      return {
        totalRevenue: 0,
        monthlyRevenue: 0,
        topPlans: [],
      };
    },
    enabled: activeTab === 'revenue',
  });

  const attendanceQuery = useQuery<AttendanceData>({
    queryKey: ['gym', 'reports', 'attendance'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      return {
        totalCheckins: 0,
        avgDaily: 0,
        peakHour: '--',
        topClasses: [],
      };
    },
    enabled: activeTab === 'attendance',
  });

  const membershipQuery = useQuery<MembershipData>({
    queryKey: ['gym', 'reports', 'memberships'],
    queryFn: async () => {
      // TODO: Replace with actual API call
      return {
        totalActive: 0,
        newThisMonth: 0,
        expiringThisMonth: 0,
        churnRate: 0,
        breakdown: [],
      };
    },
    enabled: activeTab === 'memberships',
  });

  const formatCurrency = (amount: number) =>
    `R ${amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  const isLoading =
    (activeTab === 'revenue' && revenueQuery.isLoading) ||
    (activeTab === 'attendance' && attendanceQuery.isLoading) ||
    (activeTab === 'memberships' && membershipQuery.isLoading);

  const refetch = () => {
    if (activeTab === 'revenue') revenueQuery.refetch();
    if (activeTab === 'attendance') attendanceQuery.refetch();
    if (activeTab === 'memberships') membershipQuery.refetch();
  };

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      contentContainerClassName="pb-8"
      refreshControl={<RefreshControl refreshing={false} onRefresh={refetch} />}
    >
      {/* Tab selector */}
      <View className="flex-row bg-white border-b border-gray-200 px-4 py-2">
        {(['revenue', 'attendance', 'memberships'] as const).map((tab) => (
          <Pressable
            key={tab}
            className={`flex-1 py-2 rounded-lg mx-0.5 ${activeTab === tab ? 'bg-emerald-600' : 'bg-gray-100'}`}
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
        <ActivityIndicator size="large" color="#059669" className="mt-12" />
      ) : (
        <View className="px-4 pt-4">
          {/* Revenue report */}
          {activeTab === 'revenue' && revenueQuery.data && (
            <View>
              <View className="flex-row mb-3">
                <StatCard
                  label="Total Revenue"
                  value={formatCurrency(revenueQuery.data.totalRevenue)}
                  icon="cash"
                  color="#059669"
                />
                <StatCard
                  label="This Month"
                  value={formatCurrency(revenueQuery.data.monthlyRevenue)}
                  icon="trending-up"
                  color="#6366f1"
                />
              </View>

              <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2 mt-4">
                Top Plans by Revenue
              </Text>
              {revenueQuery.data.topPlans.length === 0 ? (
                <EmptyState message="No revenue data available yet" />
              ) : (
                revenueQuery.data.topPlans.map((plan, i) => (
                  <View key={i} className="bg-white rounded-lg p-4 mb-2 border border-gray-200">
                    <View className="flex-row justify-between">
                      <Text className="text-gray-900 font-medium">{plan.name}</Text>
                      <Text className="text-gray-900 font-semibold">
                        {formatCurrency(plan.revenue)}
                      </Text>
                    </View>
                    <Text className="text-gray-500 text-sm mt-1">
                      {plan.count} subscription{plan.count !== 1 ? 's' : ''}
                    </Text>
                  </View>
                ))
              )}
            </View>
          )}

          {/* Attendance report */}
          {activeTab === 'attendance' && attendanceQuery.data && (
            <View>
              <View className="flex-row mb-3">
                <StatCard
                  label="Total Check-ins"
                  value={String(attendanceQuery.data.totalCheckins)}
                  icon="people"
                  color="#059669"
                />
                <StatCard
                  label="Avg Daily"
                  value={String(attendanceQuery.data.avgDaily)}
                  icon="bar-chart"
                  color="#f59e0b"
                />
              </View>

              <View className="bg-white rounded-lg p-4 mb-3 border border-gray-200">
                <View className="flex-row items-center">
                  <Ionicons name="time" size={20} color="#6366f1" />
                  <Text className="text-gray-500 ml-2">Peak Hour</Text>
                  <Text className="text-gray-900 font-semibold ml-auto">
                    {attendanceQuery.data.peakHour}
                  </Text>
                </View>
              </View>

              <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2 mt-4">
                Top Classes by Attendance
              </Text>
              {attendanceQuery.data.topClasses.length === 0 ? (
                <EmptyState message="No attendance data available yet" />
              ) : (
                attendanceQuery.data.topClasses.map((cls, i) => (
                  <View key={i} className="bg-white rounded-lg p-4 mb-2 border border-gray-200">
                    <View className="flex-row justify-between">
                      <Text className="text-gray-900 font-medium">{cls.name}</Text>
                      <Text className="text-gray-900 font-semibold">{cls.attendance} visits</Text>
                    </View>
                  </View>
                ))
              )}
            </View>
          )}

          {/* Membership health report */}
          {activeTab === 'memberships' && membershipQuery.data && (
            <View>
              <View className="flex-row mb-3">
                <StatCard
                  label="Active Members"
                  value={String(membershipQuery.data.totalActive)}
                  icon="person"
                  color="#059669"
                />
                <StatCard
                  label="New This Month"
                  value={String(membershipQuery.data.newThisMonth)}
                  icon="add-circle"
                  color="#6366f1"
                />
              </View>

              <View className="flex-row mb-3">
                <StatCard
                  label="Expiring Soon"
                  value={String(membershipQuery.data.expiringThisMonth)}
                  icon="warning"
                  color="#f59e0b"
                />
                <StatCard
                  label="Churn Rate"
                  value={`${membershipQuery.data.churnRate.toFixed(1)}%`}
                  icon="trending-down"
                  color="#ef4444"
                />
              </View>

              <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2 mt-4">
                Membership Breakdown
              </Text>
              {membershipQuery.data.breakdown.length === 0 ? (
                <EmptyState message="No membership data available yet" />
              ) : (
                membershipQuery.data.breakdown.map((item, i) => (
                  <View key={i} className="bg-white rounded-lg p-4 mb-2 border border-gray-200">
                    <View className="flex-row justify-between items-center">
                      <Text className="text-gray-900 font-medium">{item.plan}</Text>
                      <Text className="text-gray-900 font-semibold">{item.count}</Text>
                    </View>
                    <View className="mt-2 bg-gray-200 rounded-full h-2">
                      <View
                        className="bg-emerald-500 rounded-full h-2"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </View>
                    <Text className="text-gray-500 text-xs mt-1">{item.percentage}% of total</Text>
                  </View>
                ))
              )}
            </View>
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
      <View className="bg-white rounded-lg p-4 border border-gray-200">
        <Ionicons name={icon} size={24} color={color} />
        <Text className="text-xl font-bold text-gray-900 mt-2">{value}</Text>
        <Text className="text-xs text-gray-500 mt-1">{label}</Text>
      </View>
    </View>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <View className="bg-white rounded-lg p-6 border border-gray-200 items-center">
      <Ionicons name="analytics-outline" size={32} color="#d1d5db" />
      <Text className="text-gray-400 mt-2">{message}</Text>
    </View>
  );
}
