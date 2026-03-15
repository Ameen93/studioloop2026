/**
 * Studio profile screen with membership plans and enrollment.
 */

import { useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import {
  marketplaceViewMarketplaceGymProfile,
  staffMembershipsListConsumerMemberships,
  staffMembershipsListPublicMembershipPlans,
  staffMembershipsEnrollMembership,
  staffMembershipsAcceptDigitalWaiver,
} from '@sl/api-client';
import type { MembershipPlanPublic } from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

function formatPrice(cents: number): string {
  return `R ${(cents / 100).toFixed(2)}`;
}

export default function StudioProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [selectedPlan, setSelectedPlan] = useState<MembershipPlanPublic | null>(null);
  const [waiverAccepted, setWaiverAccepted] = useState(false);

  const profileQuery = useQuery({
    queryKey: ['gym-profile', id],
    queryFn: async () => {
      if (!id) return null;
      const response = await marketplaceViewMarketplaceGymProfile({
        path: { gym_id: id },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
    enabled: !!id,
  });

  const gymSlug = (profileQuery.data as Record<string, unknown>)?.slug as string | undefined;

  const plansQuery = useQuery({
    queryKey: ['gym-membership-plans', gymSlug],
    queryFn: async () => {
      if (!gymSlug) return [];
      const response = await staffMembershipsListPublicMembershipPlans({
        path: { gym_slug: gymSlug },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
    enabled: Boolean(gymSlug),
  });

  const myMembershipsQuery = useQuery({
    queryKey: ['consumer', 'memberships'],
    queryFn: async () => {
      const response = await staffMembershipsListConsumerMemberships({
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });

  const existingMembership = (myMembershipsQuery.data ?? []).find(
    (m) => m.gym_id === id && m.status === 'active',
  );

  const enrollMutation = useMutation({
    mutationFn: async (plan: MembershipPlanPublic) => {
      const enrollResponse = await staffMembershipsEnrollMembership({
        body: {
          gym_id: plan.gym_id,
          membership_plan_id: plan.id,
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });

      if (plan.waiver_text && enrollResponse.data) {
        await staffMembershipsAcceptDigitalWaiver({
          body: { gym_membership_id: enrollResponse.data.id },
          headers: getAuthHeaders(),
          throwOnError: true,
        });
      }

      return enrollResponse.data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['consumer', 'memberships'] });
      Alert.alert(
        'Welcome!',
        `You're now a member of ${profileQuery.data?.name}!`,
        [{ text: 'Go Home', onPress: () => router.replace('/') }],
      );
    },
    onError: () => {
      Alert.alert('Enrollment Failed', 'Could not complete enrollment. Please try again.');
    },
  });

  const handleEnroll = (plan: MembershipPlanPublic) => {
    if (plan.waiver_text && !waiverAccepted) {
      Alert.alert('Waiver Required', 'Please accept the waiver before enrolling.');
      return;
    }
    enrollMutation.mutate(plan);
  };

  const profile = profileQuery.data;
  const plans = (plansQuery.data ?? []).filter((p) => p.is_active);

  if (profileQuery.isLoading) {
    return (
      <View className="flex-1 bg-[#0a0a0a] items-center justify-center">
        <ActivityIndicator size="large" color="#FF6B4A" />
      </View>
    );
  }

  if (profileQuery.isError || !profile) {
    return (
      <View className="flex-1 bg-[#0a0a0a] items-center justify-center px-6">
        <Ionicons name="alert-circle-outline" size={48} color="#d1d5db" />
        <Text className="text-gray-500 text-lg mt-4 mb-2">Studio not found</Text>
        <Pressable className="bg-coral-600 rounded-lg py-3 px-6" onPress={() => router.back()}>
          <Text className="text-white font-semibold">Go Back</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-[#0a0a0a]">
      <ScrollView contentContainerClassName="pb-24">
        {/* Studio Header */}
        <View className="bg-[#1a1a1a] px-4 py-6 border-b border-[#2a2a2a]">
          <View className="flex-row justify-between items-start">
            <View className="flex-1 mr-3">
              <Text className="text-2xl font-bold text-gray-50">{profile.name}</Text>
              {profile.tagline && (
                <Text className="text-sm text-gray-400 mt-1">{profile.tagline}</Text>
              )}
            </View>
            {existingMembership && (
              <View className="bg-green-900 px-3 py-1 rounded-full">
                <Text className="text-green-300 text-xs font-medium">Member</Text>
              </View>
            )}
          </View>

          {profile.description && (
            <Text className="text-gray-400 mt-3 leading-5">{profile.description}</Text>
          )}

          {profile.address_line1 && (
            <View className="flex-row items-center mt-3">
              <Ionicons name="location-outline" size={14} color="#6b7280" />
              <Text className="text-sm text-gray-500 ml-1">
                {[profile.address_line1, profile.city, profile.province]
                  .filter(Boolean)
                  .join(', ')}
              </Text>
            </View>
          )}
        </View>

        {/* Already a member badge */}
        {existingMembership && (
          <View className="mx-4 mt-4 bg-green-900/30 border border-green-800 rounded-lg p-4">
            <Text className="text-green-300 font-medium">
              You're a member of {profile.name}
            </Text>
            <Text className="text-green-400 text-sm mt-1">
              Your {existingMembership.membership_tier} membership is active.
            </Text>
          </View>
        )}

        {/* Membership Plans */}
        {plans.length > 0 && !existingMembership && (
          <View className="px-4 mt-4">
            <Text className="text-lg font-semibold text-gray-50 mb-3">Membership Plans</Text>
            {plans.map((plan) => (
              <Pressable
                key={plan.id}
                className={`bg-[#1a1a1a] rounded-lg p-4 mb-3 border ${
                  selectedPlan?.id === plan.id ? 'border-coral-500' : 'border-[#2a2a2a]'
                }`}
                onPress={() => {
                  setSelectedPlan(plan);
                  setWaiverAccepted(false);
                }}
              >
                <View className="flex-row justify-between items-start">
                  <View className="flex-1 mr-3">
                    <Text className="text-lg font-semibold text-gray-50">{plan.name}</Text>
                    <Text className="text-sm text-gray-400 capitalize mt-0.5">{plan.tier}</Text>
                  </View>
                  <Text className="text-xl font-bold text-coral-500">
                    {formatPrice(plan.price_cents)}
                    <Text className="text-sm font-normal text-gray-500">
                      /{plan.billing_cycle === 'weekly' ? 'wk' : 'mo'}
                    </Text>
                  </Text>
                </View>

                {plan.description && (
                  <Text className="text-sm text-gray-400 mt-2">{plan.description}</Text>
                )}

                {plan.benefits.length > 0 && (
                  <View className="mt-3">
                    {plan.benefits.map((benefit, i) => (
                      <View key={i} className="flex-row items-center mt-1">
                        <Ionicons name="checkmark-circle" size={14} color="#22c55e" />
                        <Text className="text-sm text-gray-300 ml-2">{benefit}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </Pressable>
            ))}
          </View>
        )}

        {/* Waiver section */}
        {selectedPlan?.waiver_text && !existingMembership && (
          <View className="px-4 mt-2">
            <View className="bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a]">
              <Text className="text-sm font-medium text-gray-300 mb-2">Terms & Waiver</Text>
              <Text className="text-xs text-gray-500 mb-3 leading-4">
                {selectedPlan.waiver_text}
              </Text>
              <Pressable
                className="flex-row items-center"
                onPress={() => setWaiverAccepted(!waiverAccepted)}
              >
                <Ionicons
                  name={waiverAccepted ? 'checkbox' : 'square-outline'}
                  size={20}
                  color={waiverAccepted ? '#FF6B4A' : '#6b7280'}
                />
                <Text className="text-sm text-gray-300 ml-2">I agree to the terms</Text>
              </Pressable>
            </View>
          </View>
        )}

        {/* Upcoming Classes */}
        {profile.upcoming_marketplace_classes.length > 0 && (
          <View className="px-4 mt-4">
            <Text className="text-lg font-semibold text-gray-50 mb-3">Upcoming Classes</Text>
            {profile.upcoming_marketplace_classes.map((cls) => (
              <Pressable
                key={cls.session_id}
                className="bg-[#1a1a1a] rounded-lg p-4 mb-3 border border-[#2a2a2a]"
                onPress={() => router.push(`/class/${cls.session_id}`)}
              >
                <View className="flex-row justify-between items-center">
                  <View className="flex-1 mr-3">
                    <Text className="font-semibold text-gray-50">{cls.title}</Text>
                    <Text className="text-sm text-gray-500 mt-1">
                      {new Date(cls.start_time).toLocaleDateString('en-ZA', {
                        weekday: 'short',
                        day: 'numeric',
                        month: 'short',
                      })}{' '}
                      at{' '}
                      {new Date(cls.start_time).toLocaleTimeString('en-ZA', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Text>
                  </View>
                  <View className="items-end">
                    <Text className="font-semibold text-gray-50">{formatPrice(cls.price_cents)}</Text>
                    <Text className="text-xs text-green-500">{cls.spots_remaining} spots</Text>
                  </View>
                </View>
              </Pressable>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Enroll CTA */}
      {selectedPlan && !existingMembership && (
        <View className="absolute bottom-0 left-0 right-0 bg-[#1a1a1a] border-t border-[#2a2a2a] px-4 py-4">
          <Pressable
            className={`w-full py-4 rounded-lg ${
              enrollMutation.isPending ? 'bg-coral-400' : 'bg-coral-600'
            }`}
            onPress={() => handleEnroll(selectedPlan)}
            disabled={enrollMutation.isPending}
          >
            {enrollMutation.isPending ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="text-white text-center font-bold text-lg">
                Enroll — {formatPrice(selectedPlan.price_cents)}
                /{selectedPlan.billing_cycle === 'weekly' ? 'wk' : 'mo'}
              </Text>
            )}
          </Pressable>
        </View>
      )}
    </View>
  );
}
