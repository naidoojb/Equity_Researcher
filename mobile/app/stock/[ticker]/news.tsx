import React from 'react';
import { FlatList, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Colors } from '../../../src/theme/colors';
import { useNews } from '../../../src/hooks/useStock';
import { NewsItem } from '../../../src/components/NewsItem';

export default function NewsScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { data, isLoading, error } = useNews(ticker);

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Fetching news...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Failed to load news</Text>
      </View>
    );
  }

  return (
    <FlatList
      style={styles.list}
      contentContainerStyle={styles.content}
      data={data.articles}
      keyExtractor={(_, i) => String(i)}
      renderItem={({ item }) => <NewsItem item={item} />}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      ListHeaderComponent={
        data.avg_sentiment != null ? (
          <View style={styles.sentimentHeader}>
            <Text style={styles.sentimentLabel}>Avg Sentiment</Text>
            <Text
              style={[
                styles.sentimentValue,
                { color: data.avg_sentiment >= 0 ? Colors.bullish : Colors.bearish },
              ]}
            >
              {data.avg_sentiment > 0 ? '+' : ''}{(data.avg_sentiment * 100).toFixed(0)}%
            </Text>
          </View>
        ) : null
      }
    />
  );
}

const styles = StyleSheet.create({
  list: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: 16, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12, backgroundColor: Colors.bg },
  loadingText: { color: Colors.textSecondary, fontSize: 14 },
  errorText: { color: Colors.bearish, fontSize: 16, fontWeight: '600' },
  separator: { height: 10 },
  sentimentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 4,
    marginBottom: 8,
  },
  sentimentLabel: { fontSize: 14, color: Colors.textSecondary, fontWeight: '600' },
  sentimentValue: { fontSize: 16, fontWeight: '700' },
});
