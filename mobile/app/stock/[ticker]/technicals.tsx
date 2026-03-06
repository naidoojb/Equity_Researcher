import React from 'react';
import { ScrollView, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Colors } from '../../../src/theme/colors';
import { useTechnicals } from '../../../src/hooks/useStock';
import type { Signal } from '../../../src/services/api';

export default function TechnicalsScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { data, isLoading, error } = useTechnicals(ticker);

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Loading technicals...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Failed to load technicals</Text>
      </View>
    );
  }

  const fmt = (v: number | null, d = 2) => v != null ? v.toFixed(d) : 'N/A';
  const price = data.price;

  const maRelation = (ma: number | null) => {
    if (ma == null) return null;
    const diff = ((price - ma) / ma) * 100;
    return { diff, above: diff >= 0 };
  };

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      {/* RSI */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>RSI (14)</Text>
        {data.rsi != null ? (
          <>
            <Text style={[styles.bigValue, { color: rsiColor(data.rsi) }]}>
              {data.rsi.toFixed(1)}
            </Text>
            <View style={styles.rsiTrack}>
              <View style={[styles.rsiFill, { width: `${Math.min(data.rsi, 100)}%`, backgroundColor: rsiColor(data.rsi) }]} />
            </View>
            <View style={styles.rsiLabels}>
              <Text style={[styles.rsiLabel, { color: Colors.bearish }]}>Oversold &lt;30</Text>
              <Text style={[styles.rsiLabel, { color: Colors.bullish }]}>Overbought &gt;70</Text>
            </View>
          </>
        ) : (
          <Text style={styles.naText}>N/A</Text>
        )}
      </View>

      {/* MACD */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>MACD</Text>
        <Row label="MACD" value={fmt(data.macd)} />
        <Row label="Signal" value={fmt(data.macd_signal)} />
        <Row
          label="Histogram"
          value={fmt(data.macd_hist)}
          valueColor={data.macd_hist != null
            ? (data.macd_hist >= 0 ? Colors.bullish : Colors.bearish)
            : undefined}
        />
      </View>

      {/* Moving Averages */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Moving Averages</Text>
        {[
          { label: 'SMA 20', val: data.sma_20 },
          { label: 'SMA 50', val: data.sma_50 },
          { label: 'SMA 200', val: data.sma_200 },
        ].map(({ label, val }) => {
          const rel = maRelation(val);
          return (
            <View key={label} style={styles.maRow}>
              <Text style={styles.maLabel}>{label}</Text>
              <Text style={styles.maValue}>{fmt(val)}</Text>
              {rel && (
                <Text style={[styles.maRel, { color: rel.above ? Colors.bullish : Colors.bearish }]}>
                  {rel.above ? '▲' : '▼'} {Math.abs(rel.diff).toFixed(2)}%
                </Text>
              )}
            </View>
          );
        })}
      </View>

      {/* Bollinger Bands */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Bollinger Bands</Text>
        <Row label="Upper" value={fmt(data.bb_upper)} />
        <Row label="Middle" value={fmt(data.bb_middle)} />
        <Row label="Lower" value={fmt(data.bb_lower)} />
        <Row label="Current Price" value={`$${price.toFixed(2)}`} />
      </View>

      {/* Signals */}
      {data.signals.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Technical Signals</Text>
          {data.signals.map((s: Signal, i: number) => (
            <SignalRow key={i} signal={s} />
          ))}
        </View>
      )}
    </ScrollView>
  );
}

function rsiColor(rsi: number) {
  if (rsi >= 70) return Colors.bearish;
  if (rsi <= 30) return Colors.bullish;
  return Colors.textPrimary;
}

function Row({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={[styles.rowValue, valueColor ? { color: valueColor } : undefined]}>{value}</Text>
    </View>
  );
}

function SignalRow({ signal }: { signal: Signal }) {
  const color = signal.direction === 'bullish' ? Colors.bullish
    : signal.direction === 'bearish' ? Colors.bearish
    : Colors.neutral;
  return (
    <View style={styles.signalRow}>
      <Text style={[styles.signalIcon, { color }]}>
        {signal.direction === 'bullish' ? '▲' : signal.direction === 'bearish' ? '▼' : '●'}
      </Text>
      <Text style={styles.signalLabel}>{signal.label}</Text>
      <Text style={[styles.signalValue, { color }]}>{signal.value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: 16, gap: 12, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12, backgroundColor: Colors.bg },
  loadingText: { color: Colors.textSecondary, fontSize: 14 },
  errorText: { color: Colors.bearish, fontSize: 16, fontWeight: '600' },
  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: 16,
  },
  cardTitle: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary, marginBottom: 12 },
  bigValue: { fontSize: 42, fontWeight: '800', textAlign: 'center', marginBottom: 12 },
  naText: { color: Colors.textMuted, fontSize: 14 },
  rsiTrack: { height: 8, backgroundColor: Colors.bgElevated, borderRadius: 4, overflow: 'hidden', marginBottom: 4 },
  rsiFill: { height: '100%', borderRadius: 4 },
  rsiLabels: { flexDirection: 'row', justifyContent: 'space-between' },
  rsiLabel: { fontSize: 11 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  rowLabel: { fontSize: 14, color: Colors.textSecondary },
  rowValue: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
  maRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: Colors.border },
  maLabel: { flex: 1, fontSize: 14, color: Colors.textSecondary },
  maValue: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary, marginRight: 12 },
  maRel: { fontSize: 13, fontWeight: '600', width: 70, textAlign: 'right' },
  signalRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 6 },
  signalIcon: { fontSize: 10, width: 14 },
  signalLabel: { flex: 1, fontSize: 13, color: Colors.textSecondary },
  signalValue: { fontSize: 13, fontWeight: '600' },
});
