import React, { useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import Svg, { Defs, LinearGradient, Path, Stop } from 'react-native-svg';
import { useHistory } from '../hooks/useStock';
import { HistoryPeriod } from '../services/api';
import { Colors } from '../theme/colors';

const PERIODS: { label: string; value: HistoryPeriod }[] = [
  { label: '1W', value: '1wk' },
  { label: '1M', value: '1mo' },
  { label: '3M', value: '3mo' },
  { label: '6M', value: '6mo' },
  { label: '1Y', value: '1y' },
];

const CHART_HEIGHT = 140;
const CHART_WIDTH = 340; // intrinsic SVG viewBox width

interface Props {
  ticker: string;
  currentPrice: number;
}

export function PriceChart({ ticker, currentPrice }: Props) {
  const [period, setPeriod] = useState<HistoryPeriod>('1mo');
  const { data: history, isLoading } = useHistory(ticker, period);

  // Build the SVG line + area path from close prices
  const chartContent = React.useMemo(() => {
    if (!history || history.length < 2) return null;

    const closes = history.map((p) => p.close);
    const minPrice = Math.min(...closes);
    const maxPrice = Math.max(...closes);
    const priceRange = maxPrice - minPrice || 1;

    const xStep = CHART_WIDTH / (closes.length - 1);
    const pad = 8; // vertical padding in px

    const toY = (price: number) =>
      pad + ((maxPrice - price) / priceRange) * (CHART_HEIGHT - pad * 2);

    // Build SVG path points
    const points = closes.map((c, i) => ({ x: i * xStep, y: toY(c) }));

    // Smooth line using quadratic bezier approximation
    let linePath = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const cpx = (prev.x + curr.x) / 2;
      linePath += ` Q ${cpx} ${prev.y} ${curr.x} ${curr.y}`;
    }

    // Area path = line + close down the right side + back along the bottom
    const areaPath =
      linePath +
      ` L ${points[points.length - 1].x} ${CHART_HEIGHT}` +
      ` L ${points[0].x} ${CHART_HEIGHT} Z`;

    const isPositive = closes[closes.length - 1] >= closes[0];
    const changeAbs = closes[closes.length - 1] - closes[0];
    const changePct = (changeAbs / closes[0]) * 100;

    return { linePath, areaPath, isPositive, changePct, minPrice, maxPrice };
  }, [history]);

  const lineColor = chartContent?.isPositive ? Colors.bullish : Colors.bearish;
  const gradientId = `grad_${ticker}_${period}`;

  return (
    <View style={styles.container}>
      {/* Period selector */}
      <View style={styles.periodRow}>
        {PERIODS.map((p) => (
          <TouchableOpacity
            key={p.value}
            style={[styles.periodBtn, period === p.value && styles.periodBtnActive]}
            onPress={() => setPeriod(p.value)}
          >
            <Text style={[styles.periodLabel, period === p.value && styles.periodLabelActive]}>
              {p.label}
            </Text>
          </TouchableOpacity>
        ))}
        {chartContent && (
          <Text
            style={[
              styles.periodChangePct,
              { color: chartContent.isPositive ? Colors.bullish : Colors.bearish },
            ]}
          >
            {chartContent.isPositive ? '+' : ''}
            {chartContent.changePct.toFixed(2)}%
          </Text>
        )}
      </View>

      {/* Chart area */}
      <View style={styles.chartWrap}>
        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="small" color={Colors.accent} />
          </View>
        )}

        {!isLoading && chartContent && (
          <>
            {/* Min / max price labels */}
            <View style={styles.priceLabels}>
              <Text style={styles.priceLabel}>${chartContent.maxPrice.toFixed(2)}</Text>
              <Text style={styles.priceLabel}>${chartContent.minPrice.toFixed(2)}</Text>
            </View>

            <Svg
              width="100%"
              height={CHART_HEIGHT}
              viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
              preserveAspectRatio="none"
            >
              <Defs>
                <LinearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <Stop offset="0%" stopColor={lineColor} stopOpacity={0.25} />
                  <Stop offset="100%" stopColor={lineColor} stopOpacity={0} />
                </LinearGradient>
              </Defs>

              {/* Gradient fill */}
              <Path d={chartContent.areaPath} fill={`url(#${gradientId})`} />

              {/* Price line */}
              <Path
                d={chartContent.linePath}
                stroke={lineColor}
                strokeWidth={2}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </Svg>
          </>
        )}

        {!isLoading && !chartContent && (
          <View style={styles.noData}>
            <Text style={styles.noDataText}>No chart data available</Text>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 16,
    marginBottom: 8,
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: 'hidden',
    paddingTop: 12,
  },
  periodRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingBottom: 10,
    gap: 4,
  },
  periodBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  periodBtnActive: {
    backgroundColor: Colors.bgElevated,
  },
  periodLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.textMuted,
  },
  periodLabelActive: {
    color: Colors.textPrimary,
  },
  periodChangePct: {
    marginLeft: 'auto',
    fontSize: 13,
    fontWeight: '700',
    paddingRight: 4,
  },
  chartWrap: {
    height: CHART_HEIGHT,
    flexDirection: 'row',
  },
  loadingOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  priceLabels: {
    width: 68,
    paddingHorizontal: 8,
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  priceLabel: {
    fontSize: 10,
    color: Colors.textMuted,
    textAlign: 'right',
  },
  noData: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  noDataText: {
    fontSize: 13,
    color: Colors.textMuted,
  },
});
