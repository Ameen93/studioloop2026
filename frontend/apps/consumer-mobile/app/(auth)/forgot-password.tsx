import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { consumerAuthForgotPassword } from '@sl/api-client';

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);
    try {
      await consumerAuthForgotPassword({
        body: { email },
        throwOnError: true,
      });
      setSubmitted(true);
    } catch {
      setError('Unable to submit request right now. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-[#0a0a0a]"
    >
      <ScrollView contentContainerClassName="flex-grow justify-center px-6 py-12">
        <View className="w-full max-w-md mx-auto space-y-4">
          <Text className="text-2xl font-bold text-gray-50 text-center">Reset your password</Text>
          <Text className="text-sm text-gray-600 text-center">
            Enter your email to receive reset instructions.
          </Text>

          {submitted && (
            <View className="bg-green-50 p-4 rounded-md">
              <Text className="text-green-700 text-sm">
                If this email exists, a reset link has been sent.
              </Text>
            </View>
          )}

          {error ? (
            <View className="bg-red-50 p-4 rounded-md">
              <Text className="text-red-700 text-sm">{error}</Text>
            </View>
          ) : null}

          <TextInput
            className="w-full px-3 py-2 border border-gray-300 rounded-md bg-[#1a1a1a]"
            placeholder="you@example.com"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
          />

          <Pressable
            className={`w-full py-3 rounded-md ${isLoading ? 'bg-coral-400' : 'bg-coral-600'}`}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="text-white text-center font-semibold">Send reset link</Text>
            )}
          </Pressable>

          <Pressable onPress={() => router.push('/(auth)/login')}>
            <Text className="text-coral-600 text-center text-sm font-medium">Back to sign in</Text>
          </Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
