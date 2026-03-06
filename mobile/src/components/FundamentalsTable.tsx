import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '../theme/colors';
import type { Fundamentals } from '../services/api';
import { formatMarketCap, formatPct } from '../services/api';

interface Props {
  data: Fundamentals;
}

export function FundamentalsTable({ data }: Props) {
  const rows = [
    { label: 'P/E Ratio (TTM)', value: data.pe_ratio?.toFixed(2) },
    { label: 'Forward P/E', value: data.forward_pe?.toFixed(2) },
    { label: 'EPS (TTM)', value: data.eps != null ? `$${data.eps.toFixed(2)}` : null },
    { label: 'Revenue', value: data.revenue != null ? formatMarketCap(data.revenue) : null },
    { label: 'Revenue Growth', value: data.revenue_growth != null ? formatPct(data.revenue_growth) : null },
    { label: 'Gross Margin', value: data.gross_margin != null ? formatPct(data.gross_margin) : null },
    { label: 'Operating Margin', value: data.operating_margin != null ? formatPct(data.operating_margin) : null },
    { label: 'Net Margin', value: data.net_margin != null ? formatPct(data.net_margin) : null },
    { label: 'Debt/Equity', value: data.debt_to_equity?.toFixed(2) },
    { label: 'Current Ratio', value: data.current_ratio?.toFixed(2) },
    { label: 'Price/Book', value: data.price_to_book?.toFixed(2) },
    { label: 'Dividend Yield', value: data.dividend_yield != null ? formatPct(data.dividend_yield) : null },
    { label: 'Beta', value: data.beta?.toFixed(2) },
  ];

  return (
    <View style={styles.table}>
      {rows.map(({ label, value }, i) => (
        <View key={label} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
          <Text style={styles.label}>{label}</Text>
          <Text style={styles.value}>{value ?? 'N/A'}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  table: {
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  rowAlt: { backgroundColor: Colors.bgElevated },
  label: { fontSize: 14, color: Colors.textSecondary },
  value: { fontSize: 14, fontWeight: '600', color: Colors.textPrimary },
});
