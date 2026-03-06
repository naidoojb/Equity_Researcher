import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '../theme/colors';
import { SignalBadge } from './SignalBadge';
import type { Signal, SignalsResponse } from '../services/api';

interface Props {
  data: SignalsResponse;
}

export function SignalCard({ data }: Props) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>Daily Signals</Text>
        <SignalBadge signal={data.signal} score={data.score} size="md" />
      </View>

      <View style={styles.scoreBar}>
        <View style={styles.barTrack}>
          <View
            style={[
              styles.barFill,
              {
                left: '50%',
                width: `${Math.abs(data.score) * 50}%`,
                marginLeft: data.score < 0 ? `-${Math.abs(data.score) * 50}%` : 0,
                backgroundColor: data.score >= 0 ? Colors.bullish : Colors.bearish,
              },
            ]}
          />
        </View>
        <View style={styles.barLabels}>
          <Text style={[styles.barLabel, { color: Colors.bearish }]}>Bearish</Text>
          <Text style={[styles.barLabel, { color: Colors.bullish }]}>Bullish</Text>
        </View>
      </View>

      <View style={styles.signalList}>
        {data.signals.map((signal, i) => (
          <SignalRow key={i} signal={signal} />
        ))}
      </View>

      <Text style={styles.updated}>
        Updated {new Date(data.updated_at).toLocaleTimeString()}
      </Text>
    </View>
  );
}

function SignalRow({ signal }: { signal: Signal }) {
  const color =
    signal.direction === 'bullish' ? Colors.bullish
    : signal.direction === 'bearish' ? Colors.bearish
    : Colors.neutral;

  const icon = signal.direction === 'bullish' ? '▲' : signal.direction === 'bearish' ? '▼' : '●';

  return (
    <View style={styles.signalRow}>
      <Text style={[styles.signalIcon, { color }]}>{icon}</Text>
      <Text style={styles.signalLabel}>{signal.label}</Text>
      <Text style={[styles.signalValue, { color }]}>{signal.value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary },
  scoreBar: { marginBottom: 16 },
  barTrack: {
    height: 8,
    backgroundColor: Colors.bgElevated,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 4,
    position: 'relative',
  },
  barFill: { position: 'absolute', height: '100%', borderRadius: 4 },
  barLabels: { flexDirection: 'row', justifyContent: 'space-between' },
  barLabel: { fontSize: 11, fontWeight: '500' },
  signalList: { gap: 8 },
  signalRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  signalIcon: { fontSize: 10, width: 14 },
  signalLabel: { flex: 1, fontSize: 13, color: Colors.textSecondary },
  signalValue: { fontSize: 13, fontWeight: '600' },
  updated: { fontSize: 11, color: Colors.textMuted, marginTop: 12, textAlign: 'right' },
});
