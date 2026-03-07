import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Colors } from '../theme/colors';
import type { Competitor } from '../services/api';
import { formatMarketCap } from '../services/api';

interface Props {
  competitors: Competitor[];
  currentTicker: string;
}

export function CompetitorTable({ competitors, currentTicker }: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={[styles.col, styles.colTicker]}>Ticker</Text>
        <Text style={[styles.col, styles.colPrice]}>Price</Text>
        <Text style={[styles.col, styles.colChange]}>1D Chg</Text>
        <Text style={[styles.col, styles.colCap]}>Mkt Cap</Text>
        <Text style={[styles.col, styles.colPE]}>P/E</Text>
      </View>
      {competitors.map((c, i) => {
        const isPositive = c.change_pct >= 0;
        const changeColor = isPositive ? Colors.bullish : Colors.bearish;
        return (
          <View key={c.ticker} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
            <View style={[styles.col, styles.colTicker]}>
              <Text style={styles.ticker}>{c.ticker}</Text>
              <Text style={styles.name} numberOfLines={1}>{c.name}</Text>
            </View>
            <Text style={[styles.col, styles.colPrice, styles.value]}>
              ${c.price.toFixed(2)}
            </Text>
            <Text style={[styles.col, styles.colChange, { color: changeColor }]}>
              {isPositive ? '+' : ''}{c.change_pct.toFixed(2)}%
            </Text>
            <Text style={[styles.col, styles.colCap, styles.value]}>
              {formatMarketCap(c.market_cap)}
            </Text>
            <Text style={[styles.col, styles.colPE, styles.value]}>
              {c.pe_ratio != null ? c.pe_ratio.toFixed(1) : 'N/A'}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  header: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: Colors.bgElevated,
  },
  col: { fontSize: 12, color: Colors.textMuted, fontWeight: '600' },
  colTicker: { flex: 1.8 },
  colPrice: { flex: 1.2, textAlign: 'right' },
  colChange: { flex: 1.2, textAlign: 'right' },
  colCap: { flex: 1.2, textAlign: 'right' },
  colPE: { flex: 0.8, textAlign: 'right' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  rowAlt: { backgroundColor: Colors.bgElevated },
  ticker: { fontSize: 13, fontWeight: '700', color: Colors.textPrimary },
  name: { fontSize: 11, color: Colors.textMuted, marginTop: 1 },
  value: { color: Colors.textPrimary, fontWeight: '500', fontSize: 13 },
});
