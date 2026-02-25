/**
 * Check-in tab - QR scanner + manual search fallback.
 */

import { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  FlatList,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import {
  bookingsManualCheckIn,
  bookingsScanQr,
  bookingsSearchMembersForCheckIn,
} from '@sl/api-client';
import type { SearchResult } from '@sl/api-client';
import { getGymId } from '../../lib/auth';
import { getAuthHeaders } from '../../lib/apiAuth';
import { queueCheckin, getPendingCount } from '../../lib/offline-checkin';

type CheckinMode = 'qr' | 'manual';

export default function CheckinTab() {
  const [mode, setMode] = useState<CheckinMode>('qr');
  const [searchQuery, setSearchQuery] = useState('');
  const [scannedData, setScannedData] = useState<string | null>(null);
  const [pendingCount, setPendingCount] = useState(0);
  const [permission, requestPermission] = useCameraPermissions();
  const queryClient = useQueryClient();
  const gymId = getGymId();

  useEffect(() => {
    void getPendingCount().then(setPendingCount);
  }, []);

  const searchResults = useQuery({
    queryKey: ['gym', 'members', 'search', searchQuery],
    queryFn: async () => {
      const response = await bookingsSearchMembersForCheckIn({
        headers: getAuthHeaders(),
        query: { q: searchQuery },
      });
      return response.data ?? [];
    },
    enabled: mode === 'manual' && searchQuery.length >= 2,
  });

  const checkinMutation = useMutation({
    mutationFn: async (params: { consumerId?: string; method: 'qr' | 'manual'; qrToken?: string }) => {
      try {
        if (params.method === 'qr' && params.qrToken) {
          await bookingsScanQr({
            headers: getAuthHeaders(),
            body: { token: params.qrToken },
          });
          return { offline: false };
        }

        if (!params.consumerId) {
          throw new Error('Missing consumer id for manual check-in');
        }

        await bookingsManualCheckIn({
          headers: getAuthHeaders(),
          body: { consumer_id: params.consumerId },
        });
        return { offline: false };
      } catch {
        if (gymId && params.consumerId) {
          await queueCheckin({
            consumerId: params.consumerId,
            gymId,
            method: params.method,
          });
          const count = await getPendingCount();
          setPendingCount(count);
          return { offline: true };
        }
        throw new Error('No gym ID available');
      }
    },
    onSuccess: (result) => {
      Alert.alert(
        `Check-in ${result.offline ? 'Queued' : 'Successful'}`,
        result.offline
          ? 'Check-in saved offline and will sync when connected.'
          : 'Member has been checked in.',
      );
      void queryClient.invalidateQueries({ queryKey: ['gym', 'dashboard'] });
      setScannedData(null);
    },
    onError: () => {
      Alert.alert('Check-in Failed', 'Unable to process check-in. Please try again.');
    },
  });

  const handleQrScanned = (data: string) => {
    if (scannedData) return;
    setScannedData(data);

    try {
      const parsed = JSON.parse(data) as { type?: string; consumer_id?: string };
      if (parsed.type === 'studioloop_checkin' && parsed.consumer_id) {
        checkinMutation.mutate({
          consumerId: parsed.consumer_id,
          method: 'qr',
          qrToken: data,
        });
      } else {
        checkinMutation.mutate({
          consumerId: parsed.consumer_id,
          method: 'qr',
          qrToken: data,
        });
      }
    } catch {
      checkinMutation.mutate({
        method: 'qr',
        qrToken: data,
      });
    }
  };

  const handleManualCheckin = (member: SearchResult) => {
    const fullName = `${member.first_name} ${member.last_name}`.trim();
    Alert.alert('Confirm Check-in', `Check in ${fullName}?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Check In',
        onPress: () => checkinMutation.mutate({ consumerId: member.consumer_id, method: 'manual' }),
      },
    ]);
  };

  if (mode === 'qr' && !permission?.granted) {
    return (
      <View className="flex-1 bg-gray-50 items-center justify-center px-6">
        <Ionicons name="camera-outline" size={64} color="#d1d5db" />
        <Text className="text-lg font-semibold text-gray-900 mt-4 mb-2">Camera Permission</Text>
        <Text className="text-gray-500 text-center mb-6">
          Camera access is needed to scan member QR codes for check-in
        </Text>
        <Pressable className="bg-emerald-600 rounded-lg py-3 px-6" onPress={requestPermission}>
          <Text className="text-white font-semibold">Grant Permission</Text>
        </Pressable>
        <Pressable className="mt-4" onPress={() => setMode('manual')}>
          <Text className="text-emerald-600 font-medium">Use manual check-in instead</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-gray-50">
      <View className="flex-row bg-white border-b border-gray-200 px-4 py-2">
        <Pressable
          className={`flex-1 py-2 rounded-lg mr-1 ${mode === 'qr' ? 'bg-emerald-600' : 'bg-gray-100'}`}
          onPress={() => setMode('qr')}
        >
          <Text className={`text-center font-medium ${mode === 'qr' ? 'text-white' : 'text-gray-600'}`}>
            QR Scanner
          </Text>
        </Pressable>
        <Pressable
          className={`flex-1 py-2 rounded-lg ml-1 ${mode === 'manual' ? 'bg-emerald-600' : 'bg-gray-100'}`}
          onPress={() => setMode('manual')}
        >
          <Text className={`text-center font-medium ${mode === 'manual' ? 'text-white' : 'text-gray-600'}`}>
            Manual Search
          </Text>
        </Pressable>
      </View>

      {pendingCount > 0 && (
        <View className="mx-4 mt-2 bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2 flex-row items-center">
          <Ionicons name="cloud-offline-outline" size={16} color="#d97706" />
          <Text className="text-yellow-700 text-sm ml-2">
            {pendingCount} offline check-in{pendingCount > 1 ? 's' : ''} pending sync
          </Text>
        </View>
      )}

      {mode === 'qr' ? (
        <View className="flex-1">
          <CameraView
            style={{ flex: 1 }}
            facing="back"
            barcodeScannerSettings={{
              barcodeTypes: ['qr'],
            }}
            onBarcodeScanned={scannedData ? undefined : (result) => handleQrScanned(result.data)}
          />

          <View className="absolute inset-0 items-center justify-center">
            <View className="w-64 h-64 border-2 border-white rounded-2xl opacity-60" />
          </View>

          <View className="absolute bottom-8 left-0 right-0 items-center">
            <Text className="text-white text-lg font-medium bg-black/50 px-4 py-2 rounded-lg">
              Point at member's QR code
            </Text>
          </View>

          {checkinMutation.isPending && (
            <View className="absolute inset-0 bg-black/50 items-center justify-center">
              <ActivityIndicator size="large" color="#fff" />
              <Text className="text-white mt-4 font-medium">Processing check-in...</Text>
            </View>
          )}
        </View>
      ) : (
        <View className="flex-1 px-4 pt-4">
          <View className="flex-row items-center bg-white border border-gray-300 rounded-lg px-3">
            <Ionicons name="search" size={20} color="#9ca3af" />
            <TextInput
              className="flex-1 py-3 px-2 text-gray-900"
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

          <FlatList
            data={searchResults.data ?? []}
            keyExtractor={(item) => item.consumer_id}
            className="mt-3"
            renderItem={({ item }) => (
              <Pressable
                className="bg-white rounded-lg p-4 mb-2 border border-gray-200 flex-row items-center"
                onPress={() => handleManualCheckin(item)}
              >
                <View className="w-10 h-10 rounded-full bg-emerald-100 items-center justify-center">
                  <Text className="text-emerald-600 font-bold">
                    {[item.first_name, item.last_name]
                      .map((n) => n[0] ?? '')
                      .join('')
                      .toUpperCase()}
                  </Text>
                </View>
                <View className="flex-1 ml-3">
                  <Text className="text-gray-900 font-semibold">
                    {item.first_name} {item.last_name}
                  </Text>
                  <Text className="text-gray-500 text-sm">{item.phone ?? 'No phone'}</Text>
                </View>
              </Pressable>
            )}
            ListEmptyComponent={
              searchQuery.length >= 2 && !searchResults.isLoading ? (
                <View className="items-center py-8">
                  <Text className="text-gray-500">No members found</Text>
                </View>
              ) : searchQuery.length < 2 ? (
                <View className="items-center py-8">
                  <Ionicons name="search" size={48} color="#d1d5db" />
                  <Text className="text-gray-400 mt-4">Type at least 2 characters to search</Text>
                </View>
              ) : null
            }
          />
        </View>
      )}
    </View>
  );
}
