/**
 * Profile tab - profile management and settings.
 *
 * Displays consumer profile information, notification preferences,
 * and provides logout functionality.
 */

import { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, Pressable, Switch, Alert, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import * as Linking from 'expo-linking';
import {
  notificationsGetPreferences,
  notificationsUpdatePreferences,
} from '@sl/api-client';
import type { PreferencesPublic } from '@sl/api-client';
import { getConsumerProfile, clearAuth, getAccessToken } from '../../lib/auth';
import { clearQrCache } from '../../lib/qr-cache';

export default function ProfileTab() {
  const queryClient = useQueryClient();
  const profile = getConsumerProfile();
  const legalBaseUrl =
    process.env.EXPO_PUBLIC_LEGAL_BASE_URL ?? 'https://studioloop.co.za';

  // Notification preferences — synced with backend API
  const [pushEnabled, setPushEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [whatsappEnabled, setWhatsappEnabled] = useState(false);
  const [prefsLoading, setPrefsLoading] = useState(true);
  // Track whether we successfully loaded prefs from the server.
  // When false, toggles are disabled to prevent overwriting real
  // preferences with fabricated client-side defaults after a fetch failure.
  const [prefsFetched, setPrefsFetched] = useState(false);

  // Derive aggregate toggle values from granular backend preferences
  const applyPreferences = useCallback((prefs: PreferencesPublic) => {
    const pushFields = [
      prefs.booking_push,
      prefs.reminder_push,
      prefs.waitlist_push,
      prefs.payment_push,
      prefs.gym_message_push,
    ];
    const emailFields = [
      prefs.booking_email,
      prefs.reminder_email,
      prefs.waitlist_email,
      prefs.payment_email,
      prefs.gym_message_email,
    ];
    setPushEnabled(pushFields.every(Boolean));
    setEmailEnabled(emailFields.every(Boolean));
    setWhatsappEnabled(prefs.whatsapp_enabled);
  }, []);

  // Fetch preferences on mount
  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setPrefsLoading(false);
      return;
    }

    notificationsGetPreferences({
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (res.data) {
          applyPreferences(res.data);
          setPrefsFetched(true);
        }
      })
      .catch(() => {
        // Leave prefsFetched=false so toggles stay disabled
      })
      .finally(() => setPrefsLoading(false));
  }, [applyPreferences]);

  // Patch preferences on toggle change
  const updatePushPreference = useCallback(
    (val: boolean) => {
      setPushEnabled(val);
      const token = getAccessToken();
      if (!token) return;
      notificationsUpdatePreferences({
        headers: { Authorization: `Bearer ${token}` },
        body: {
          booking_push: val,
          reminder_push: val,
          waitlist_push: val,
          payment_push: val,
          gym_message_push: val,
        },
      }).catch(() =>
        Alert.alert('Error', 'Failed to save notification preferences'),
      );
    },
    [],
  );

  const updateEmailPreference = useCallback(
    (val: boolean) => {
      setEmailEnabled(val);
      const token = getAccessToken();
      if (!token) return;
      notificationsUpdatePreferences({
        headers: { Authorization: `Bearer ${token}` },
        body: {
          booking_email: val,
          reminder_email: val,
          waitlist_email: val,
          payment_email: val,
          gym_message_email: val,
        },
      }).catch(() =>
        Alert.alert('Error', 'Failed to save notification preferences'),
      );
    },
    [],
  );

  const updateWhatsappPreference = useCallback(
    (val: boolean) => {
      setWhatsappEnabled(val);
      const token = getAccessToken();
      if (!token) return;
      notificationsUpdatePreferences({
        headers: { Authorization: `Bearer ${token}` },
        body: { whatsapp_enabled: val },
      }).catch(() =>
        Alert.alert('Error', 'Failed to save notification preferences'),
      );
    },
    [],
  );

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
    disabled,
  }: {
    icon: keyof typeof Ionicons.glyphMap;
    label: string;
    value: boolean;
    onValueChange: (val: boolean) => void;
    disabled?: boolean;
  }) => (
    <View className="flex-row items-center py-3 px-4 bg-[#1a1a1a]">
      <Ionicons name={icon} size={22} color="#6b7280" />
      <Text className="flex-1 ml-3 text-gray-50">{label}</Text>
      {disabled ? (
        <ActivityIndicator size="small" color="#6b7280" />
      ) : (
        <Switch
          value={value}
          onValueChange={onValueChange}
          trackColor={{ false: '#d1d5db', true: '#818cf8' }}
          thumbColor={value ? '#FF6B4A' : '#f4f4f5'}
        />
      )}
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
            onValueChange={updatePushPreference}
            disabled={prefsLoading || !prefsFetched}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <ToggleRow
            icon="mail-outline"
            label="Email Notifications"
            value={emailEnabled}
            onValueChange={updateEmailPreference}
            disabled={prefsLoading || !prefsFetched}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <ToggleRow
            icon="chatbubble-outline"
            label="WhatsApp Notifications"
            value={whatsappEnabled}
            onValueChange={updateWhatsappPreference}
            disabled={prefsLoading || !prefsFetched}
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
                'Support is available at support@studioloop.co.za',
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
