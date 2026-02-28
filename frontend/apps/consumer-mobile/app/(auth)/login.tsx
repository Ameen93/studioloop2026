/**
 * Consumer login screen for mobile.
 *
 * Allows consumers to login with email and password.
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
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { useMutation } from '@tanstack/react-query';
import { consumerAuthGetCurrentConsumerProfile, consumerAuthLoginConsumer } from '@sl/api-client';
import type { ConsumerLoginRequest } from '@sl/api-client';
import { setConsumerProfile, setTokens } from '../../lib/auth';
import { startGoogleLogin, startAppleLogin } from '../../lib/oauth';

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
    mutationFn: async (data: ConsumerLoginRequest) => {
      const loginResponse = await consumerAuthLoginConsumer({
        body: data,
        throwOnError: true,
      });

      if (!loginResponse.data) {
        throw new Error('Login failed');
      }

      const token = loginResponse.data.access_token;
      const profileResponse = await consumerAuthGetCurrentConsumerProfile({
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return {
        login: loginResponse.data,
        profile: profileResponse.data ?? null,
      };
    },
    onSuccess: (response) => {
      // Store tokens via centralized auth library (MMKV)
      setTokens({
        access_token: response.login.access_token,
        refresh_token: response.login.refresh_token,
      });

      if (response.profile) {
        setConsumerProfile({
          id: response.profile.id,
          email: response.profile.email,
          name: `${response.profile.first_name} ${response.profile.last_name}`.trim(),
        });
      }
      // Navigate to main app tabs
      router.replace('/(tabs)');
    },
    onError: (error: unknown) => {
      const err = error as {
        body?: { detail?: { code?: string; message?: string } };
        detail?: { code?: string; message?: string };
      };
      const code = err?.body?.detail?.code || err?.detail?.code;

      if (code === 'EMAIL_NOT_VERIFIED') {
        setErrors({
          general: 'Please verify your email before logging in. Check your inbox for the verification link.',
        });
      } else if (code === 'INVALID_CREDENTIALS') {
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

  const [oauthLoading, setOauthLoading] = useState(false);

  const handleOAuthLogin = async (provider: 'google' | 'apple') => {
    setOauthLoading(true);
    try {
      const result = provider === 'google' ? await startGoogleLogin() : await startAppleLogin();

      if (result.type === 'dismiss') {
        return;
      }

      if (result.type === 'error') {
        setErrors({ general: result.error_message || 'OAuth sign-in failed. Please try again.' });
        return;
      }

      // Store tokens
      setTokens({
        access_token: result.access_token,
        refresh_token: result.refresh_token,
      });

      // Fetch and store profile
      try {
        const profileResponse = await consumerAuthGetCurrentConsumerProfile({
          headers: { Authorization: `Bearer ${result.access_token}` },
        });
        if (profileResponse.data) {
          setConsumerProfile({
            id: profileResponse.data.id,
            email: profileResponse.data.email,
            name: `${profileResponse.data.first_name} ${profileResponse.data.last_name}`.trim(),
          });
        }
      } catch {
        // Profile fetch failed but tokens are stored, continue
      }

      router.replace('/(tabs)');
    } catch {
      setErrors({ general: 'OAuth sign-in failed. Please try again.' });
    } finally {
      setOauthLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-[#0a0a0a]"
    >
      <ScrollView
        contentContainerClassName="flex-grow justify-center px-6 py-12"
        keyboardShouldPersistTaps="handled"
      >
        <View className="w-full max-w-md mx-auto">
          <Text className="text-3xl font-bold text-gray-50 text-center mb-2">
            Sign in to your account
          </Text>
          <Text className="text-gray-600 text-center mb-8">
            Don't have an account?{' '}
            <Text
              className="text-coral-600 font-medium"
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
                className={`w-full px-3 py-2 border rounded-md bg-[#1a1a1a] ${
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
                className={`w-full px-3 py-2 border rounded-md bg-[#1a1a1a] ${
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
              <Text className="text-coral-600 text-sm font-medium text-right">
                Forgot your password?
              </Text>
            </Pressable>

            {/* Submit button */}
            <Pressable
              className={`w-full py-3 rounded-md mt-6 ${
                loginMutation.isPending ? 'bg-coral-400' : 'bg-coral-600'
              }`}
              onPress={handleSubmit}
              disabled={loginMutation.isPending || oauthLoading}
            >
              {loginMutation.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text className="text-white text-center font-semibold">Sign in</Text>
              )}
            </Pressable>

            {/* OAuth divider */}
            <View className="flex-row items-center my-4">
              <View className="flex-1 h-px bg-gray-300" />
              <Text className="px-3 text-gray-500 text-sm">Or continue with</Text>
              <View className="flex-1 h-px bg-gray-300" />
            </View>

            {/* OAuth buttons */}
            <View className="flex-row gap-3">
              <Pressable
                className="flex-1 flex-row items-center justify-center py-3 border border-gray-300 rounded-md bg-[#1a1a1a]"
                onPress={() => handleOAuthLogin('google')}
                disabled={loginMutation.isPending || oauthLoading}
              >
                {oauthLoading ? (
                  <ActivityIndicator size="small" color="#FF6B4A" />
                ) : (
                  <Text className="text-gray-700 font-medium">Google</Text>
                )}
              </Pressable>
              <Pressable
                className="flex-1 flex-row items-center justify-center py-3 border border-gray-300 rounded-md bg-[#1a1a1a]"
                onPress={() => handleOAuthLogin('apple')}
                disabled={loginMutation.isPending || oauthLoading}
              >
                {oauthLoading ? (
                  <ActivityIndicator size="small" color="#FF6B4A" />
                ) : (
                  <Text className="text-gray-700 font-medium">Apple</Text>
                )}
              </Pressable>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
