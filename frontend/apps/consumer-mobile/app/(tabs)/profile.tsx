/**
 * Profile tab - profile management and settings.
 *
 * Displays consumer profile information, notification preferences,
 * and provides logout functionality.
 */

import { useState } from 'react';
import { View, Text, ScrollView, Pressable, Switch, Alert } from 'react-native';
import { router } from 'expo-router';
import { useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import * as Linking from 'expo-linking';
import { getConsumerProfile, clearAuth } from '../../lib/auth';
import { clearQrCache } from '../../lib/qr-cache';

export default function ProfileTab() {
  const queryClient = useQueryClient();
  const profile = getConsumerProfile();
  const legalBaseUrl = process.env.EXPO_PUBLIC_LEGAL_BASE_URL ?? 'https://studioloop.com';

  // Notification preferences (stored in state, would sync with API)
  const [pushEnabled, setPushEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [whatsappEnabled, setWhatsappEnabled] = useState(false);

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Sign Out',
        style: 'destructive',
        onPress: () => {
          clearAuth();
          clearQrCache();
          queryClient.clear();
          router.replace('/(auth)/login');
        },
      },
    ]);
  };

  const openExternalLink = async (path: string) => {
    const url = `${legalBaseUrl.replace(/\/$/, '')}${path}`;
    const supported = await Linking.canOpenURL(url);
    if (!supported) {
      Alert.alert('Unable to open link', 'Please try again later.');
      return;
    }
    await Linking.openURL(url);
  };

  const MenuRow = ({
    icon,
    label,
    value,
    onPress,
  }: {
    icon: keyof typeof Ionicons.glyphMap;
    label: string;
    value?: string;
    onPress?: () => void;
  }) => (
    <Pressable
      className="flex-row items-center py-3 px-4 bg-[#1a1a1a]"
      onPress={onPress}
      disabled={!onPress}
    >
      <Ionicons name={icon} size={22} color="#6b7280" />
      <Text className="flex-1 ml-3 text-gray-50">{label}</Text>
      {value && <Text className="text-gray-500 mr-2">{value}</Text>}
      {onPress && <Ionicons name="chevron-forward" size={18} color="#d1d5db" />}
    </Pressable>
  );

  const ToggleRow = ({
    icon,
    label,
    value,
    onValueChange,
  }: {
    icon: keyof typeof Ionicons.glyphMap;
    label: string;
    value: boolean;
    onValueChange: (val: boolean) => void;
  }) => (
    <View className="flex-row items-center py-3 px-4 bg-[#1a1a1a]">
      <Ionicons name={icon} size={22} color="#6b7280" />
      <Text className="flex-1 ml-3 text-gray-50">{label}</Text>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#d1d5db', true: '#818cf8' }}
        thumbColor={value ? '#FF6B4A' : '#f4f4f5'}
      />
    </View>
  );

  return (
    <ScrollView className="flex-1 bg-[#0a0a0a]">
      {/* Profile header */}
      <View className="bg-[#1a1a1a] px-4 py-6 items-center border-b border-[#2a2a2a]">
        <View className="w-20 h-20 rounded-full bg-coral-100 items-center justify-center mb-3">
          <Text className="text-2xl font-bold text-coral-600">
            {profile?.name
              ? profile.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
              : '?'}
          </Text>
        </View>
        <Text className="text-xl font-bold text-gray-50">{profile?.name ?? 'Consumer'}</Text>
        <Text className="text-gray-500 mt-1">{profile?.email ?? ''}</Text>
      </View>

      {/* Account section */}
      <View className="mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide px-4 mb-2">
          Account
        </Text>
        <View className="border-t border-b border-[#2a2a2a]">
          <MenuRow
            icon="person-outline"
            label="Edit Profile"
            onPress={() => router.push('/(tabs)/memberships')}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <MenuRow
            icon="lock-closed-outline"
            label="Change Password"
            onPress={() => {
              router.push('/(auth)/forgot-password');
            }}
          />
        </View>
      </View>

      {/* Notifications section */}
      <View className="mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide px-4 mb-2">
          Notifications
        </Text>
        <View className="border-t border-b border-[#2a2a2a]">
          <ToggleRow
            icon="notifications-outline"
            label="Push Notifications"
            value={pushEnabled}
            onValueChange={setPushEnabled}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <ToggleRow
            icon="mail-outline"
            label="Email Notifications"
            value={emailEnabled}
            onValueChange={setEmailEnabled}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <ToggleRow
            icon="chatbubble-outline"
            label="WhatsApp Notifications"
            value={whatsappEnabled}
            onValueChange={setWhatsappEnabled}
          />
        </View>
      </View>

      {/* Support section */}
      <View className="mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide px-4 mb-2">
          Support
        </Text>
        <View className="border-t border-b border-[#2a2a2a]">
          <MenuRow
            icon="help-circle-outline"
            label="Help & FAQ"
            onPress={() => {
              Alert.alert(
                'Help & FAQ',
                'Support is available at support@studioloop.com',
              );
            }}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <MenuRow
            icon="document-text-outline"
            label="Privacy Policy"
            onPress={() => void openExternalLink('/privacy')}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <MenuRow
            icon="document-text-outline"
            label="Terms of Service"
            onPress={() => void openExternalLink('/terms')}
          />
        </View>
      </View>

      {/* Sign out */}
      <View className="mt-6 mb-8">
        <Pressable
          className="mx-4 py-3 bg-[#1a1a1a] border border-red-300 rounded-lg"
          onPress={handleLogout}
        >
          <Text className="text-red-600 text-center font-semibold">Sign Out</Text>
        </Pressable>
      </View>

      {/* App version */}
      <Text className="text-center text-gray-400 text-xs mb-8">StudioLoop v1.0.0</Text>
    </ScrollView>
  );
}
