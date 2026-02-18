/**
 * QR Code display screen for consumer check-in.
 *
 * Displays a QR code that gym staff can scan for check-in.
 * Works offline by caching QR data in MMKV.
 */

import { useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import QRCode from 'react-native-qrcode-svg';
import { getConsumerProfile } from '../../lib/auth';
import { cacheQrData, getCachedQrData, getCachedQrMeta } from '../../lib/qr-cache';

export default function QrCodeTab() {
  const profile = getConsumerProfile();
  const cachedQr = getCachedQrData();
  const cachedMeta = getCachedQrMeta();

  // Fetch fresh QR data from consumer profile / memberships
  const qrQuery = useQuery({
    queryKey: ['consumer', 'qr-data'],
    queryFn: async () => {
      // TODO: Replace with actual API call to get consumer's active membership
      // For now, generate QR data from stored profile
      if (!profile) return null;

      const data = {
        consumerId: profile.id,
        membershipId: undefined as string | undefined,
        updatedAt: new Date().toISOString(),
      };

      return data;
    },
    enabled: !!profile,
  });

  // Cache the QR data whenever we get fresh data
  useEffect(() => {
    if (qrQuery.data) {
      cacheQrData(qrQuery.data);
    }
  }, [qrQuery.data]);

  // Use cached QR data if available, otherwise show loading
  const qrValue = cachedQr ?? (qrQuery.data ? JSON.stringify({
    type: 'studioloop_checkin',
    consumer_id: qrQuery.data.consumerId,
    membership_id: qrQuery.data.membershipId,
    ts: qrQuery.data.updatedAt,
  }) : null);

  if (!profile) {
    return (
      <View className="flex-1 bg-gray-50 items-center justify-center px-6">
        <Text className="text-gray-500 text-lg text-center">
          Please log in to view your QR code
        </Text>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-gray-50 items-center justify-center px-6">
      <View className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200 items-center">
        <Text className="text-xl font-bold text-gray-900 mb-2">Your Check-in Code</Text>
        <Text className="text-gray-500 text-sm mb-6 text-center">
          Show this QR code at the gym for check-in
        </Text>

        {qrValue ? (
          <View className="p-4 bg-white rounded-lg">
            <QRCode
              value={qrValue}
              size={220}
              backgroundColor="#ffffff"
              color="#1f2937"
            />
          </View>
        ) : (
          <View className="w-56 h-56 items-center justify-center">
            <ActivityIndicator size="large" color="#6366f1" />
            <Text className="text-gray-400 text-sm mt-4">Loading QR code...</Text>
          </View>
        )}

        <View className="mt-6 items-center">
          <Text className="text-gray-900 font-semibold">{profile.name}</Text>
          <Text className="text-gray-500 text-sm">{profile.email}</Text>
        </View>

        {cachedMeta && (
          <Text className="text-gray-400 text-xs mt-4">
            Last updated: {new Date(cachedMeta.updatedAt).toLocaleString('en-ZA')}
          </Text>
        )}

        <View className="mt-4 bg-green-50 px-4 py-2 rounded-full">
          <Text className="text-green-700 text-xs font-medium">
            {cachedQr ? 'Available offline' : 'Online only'}
          </Text>
        </View>
      </View>
    </View>
  );
}
