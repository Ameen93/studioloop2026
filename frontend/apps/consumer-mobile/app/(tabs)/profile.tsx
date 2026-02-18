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
import { getConsumerProfile, clearAuth } from '../../lib/auth';
import { clearQrCache } from '../../lib/qr-cache';

export default function ProfileTab() {
  const queryClient = useQueryClient();
  const profile = getConsumerProfile();

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
      className="flex-row items-center py-3 px-4 bg-white"
      onPress={onPress}
      disabled={!onPress}
    >
      <Ionicons name={icon} size={22} color="#6b7280" />
      <Text className="flex-1 ml-3 text-gray-900">{label}</Text>
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
    <View className="flex-row items-center py-3 px-4 bg-white">
      <Ionicons name={icon} size={22} color="#6b7280" />
      <Text className="flex-1 ml-3 text-gray-900">{label}</Text>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#d1d5db', true: '#818cf8' }}
        thumbColor={value ? '#6366f1' : '#f4f4f5'}
      />
    </View>
  );

  return (
    <ScrollView className="flex-1 bg-gray-50">
      {/* Profile header */}
      <View className="bg-white px-4 py-6 items-center border-b border-gray-200">
        <View className="w-20 h-20 rounded-full bg-indigo-100 items-center justify-center mb-3">
          <Text className="text-2xl font-bold text-indigo-600">
            {profile?.name
              ? profile.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
              : '?'}
          </Text>
        </View>
        <Text className="text-xl font-bold text-gray-900">{profile?.name ?? 'Consumer'}</Text>
        <Text className="text-gray-500 mt-1">{profile?.email ?? ''}</Text>
      </View>

      {/* Account section */}
      <View className="mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide px-4 mb-2">
          Account
        </Text>
        <View className="border-t border-b border-gray-200">
          <MenuRow
            icon="person-outline"
            label="Edit Profile"
            onPress={() => {
              // TODO: Navigate to edit profile screen
            }}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <MenuRow
            icon="lock-closed-outline"
            label="Change Password"
            onPress={() => {
              // TODO: Navigate to change password screen
            }}
          />
        </View>
      </View>

      {/* Notifications section */}
      <View className="mt-6">
        <Text className="text-sm font-medium text-gray-500 uppercase tracking-wide px-4 mb-2">
          Notifications
        </Text>
        <View className="border-t border-b border-gray-200">
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
        <View className="border-t border-b border-gray-200">
          <MenuRow
            icon="help-circle-outline"
            label="Help & FAQ"
            onPress={() => {
              // TODO: Navigate to help screen
            }}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <MenuRow
            icon="document-text-outline"
            label="Privacy Policy"
            onPress={() => {
              // TODO: Open privacy policy
            }}
          />
          <View className="h-px bg-gray-200 ml-12" />
          <MenuRow
            icon="document-text-outline"
            label="Terms of Service"
            onPress={() => {
              // TODO: Open terms of service
            }}
          />
        </View>
      </View>

      {/* Sign out */}
      <View className="mt-6 mb-8">
        <Pressable
          className="mx-4 py-3 bg-white border border-red-300 rounded-lg"
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
