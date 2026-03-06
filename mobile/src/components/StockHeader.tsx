import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors } from '../theme/colors';
import { SignalBadge } from './SignalBadge';
import type { StockOverview, SignalsResponse } from '../services/api';
import { formatMarketCap, formatVolume } from '../services/api';

interface Props {
  overview: StockOverview;
  signals?: SignalsResponse;
}

export function StockHeader({ overview, signals }: Props) {
  const isPositive = overview.change >= 0;
  const changeColor = isPositive ? Colors.bullish : Colors.bearish;

  return (
    <LinearGradient
      colors={['#12121A', '#0A0A0F']}
      style={styles.container}
    >
      <View style={styles.row}>
        <View style={styles.nameBlock}>
          <Text style={styles.ticker}>{overview.ticker}</Text>
          <Text style={styles.name} numberOfLines={1}>{overview.name}</Text>
          {overview.exchange && (
            <Text style={styles.exchange}>{overview.exchange} · {overview.sector ?? 'N/A'}</Text>
          )}
        </View>
        {signals && (
          <SignalBadge signal={signals.signal} score={signals.score} size="md" />
        )}
      </View>

      <View style={styles.priceRow}>
        <Text style={styles.price}>
          {overview.currency === 'USD' ? '$' : ''}{overview.price.toFixed(2)}
        </Text>
        <View style={[styles.changePill, { backgroundColor: `${changeColor}20` }]}>
          <Text style={[styles.change, { color: changeColor }]}>
            {isPositive ? '▲' : '▼'} {Math.abs(overview.change).toFixed(2)} ({Math.abs(overview.change_pct).toFixed(2)}%)
          </Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        <Stat label="Market Cap" value={formatMarketCap(overview.market_cap)} />
        <Stat label="Volume" value={formatVolume(overview.volume)} />
        <Stat label="52W High" value={`$${overview.week_52_high.toFixed(2)}`} />
        <Stat label="52W Low" value={`$${overview.week_52_low.toFixed(2)}`} />
      </View>
    </LinearGradient>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingTop: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  nameBlock: { flex: 1, marginRight: 12 },
  ticker: { fontSize: 26, fontWeight: '800', color: Colors.textPrimary },
  name: { fontSize: 14, color: Colors.textSecondary, marginTop: 2 },
  exchange: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },
  priceRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 16 },
  price: { fontSize: 36, fontWeight: '700', color: Colors.textPrimary },
  changePill: { borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4 },
  change: { fontSize: 15, fontWeight: '600' },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between' },
  stat: { alignItems: 'center' },
  statLabel: { fontSize: 11, color: Colors.textMuted, marginBottom: 3 },
  statValue: { fontSize: 13, fontWeight: '600', color: Colors.textSecondary },
});
