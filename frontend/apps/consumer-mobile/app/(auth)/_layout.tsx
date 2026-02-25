/**
 * Auth group layout for mobile.
 *
 * Provides the navigation stack for auth-related screens
 * with appropriate header configuration.
 */

import { Stack } from 'expo-router';

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerBackTitle: 'Back',
        headerStyle: {
          backgroundColor: '#f9fafb',
        },
        headerTitleStyle: {
          fontWeight: '600',
        },
      }}
    >
      <Stack.Screen
        name="register"
        options={{
          title: 'Create Account',
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="verify-email-sent"
        options={{
          title: 'Verify Email',
          headerBackVisible: false,
        }}
      />
      <Stack.Screen
        name="login"
        options={{
          title: 'Sign In',
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="forgot-password"
        options={{
          title: 'Reset Password',
        }}
      />
      <Stack.Screen
        name="resend-verification"
        options={{
          title: 'Resend Verification',
        }}
      />
    </Stack>
  );
}
