/**
 * QR code display screen for consumer check-in.
 */

import { useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import QRCode from 'react-native-qrcode-svg';
import { bookingsGetConsumerQr } from '@sl/api-client';
import { getConsumerProfile } from '../../lib/auth';
import { getAuthHeaders } from '../../lib/apiAuth';
import { cacheQrData, getCachedQrData, getCachedQrMeta } from '../../lib/qr-cache';

export default function QrCodeTab() {
  const profile = getConsumerProfile();
  const cachedQr = getCachedQrData();
  const cachedMeta = getCachedQrMeta();

  const qrQuery = useQuery({
    queryKey: ['consumer', 'qr-data'],
    queryFn: async () => {
      const response = await bookingsGetConsumerQr({ headers: getAuthHeaders(), throwOnError: true });
      return response.data ?? null;
    },
    enabled: !!profile,
  });

  useEffect(() => {
    if (qrQuery.data && profile) {
      cacheQrData({
        consumerId: profile.id,
        membershipId: undefined,
        token: qrQuery.data.token,
        updatedAt: new Date().toISOString(),
      });
    }
  }, [qrQuery.data, profile]);

  const qrValue = qrQuery.data?.token ?? cachedQr;

  if (!profile) {
    return (
      <View className="flex-1 bg-[#0a0a0a] items-center justify-center px-6">
        <Text className="text-gray-500 text-lg text-center">
          Please log in to view your QR code
        </Text>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-[#0a0a0a] items-center justify-center px-6">
      <View className="bg-[#1a1a1a] rounded-2xl p-8 shadow-sm border border-[#2a2a2a] items-center">
        <Text className="text-xl font-bold text-gray-50 mb-2">Your Check-in Code</Text>
        <Text className="text-gray-500 text-sm mb-6 text-center">
          Show this QR code at the gym for check-in
        </Text>

        {qrValue ? (
          <View className="p-4 bg-[#1a1a1a] rounded-lg">
            <QRCode value={qrValue} size={220} backgroundColor="#ffffff" color="#1f2937" />
          </View>
        ) : (
          <View className="w-56 h-56 items-center justify-center">
            <ActivityIndicator size="large" color="#FF6B4A" />
            <Text className="text-gray-400 text-sm mt-4">Loading QR code...</Text>
          </View>
        )}

        <View className="mt-6 items-center">
          <Text className="text-gray-50 font-semibold">{profile.name}</Text>
          <Text className="text-gray-500 text-sm">{profile.email}</Text>
        </View>

        {cachedMeta && (
          <Text className="text-gray-400 text-xs mt-4">
            Last updated: {new Date(cachedMeta.updatedAt).toLocaleString('en-ZA')}
          </Text>
        )}

        <View className="mt-4 bg-green-50 px-4 py-2 rounded-full">
          <Text className="text-green-700 text-xs font-medium">
            {qrQuery.data ? 'Online' : cachedQr ? 'Available offline' : 'Online only'}
          </Text>
        </View>
      </View>
    </View>
  );
}
