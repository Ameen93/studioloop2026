/**
 * Staff login screen for gym mobile app.
 *
 * Allows gym staff to log in with email and password.
 * Stores tokens in MMKV via centralized auth library.
 */

import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { useMutation } from '@tanstack/react-query';
import { gymsGetMyGymProfile, staffAuthLoginStaff } from '@sl/api-client';
import { setStaffProfile, setTokens } from '../../lib/auth';

interface FormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export default function StaffLoginScreen() {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const loginMutation = useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const response = await staffAuthLoginStaff({
        body: data,
        throwOnError: true,
      });
      if (!response.data) {
        throw new Error('Login failed');
      }

      const authData = response.data;

      const gymProfile = await gymsGetMyGymProfile({
        headers: {
          Authorization: `Bearer ${authData.access_token}`,
        },
      });

      return {
        auth: authData,
        gymProfile: gymProfile.data ?? null,
        email: data.email,
      };
    },
    onSuccess: (response) => {
      setTokens({
        access_token: response.auth.access_token,
        refresh_token: response.auth.refresh_token,
      });

      setStaffProfile({
        id: response.email,
        email: response.email,
        name: response.email.split('@')[0],
        role: response.auth.role,
        gymId: response.auth.gym_id,
        gymName: response.gymProfile?.name ?? 'StudioLoop Gym',
      });
      router.replace('/(tabs)');
    },
    onError: (error: unknown) => {
      const err = error as {
        body?: { detail?: { code?: string; message?: string } };
        detail?: { code?: string; message?: string };
      };
      const code = err?.body?.detail?.code || err?.detail?.code;
      if (code === 'INVALID_CREDENTIALS') {
        setErrors({ general: 'Invalid email or password' });
      } else {
        setErrors({ general: 'Login failed. Please try again.' });
      }
    },
  });

  const validateForm = (): { email: string; password: string } | null => {
    const newErrors: FormErrors = {};

    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password || formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return null;
    }

    setErrors({});
    return { email: formData.email, password: formData.password };
  };

  const handleSubmit = () => {
    const data = validateForm();
    if (data) {
      loginMutation.mutate(data);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-gray-50"
    >
      <ScrollView
        contentContainerClassName="flex-grow justify-center px-6 py-12"
        keyboardShouldPersistTaps="handled"
      >
        <View className="w-full max-w-md mx-auto">
          {/* Logo / branding area */}
          <View className="items-center mb-8">
            <View className="w-16 h-16 rounded-2xl bg-emerald-600 items-center justify-center mb-4">
              <Text className="text-3xl font-bold text-white">SL</Text>
            </View>
            <Text className="text-3xl font-bold text-gray-900 text-center">StudioLoop Gym</Text>
            <Text className="text-gray-500 text-center mt-1">Staff Portal</Text>
          </View>

          <Text className="text-xl font-semibold text-gray-900 text-center mb-6">
            Sign in to your account
          </Text>

          {errors.general && (
            <View className="bg-red-50 p-4 rounded-md mb-4">
              <Text className="text-red-700 text-sm">{errors.general}</Text>
            </View>
          )}

          <View className="space-y-4">
            {/* Email */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-1">Email address</Text>
              <TextInput
                className={`w-full px-3 py-2 border rounded-md bg-white ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="staff@gym.co.za"
                value={formData.email}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, email: text }))}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
              />
              {errors.email && <Text className="text-red-600 text-sm mt-1">{errors.email}</Text>}
            </View>

            {/* Password */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-1">Password</Text>
              <TextInput
                className={`w-full px-3 py-2 border rounded-md bg-white ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your password"
                value={formData.password}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, password: text }))}
                secureTextEntry
                autoComplete="current-password"
              />
              {errors.password && (
                <Text className="text-red-600 text-sm mt-1">{errors.password}</Text>
              )}
            </View>

            {/* Submit */}
            <Pressable
              className={`w-full py-3 rounded-md mt-6 ${
                loginMutation.isPending ? 'bg-emerald-400' : 'bg-emerald-600'
              }`}
              onPress={handleSubmit}
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text className="text-white text-center font-semibold">Sign in</Text>
              )}
            </Pressable>
          </View>

          <Text className="text-xs text-gray-400 text-center mt-8">
            Contact your gym administrator if you need access
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
