import React from 'react';
import { ScrollView, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Colors } from '../../../src/theme/colors';
import { useOverview, useSignals } from '../../../src/hooks/useStock';
import { StockHeader } from '../../../src/components/StockHeader';

export default function OverviewScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { data: overview, isLoading: overviewLoading, error: overviewError } = useOverview(ticker);
  const { data: signals } = useSignals(ticker);

  if (overviewLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Loading {ticker}...</Text>
      </View>
    );
  }

  if (overviewError || !overview) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Failed to load {ticker}</Text>
        <Text style={styles.errorSub}>Check the ticker symbol and try again.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <StockHeader overview={overview} signals={signals} />

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.card}>
          <Row label="Industry" value={overview.industry ?? 'N/A'} />
          <Row label="Sector" value={overview.sector ?? 'N/A'} />
          <Row label="Exchange" value={overview.exchange} />
          <Row label="Currency" value={overview.currency} />
          <Row label="Avg Volume" value={formatVol(overview.avg_volume)} />
        </View>
      </View>
    </ScrollView>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

function formatVol(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`;
  return String(v);
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.bg },
  content: { paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12, backgroundColor: Colors.bg },
  loadingText: { color: Colors.textSecondary, fontSize: 14 },
  errorText: { color: Colors.bearish, fontSize: 18, fontWeight: '700' },
  errorSub: { color: Colors.textMuted, fontSize: 13 },
  section: { padding: 16 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary, marginBottom: 10 },
  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: 'hidden',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  rowLabel: { fontSize: 14, color: Colors.textSecondary },
  rowValue: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
});
