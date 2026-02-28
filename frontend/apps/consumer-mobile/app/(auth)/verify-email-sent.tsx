/**
 * Email verification sent confirmation screen for mobile.
 *
 * Displayed after successful registration to inform the user
 * to check their email for the verification link.
 */

import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';

export default function VerifyEmailSentScreen() {
  return (
    <View className="flex-1 bg-[#0a0a0a] justify-center items-center px-6">
      <View className="w-full max-w-md items-center">
        {/* Email icon */}
        <View className="w-16 h-16 rounded-full bg-green-100 items-center justify-center mb-6">
          <Text className="text-3xl">✉️</Text>
        </View>

        <Text className="text-3xl font-bold text-gray-50 text-center mb-2">
          Check your email
        </Text>

        <Text className="text-gray-600 text-center mb-6">
          We've sent a verification link to your email address. Please click the link to verify
          your account.
        </Text>

        <Text className="text-sm text-gray-500 text-center mb-8">
          The verification link will expire in 24 hours.
        </Text>

        <View className="w-full border-t border-[#2a2a2a] pt-6">
          <Text className="text-sm text-gray-600 text-center mb-4">
            Didn't receive the email?{' '}
            <Text
              className="text-coral-600 font-medium"
              onPress={() => router.push('/(auth)/resend-verification')}
            >
              Click here to resend
            </Text>
          </Text>

          <Pressable onPress={() => router.push('/(auth)/login')}>
            <Text className="text-sm text-gray-600 text-center">Back to login</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}
