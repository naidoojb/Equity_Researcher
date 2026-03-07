import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Colors } from '../src/theme/colors';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: Colors.bgCard },
          headerTintColor: Colors.textPrimary,
          headerTitleStyle: { fontWeight: '700' },
          contentStyle: { backgroundColor: Colors.bg },
          headerShadowVisible: false,
        }}
      >
        <Stack.Screen
          name="index"
          options={{ title: 'Equity Researcher', headerShown: false }}
        />
        <Stack.Screen
          name="stock/[ticker]"
          options={{ headerShown: false }}
        />
      </Stack>
    </QueryClientProvider>
  );
}
