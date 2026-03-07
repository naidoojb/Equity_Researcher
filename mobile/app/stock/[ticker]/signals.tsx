import React from 'react';
import { ScrollView, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Colors } from '../../../src/theme/colors';
import { useSignals } from '../../../src/hooks/useStock';
import { SignalCard } from '../../../src/components/SignalCard';

export default function SignalsScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { data, isLoading, error } = useSignals(ticker);

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Computing signals...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Failed to load signals</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <SignalCard data={data} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: 16, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12, backgroundColor: Colors.bg },
  loadingText: { color: Colors.textSecondary, fontSize: 14 },
  errorText: { color: Colors.bearish, fontSize: 16, fontWeight: '600' },
});
