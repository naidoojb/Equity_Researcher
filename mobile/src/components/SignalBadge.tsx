import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, SignalColors } from '../theme/colors';

type SignalLabel = keyof typeof SignalColors;

interface Props {
  signal: string;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}

export function SignalBadge({ signal, score, size = 'md' }: Props) {
  const color = SignalColors[signal as SignalLabel] ?? Colors.neutral;
  const isSmall = size === 'sm';
  const isLarge = size === 'lg';

  return (
    <View style={[
      styles.badge,
      { borderColor: color, backgroundColor: `${color}20` },
      isSmall && styles.badgeSm,
      isLarge && styles.badgeLg,
    ]}>
      <Text style={[
        styles.text,
        { color },
        isSmall && styles.textSm,
        isLarge && styles.textLg,
      ]}>
        {signal}
      </Text>
      {score !== undefined && (
        <Text style={[styles.score, { color }, isSmall && styles.textSm]}>
          {' '}({score > 0 ? '+' : ''}{(score * 100).toFixed(0)}%)
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 4,
    alignSelf: 'flex-start',
  },
  badgeSm: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  badgeLg: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 8 },
  text: { fontWeight: '700', fontSize: 13, letterSpacing: 0.5 },
  textSm: { fontSize: 11 },
  textLg: { fontSize: 16 },
  score: { fontWeight: '500', fontSize: 13 },
});
