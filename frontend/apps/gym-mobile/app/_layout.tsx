import '../global.css';
import '../lib/configureApiClient';

import { useEffect } from 'react';
import { Stack, router } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { onSessionExpired } from '../lib/authSession';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2 * 60 * 1000, // 2 minutes (staff needs fresher data)
      retry: 1,
    },
  },
});

export default function RootLayout() {
  useEffect(() => {
    return onSessionExpired(() => {
      queryClient.clear();
      router.replace('/(auth)/login');
    });
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="auto" />
      <Stack>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="reports"
          options={{
            title: 'Reports',
            headerBackTitle: 'Back',
          }}
        />
      </Stack>
    </QueryClientProvider>
  );
}
