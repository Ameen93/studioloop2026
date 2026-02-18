/**
 * Auth group layout for gym staff mobile.
 *
 * Provides the navigation stack for staff auth screens.
 */

import { Stack } from 'expo-router';

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        headerStyle: {
          backgroundColor: '#f9fafb',
        },
        headerTitleStyle: {
          fontWeight: '600',
        },
      }}
    >
      <Stack.Screen
        name="login"
        options={{
          title: 'Staff Login',
        }}
      />
    </Stack>
  );
}
