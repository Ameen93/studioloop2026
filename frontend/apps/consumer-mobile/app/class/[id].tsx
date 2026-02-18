/**
 * Class detail screen with booking functionality.
 *
 * Displays full class information and allows consumers
 * to book a spot in the class.
 */

import { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  Pressable,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';

// Placeholder types until API client types are generated
interface ClassDetail {
  id: string;
  name: string;
  description: string;
  gymName: string;
  gymAddress: string;
  instructorName: string;
  startTime: string;
  endTime: string;
  duration: number;
  spotsAvailable: number;
  totalSpots: number;
  priceZar: number;
  category: string;
  requirements: string;
  cancellationPolicy: string;
}

export default function ClassDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [isBooking, setIsBooking] = useState(false);

  const classQuery = useQuery<ClassDetail>({
    queryKey: ['class', id],
    queryFn: async () => {
      // TODO: Replace with actual API call
      // e.g., marketplaceGetClass({ path: { class_id: id } })
      throw new Error('Not implemented');
    },
    enabled: !!id,
  });

  const bookMutation = useMutation({
    mutationFn: async () => {
      // TODO: Replace with actual API call
      // e.g., consumerBookingsCreateBooking({ body: { class_session_id: id } })
      setIsBooking(true);
    },
    onSuccess: () => {
      setIsBooking(false);
      queryClient.invalidateQueries({ queryKey: ['consumer', 'bookings'] });
      Alert.alert('Booked!', 'Your spot has been reserved.', [
        { text: 'OK', onPress: () => router.back() },
      ]);
    },
    onError: () => {
      setIsBooking(false);
      Alert.alert('Booking Failed', 'Unable to book this class. Please try again.');
    },
  });

  const formatCurrency = (amount: number) =>
    `R ${amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}`;

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
      <View className="flex-1 bg-gray-50 items-center justify-center">
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  if (classQuery.isError || !classQuery.data) {
    return (
      <View className="flex-1 bg-gray-50 items-center justify-center px-6">
        <Ionicons name="alert-circle-outline" size={48} color="#d1d5db" />
        <Text className="text-gray-500 text-lg mt-4 mb-2">Class not found</Text>
        <Text className="text-gray-400 text-center mb-4">
          This class may no longer be available
        </Text>
        <Pressable className="bg-indigo-600 rounded-lg py-3 px-6" onPress={() => router.back()}>
          <Text className="text-white font-semibold">Go Back</Text>
        </Pressable>
      </View>
    );
  }

  const classData = classQuery.data;

  return (
    <View className="flex-1 bg-gray-50">
      <ScrollView contentContainerClassName="pb-24">
        {/* Header */}
        <View className="bg-white px-4 py-6 border-b border-gray-200">
          <View className="flex-row justify-between items-start">
            <View className="flex-1 mr-3">
              <View className="bg-indigo-50 px-3 py-1 rounded-full self-start mb-2">
                <Text className="text-indigo-700 text-sm font-medium">{classData.category}</Text>
              </View>
              <Text className="text-2xl font-bold text-gray-900">{classData.name}</Text>
            </View>
            <Text className="text-2xl font-bold text-indigo-600">
              {formatCurrency(classData.priceZar)}
            </Text>
          </View>
        </View>

        {/* Details */}
        <View className="bg-white mt-2 px-4 py-4 border-t border-b border-gray-200">
          <DetailRow
            icon="business-outline"
            label="Gym"
            value={classData.gymName}
          />
          <DetailRow
            icon="location-outline"
            label="Address"
            value={classData.gymAddress}
          />
          <DetailRow
            icon="person-outline"
            label="Instructor"
            value={classData.instructorName}
          />
          <DetailRow
            icon="calendar-outline"
            label="Date"
            value={formatDate(classData.startTime)}
          />
          <DetailRow
            icon="time-outline"
            label="Time"
            value={`${formatTime(classData.startTime)} - ${formatTime(classData.endTime)}`}
          />
          <DetailRow
            icon="timer-outline"
            label="Duration"
            value={`${classData.duration} minutes`}
          />
          <DetailRow
            icon="people-outline"
            label="Availability"
            value={`${classData.spotsAvailable} of ${classData.totalSpots} spots available`}
          />
        </View>

        {/* Description */}
        <View className="bg-white mt-2 px-4 py-4 border-t border-b border-gray-200">
          <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
            About this class
          </Text>
          <Text className="text-gray-700 leading-5">{classData.description}</Text>
        </View>

        {/* Requirements */}
        {classData.requirements && (
          <View className="bg-white mt-2 px-4 py-4 border-t border-b border-gray-200">
            <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
              Requirements
            </Text>
            <Text className="text-gray-700 leading-5">{classData.requirements}</Text>
          </View>
        )}

        {/* Cancellation policy */}
        {classData.cancellationPolicy && (
          <View className="bg-white mt-2 px-4 py-4 border-t border-b border-gray-200">
            <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
              Cancellation Policy
            </Text>
            <Text className="text-gray-700 leading-5">{classData.cancellationPolicy}</Text>
          </View>
        )}
      </ScrollView>

      {/* Fixed booking button */}
      <View className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-4">
        <Pressable
          className={`w-full py-4 rounded-lg ${
            classData.spotsAvailable === 0
              ? 'bg-gray-300'
              : isBooking
                ? 'bg-indigo-400'
                : 'bg-indigo-600'
          }`}
          onPress={() => bookMutation.mutate()}
          disabled={classData.spotsAvailable === 0 || isBooking}
        >
          {isBooking ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="text-white text-center font-bold text-lg">
              {classData.spotsAvailable === 0 ? 'Class Full' : `Book for ${formatCurrency(classData.priceZar)}`}
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
      <Text className="text-sm text-gray-900 flex-1">{value}</Text>
    </View>
  );
}
