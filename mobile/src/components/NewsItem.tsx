import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking } from 'react-native';
import { Colors } from '../theme/colors';
import type { NewsItem as NewsItemType } from '../services/api';

interface Props {
  item: NewsItemType;
}

export function NewsItem({ item }: Props) {
  const sentimentColor =
    item.sentiment_label === 'Positive' ? Colors.bullish
    : item.sentiment_label === 'Negative' ? Colors.bearish
    : Colors.neutral;

  const date = new Date(item.published_at);
  const timeAgo = formatTimeAgo(date);

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={() => item.url && Linking.openURL(item.url)}
      activeOpacity={0.7}
    >
      <View style={[styles.sentimentBar, { backgroundColor: sentimentColor }]} />
      <View style={styles.content}>
        <View style={styles.meta}>
          <Text style={styles.source}>{item.source}</Text>
          <Text style={styles.time}>{timeAgo}</Text>
        </View>
        <Text style={styles.title} numberOfLines={3}>{item.title}</Text>
        <View style={styles.footer}>
          <View style={[styles.sentimentPill, { backgroundColor: `${sentimentColor}20`, borderColor: sentimentColor }]}>
            <Text style={[styles.sentimentText, { color: sentimentColor }]}>
              {item.sentiment_label} · {item.sentiment > 0 ? '+' : ''}{(item.sentiment * 100).toFixed(0)}%
            </Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
}

function formatTimeAgo(date: Date): string {
  const now = Date.now();
  const diff = now - date.getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return `${Math.floor(diff / 60_000)}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  sentimentBar: { width: 4 },
  content: { flex: 1, padding: 12 },
  meta: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  source: { fontSize: 11, fontWeight: '600', color: Colors.accent, textTransform: 'uppercase' },
  time: { fontSize: 11, color: Colors.textMuted },
  title: { fontSize: 14, fontWeight: '500', color: Colors.textPrimary, lineHeight: 20 },
  footer: { marginTop: 8 },
  sentimentPill: {
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  sentimentText: { fontSize: 11, fontWeight: '600' },
});
