import React from 'react';
import { ScrollView, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Colors } from '../../../src/theme/colors';
import { useCompetitors } from '../../../src/hooks/useStock';
import { CompetitorTable } from '../../../src/components/CompetitorTable';

export default function CompetitorsScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { data, isLoading, error } = useCompetitors(ticker);

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Loading competitors...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Failed to load competitors</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      {data.sector && (
        <Text style={styles.sectorBadge}>{data.sector}</Text>
      )}
      <CompetitorTable competitors={data.competitors} currentTicker={ticker} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: 16, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12, backgroundColor: Colors.bg },
  loadingText: { color: Colors.textSecondary, fontSize: 14 },
  errorText: { color: Colors.bearish, fontSize: 16, fontWeight: '600' },
  sectorBadge: {
    alignSelf: 'flex-start',
    backgroundColor: `${Colors.accent}20`,
    color: Colors.accent,
    borderWidth: 1,
    borderColor: Colors.accent,
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 4,
    fontSize: 12,
    fontWeight: '700',
    marginBottom: 12,
  },
});
