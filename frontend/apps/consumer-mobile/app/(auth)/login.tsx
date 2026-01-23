/**
 * Consumer login screen for mobile.
 *
 * Allows consumers to login with email and password.
 * Stores tokens in MMKV (NOT AsyncStorage per architecture).
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
import { createMMKV } from 'react-native-mmkv';
import { consumerAuthLoginConsumer } from '@sl/api-client';
import type { ConsumerLoginRequest } from '@sl/api-client';

// MMKV storage instance for auth tokens (AC #2 - MMKV, NOT AsyncStorage)
const storage = createMMKV({ id: 'auth-storage' });

interface FormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export default function LoginScreen() {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const loginMutation = useMutation({
    mutationFn: (data: ConsumerLoginRequest) =>
      consumerAuthLoginConsumer({
        body: data,
      }),
    onSuccess: (response) => {
      // Store tokens in MMKV (AC #2 - NOT AsyncStorage!)
      if (response.data) {
        storage.set('access_token', response.data.access_token);
        storage.set('refresh_token', response.data.refresh_token);
      }
      // Navigate to home screen (AC #3)
      router.replace('/');
    },
    onError: (error: unknown) => {
      const err = error as { body?: { detail?: { code?: string; message?: string } } };
      if (err?.body?.detail?.code === 'EMAIL_NOT_VERIFIED') {
        setErrors({
          general: 'Please verify your email before logging in. Check your inbox for the verification link.',
        });
      } else if (err?.body?.detail?.code === 'INVALID_CREDENTIALS') {
        setErrors({ general: 'Invalid email or password' });
      } else {
        setErrors({ general: 'Login failed. Please try again.' });
      }
    },
  });

  const validateForm = (): ConsumerLoginRequest | null => {
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
    return {
      email: formData.email,
      password: formData.password,
    };
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
          <Text className="text-3xl font-bold text-gray-900 text-center mb-2">
            Sign in to your account
          </Text>
          <Text className="text-gray-600 text-center mb-8">
            Don't have an account?{' '}
            <Text
              className="text-primary-600 font-medium"
              onPress={() => router.push('/(auth)/register')}
            >
              Create one
            </Text>
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
                placeholder="john@example.com"
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

            {/* Forgot password link */}
            <Pressable onPress={() => router.push('/(auth)/forgot-password')}>
              <Text className="text-primary-600 text-sm font-medium text-right">
                Forgot your password?
              </Text>
            </Pressable>

            {/* Submit button */}
            <Pressable
              className={`w-full py-3 rounded-md mt-6 ${
                loginMutation.isPending ? 'bg-primary-400' : 'bg-primary-600'
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
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
