/**
 * Consumer registration screen for mobile.
 *
 * Allows new consumers to create an account with email and password.
 * Uses shared UI components from @sl/ui.
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
import { consumerAuthRegisterConsumer } from '@sl/api-client';
import type { ConsumerCreate } from '@sl/api-client';

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  firstName?: string;
  lastName?: string;
  general?: string;
}

export default function RegisterScreen() {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const registerMutation = useMutation({
    mutationFn: async (data: ConsumerCreate) => {
      const response = await consumerAuthRegisterConsumer({
        body: data,
        throwOnError: true,
      });
      if (!response.data) {
        throw new Error('REGISTER_RESPONSE_INVALID');
      }
      return response.data;
    },
    onSuccess: () => {
      router.replace('/(auth)/verify-email-sent');
    },
    onError: (error: unknown) => {
      const err = error as {
        body?: { detail?: { code?: string; message?: string } };
        detail?: { code?: string; message?: string };
      };
      const code = err?.body?.detail?.code || err?.detail?.code;

      if (code === 'EMAIL_ALREADY_EXISTS') {
        setErrors({ email: 'An account with this email already exists' });
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    },
  });

  const validateForm = (): ConsumerCreate | null => {
    const newErrors: FormErrors = {};

    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password || formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.password = 'Passwords do not match';
    }

    if (!formData.firstName || formData.firstName.trim().length === 0) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName || formData.lastName.trim().length === 0) {
      newErrors.lastName = 'Last name is required';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return null;
    }

    setErrors({});
    return {
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName.trim(),
      last_name: formData.lastName.trim(),
    };
  };

  const handleSubmit = () => {
    const data = validateForm();
    if (data) {
      registerMutation.mutate(data);
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
            Create your account
          </Text>
          <Text className="text-gray-600 text-center mb-8">
            Already have an account?{' '}
            <Text
              className="text-coral-600 font-medium"
              onPress={() => router.push('/(auth)/login')}
            >
              Sign in
            </Text>
          </Text>

          {errors.general && (
            <View className="bg-red-50 p-4 rounded-md mb-4">
              <Text className="text-red-700 text-sm">{errors.general}</Text>
            </View>
          )}

          <View className="space-y-4">
            {/* Name row */}
            <View className="flex-row space-x-4">
              <View className="flex-1">
                <Text className="text-sm font-medium text-gray-700 mb-1">First name</Text>
                <TextInput
                  className={`w-full px-3 py-2 border rounded-md bg-[#1a1a1a] ${
                    errors.firstName ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="John"
                  value={formData.firstName}
                  onChangeText={(text) => setFormData((prev) => ({ ...prev, firstName: text }))}
                  autoCapitalize="words"
                  autoComplete="given-name"
                />
                {errors.firstName && (
                  <Text className="text-red-600 text-sm mt-1">{errors.firstName}</Text>
                )}
              </View>
              <View className="flex-1">
                <Text className="text-sm font-medium text-gray-700 mb-1">Last name</Text>
                <TextInput
                  className={`w-full px-3 py-2 border rounded-md bg-[#1a1a1a] ${
                    errors.lastName ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Doe"
                  value={formData.lastName}
                  onChangeText={(text) => setFormData((prev) => ({ ...prev, lastName: text }))}
                  autoCapitalize="words"
                  autoComplete="family-name"
                />
                {errors.lastName && (
                  <Text className="text-red-600 text-sm mt-1">{errors.lastName}</Text>
                )}
              </View>
            </View>

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
                placeholder="Min. 8 characters"
                value={formData.password}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, password: text }))}
                secureTextEntry
                autoComplete="new-password"
              />
              {errors.password && (
                <Text className="text-red-600 text-sm mt-1">{errors.password}</Text>
              )}
            </View>

            {/* Confirm Password */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-1">Confirm password</Text>
              <TextInput
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-[#1a1a1a]"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, confirmPassword: text }))}
                secureTextEntry
                autoComplete="new-password"
              />
            </View>

            {/* Submit button */}
            <Pressable
              className={`w-full py-3 rounded-md mt-6 ${
                registerMutation.isPending ? 'bg-coral-400' : 'bg-coral-600'
              }`}
              onPress={handleSubmit}
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text className="text-white text-center font-semibold">Create account</Text>
              )}
            </Pressable>

            <Text className="text-xs text-gray-500 text-center mt-4">
              By creating an account, you agree to our Terms of Service and Privacy Policy
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
