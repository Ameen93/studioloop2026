/**
 * Class detail screen with booking functionality.
 */

import { useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import {
  bookingsBookPayPerClass,
  bookingsBookWithMembership,
  bookingsJoinWaitlist,
  marketplaceBookMarketplaceClassWithSubscription,
  marketplaceViewMarketplaceClassDetails,
  staffMembershipsListConsumerMemberships,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

type BookingMethod = 'membership' | 'subscription' | 'pay_per_class';

export default function ClassDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [bookingMethod, setBookingMethod] = useState<BookingMethod>('pay_per_class');

  const classQuery = useQuery({
    queryKey: ['class', id],
    queryFn: async () => {
      if (!id) {
        return null;
      }

      const response = await marketplaceViewMarketplaceClassDetails({
        path: { session_id: id },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data ?? null;
    },
    enabled: !!id,
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

  const bookMutation = useMutation({
    mutationFn: async () => {
      const classData = classQuery.data;
      if (!classData) {
        throw new Error('Missing class details');
      }

      const headers = getAuthHeaders();

      if (classData.spots_remaining === 0) {
        await bookingsJoinWaitlist({
          body: {
            gym_id: classData.gym_id,
            session_id: classData.session_id,
          },
          headers,
          throwOnError: true,
        });
        return 'waitlist';
      }

      if (bookingMethod === 'membership') {
        await bookingsBookWithMembership({
          body: {
            gym_id: classData.gym_id,
            session_id: classData.session_id,
          },
          headers,
          throwOnError: true,
        });
        return 'booked';
      }

      if (bookingMethod === 'subscription') {
        await marketplaceBookMarketplaceClassWithSubscription({
          body: {
            session_id: classData.session_id,
          },
          headers,
          throwOnError: true,
        });
        return 'booked';
      }

      await bookingsBookPayPerClass({
        body: {
          gym_id: classData.gym_id,
          session_id: classData.session_id,
          amount_cents: classData.price_cents,
        },
        headers,
        throwOnError: true,
      });
      return 'booked';
    },
    onSuccess: (mode) => {
      void queryClient.invalidateQueries({ queryKey: ['consumer', 'class-history'] });
      Alert.alert(
        mode === 'waitlist' ? 'Added to waitlist' : 'Booked!',
        mode === 'waitlist'
          ? 'You were added to the waitlist for this class.'
          : 'Your spot has been reserved.',
        [{ text: 'OK', onPress: () => router.back() }],
      );
    },
    onError: () => {
      Alert.alert('Booking Failed', 'Unable to book this class. Please try again.');
    },
  });

  const formatCurrency = (amount: number) =>
    `R ${(amount / 100).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('en-ZA', {
      weekday: 'long',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });

  const formatTime = (dateStr: string) =>
    new Date(dateStr).toLocaleTimeString('en-ZA', {
      hour: '2-digit',
      minute: '2-digit',
    });

  if (classQuery.isLoading) {
    return (
      <View className="flex-1 bg-[#0a0a0a] items-center justify-center">
        <ActivityIndicator size="large" color="#FF6B4A" />
      </View>
    );
  }

  if (classQuery.isError || !classQuery.data) {
    return (
      <View className="flex-1 bg-[#0a0a0a] items-center justify-center px-6">
        <Ionicons name="alert-circle-outline" size={48} color="#d1d5db" />
        <Text className="text-gray-500 text-lg mt-4 mb-2">Class not found</Text>
        <Pressable className="bg-coral-600 rounded-lg py-3 px-6" onPress={() => router.back()}>
          <Text className="text-white font-semibold">Go Back</Text>
        </Pressable>
      </View>
    );
  }

  const classData = classQuery.data;
  const hasMembershipAtGym = (myMembershipsQuery.data ?? []).some(
    (m) => m.gym_id === classData?.gym_id && m.status === 'active',
  );

  return (
    <View className="flex-1 bg-[#0a0a0a]">
      <ScrollView contentContainerClassName="pb-24">
        <View className="bg-[#1a1a1a] px-4 py-6 border-b border-[#2a2a2a]">
          <View className="flex-row justify-between items-start">
            <View className="flex-1 mr-3">
              <View className="bg-coral-50 px-3 py-1 rounded-full self-start mb-2">
                <Text className="text-coral-700 text-sm font-medium">{classData.class_type}</Text>
              </View>
              <Text className="text-2xl font-bold text-gray-50">{classData.title}</Text>
            </View>
            <Text className="text-2xl font-bold text-coral-600">
              {formatCurrency(classData.price_cents)}
            </Text>
          </View>
        </View>

        <View className="bg-[#1a1a1a] mt-2 px-4 py-4 border-t border-b border-[#2a2a2a]">
          <DetailRow icon="business-outline" label="Gym" value={classData.gym_name} />
          <DetailRow
            icon="location-outline"
            label="Address"
            value={[classData.address_line1, classData.city, classData.province].filter(Boolean).join(', ') || '-'}
          />
          <DetailRow icon="person-outline" label="Instructor" value={classData.instructor_name ?? 'TBA'} />
          <DetailRow icon="calendar-outline" label="Date" value={formatDate(classData.start_time)} />
          <DetailRow
            icon="time-outline"
            label="Time"
            value={`${formatTime(classData.start_time)} - ${formatTime(classData.end_time)}`}
          />
          <DetailRow
            icon="timer-outline"
            label="Duration"
            value={`${classData.duration_minutes} minutes`}
          />
          <DetailRow
            icon="people-outline"
            label="Availability"
            value={`${classData.spots_remaining} of ${classData.capacity} spots available`}
          />
        </View>

        {!!classData.description && (
          <View className="bg-[#1a1a1a] mt-2 px-4 py-4 border-t border-b border-[#2a2a2a]">
            <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
              About this class
            </Text>
            <Text className="text-gray-700 leading-5">{classData.description}</Text>
          </View>
        )}

        {!!classData.cancellation_policy && (
          <View className="bg-[#1a1a1a] mt-2 px-4 py-4 border-t border-b border-[#2a2a2a]">
            <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
              Cancellation Policy
            </Text>
            <Text className="text-gray-700 leading-5">{classData.cancellation_policy}</Text>
          </View>
        )}

        {/* Membership CTA */}
        {!hasMembershipAtGym ? (
          <Pressable
            className="bg-coral-900/20 mx-4 mt-2 rounded-lg p-4 border border-coral-800"
            onPress={() => router.push(`/studio/${classData.gym_id}`)}
          >
            <Text className="text-coral-400 font-medium">
              Join {classData.gym_name} to book regularly
            </Text>
            <Text className="text-coral-500 text-sm mt-1">
              View membership plans →
            </Text>
          </Pressable>
        ) : (
          <View className="bg-green-900/20 mx-4 mt-2 rounded-lg p-4 border border-green-800">
            <View className="flex-row items-center">
              <Ionicons name="checkmark-circle" size={16} color="#22c55e" />
              <Text className="text-green-400 font-medium ml-2">
                You're a member at {classData.gym_name}
              </Text>
            </View>
          </View>
        )}

        <View className="bg-[#1a1a1a] mt-2 px-4 py-4 border-t border-b border-[#2a2a2a]">
          <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
            Booking Method
          </Text>

          <Pressable className="flex-row items-center py-2" onPress={() => setBookingMethod('membership')}>
            <Ionicons
              name={bookingMethod === 'membership' ? 'radio-button-on' : 'radio-button-off'}
              size={18}
              color="#4f46e5"
            />
            <Text className="ml-2 text-gray-800">Use gym membership</Text>
          </Pressable>

          <Pressable className="flex-row items-center py-2" onPress={() => setBookingMethod('subscription')}>
            <Ionicons
              name={bookingMethod === 'subscription' ? 'radio-button-on' : 'radio-button-off'}
              size={18}
              color="#4f46e5"
            />
            <Text className="ml-2 text-gray-800">Use marketplace subscription</Text>
          </Pressable>

          <Pressable className="flex-row items-center py-2" onPress={() => setBookingMethod('pay_per_class')}>
            <Ionicons
              name={bookingMethod === 'pay_per_class' ? 'radio-button-on' : 'radio-button-off'}
              size={18}
              color="#4f46e5"
            />
            <Text className="ml-2 text-gray-800">Pay per class</Text>
          </Pressable>
        </View>
      </ScrollView>

      <View className="absolute bottom-0 left-0 right-0 bg-[#1a1a1a] border-t border-[#2a2a2a] px-4 py-4">
        <Pressable
          className={`w-full py-4 rounded-lg ${
            bookMutation.isPending
              ? 'bg-coral-400'
              : classData.spots_remaining === 0
                ? 'bg-orange-500'
                : 'bg-coral-600'
          }`}
          onPress={() => bookMutation.mutate()}
          disabled={bookMutation.isPending}
        >
          {bookMutation.isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="text-white text-center font-bold text-lg">
              {classData.spots_remaining === 0 ? 'Join Waitlist' : `Book for ${formatCurrency(classData.price_cents)}`}
            </Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}

function DetailRow({
  icon,
  label,
  value,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
}) {
  return (
    <View className="flex-row items-center py-2">
      <Ionicons name={icon} size={18} color="#6b7280" />
      <Text className="text-sm text-gray-500 ml-2 w-20">{label}</Text>
      <Text className="text-sm text-gray-50 flex-1">{value}</Text>
    </View>
  );
}
