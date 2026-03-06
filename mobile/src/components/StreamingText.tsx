import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Colors } from '../theme/colors';

interface Props {
  content: string;
  isStreaming: boolean;
  isThinking: boolean;
  toolsUsed: string[];
}

const TOOL_LABELS: Record<string, string> = {
  get_stock_price: '📈 Fetching price data',
  get_technical_indicators: '📊 Analyzing technicals',
  get_news_headlines: '📰 Reading news',
  get_fundamentals: '📋 Reviewing fundamentals',
  get_competitor_data: '🔍 Comparing competitors',
  get_options_flow: '⚡ Checking options flow',
};

export function StreamingText({ content, isStreaming, isThinking, toolsUsed }: Props) {
  // Render markdown-like content with basic styling
  const lines = content.split('\n');

  return (
    <View>
      {/* Status bar while streaming */}
      {isStreaming && (
        <View style={styles.status}>
          <ActivityIndicator size="small" color={Colors.accent} />
          <Text style={styles.statusText}>
            {isThinking ? 'Thinking...' : 'Generating report...'}
          </Text>
        </View>
      )}

      {/* Tools used progress */}
      {toolsUsed.length > 0 && isStreaming && (
        <View style={styles.toolsContainer}>
          {toolsUsed.map(tool => (
            <View key={tool} style={styles.toolPill}>
              <Text style={styles.toolText}>{TOOL_LABELS[tool] ?? tool}</Text>
              <Text style={styles.toolDone}> ✓</Text>
            </View>
          ))}
        </View>
      )}

      {/* Rendered report */}
      {lines.map((line, i) => {
        if (line.startsWith('## ')) {
          return <Text key={i} style={styles.h2}>{line.slice(3)}</Text>;
        } else if (line.startsWith('### ')) {
          return <Text key={i} style={styles.h3}>{line.slice(4)}</Text>;
        } else if (line.startsWith('**') && line.endsWith('**')) {
          return <Text key={i} style={styles.bold}>{line.slice(2, -2)}</Text>;
        } else if (line.startsWith('- ') || line.startsWith('• ')) {
          return (
            <View key={i} style={styles.bulletRow}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.bulletText}>{line.slice(2)}</Text>
            </View>
          );
        } else if (line.trim() === '') {
          return <View key={i} style={styles.spacer} />;
        } else {
          return <Text key={i} style={styles.body}>{line}</Text>;
        }
      })}

      {/* Streaming cursor */}
      {isStreaming && content.length > 0 && (
        <Text style={styles.cursor}>▌</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  status: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    backgroundColor: `${Colors.accent}15`,
    borderRadius: 8,
    marginBottom: 12,
  },
  statusText: { color: Colors.accent, fontSize: 14, fontWeight: '500' },
  toolsContainer: { gap: 6, marginBottom: 16 },
  toolPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.bgElevated,
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 5,
    alignSelf: 'flex-start',
  },
  toolText: { fontSize: 12, color: Colors.textSecondary },
  toolDone: { fontSize: 12, color: Colors.bullish },
  h2: {
    fontSize: 20,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginTop: 20,
    marginBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    paddingBottom: 6,
  },
  h3: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginTop: 14,
    marginBottom: 6,
  },
  bold: {
    fontSize: 14,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  bulletRow: { flexDirection: 'row', marginBottom: 6, paddingLeft: 4 },
  bullet: { color: Colors.accent, fontSize: 14, marginRight: 8, marginTop: 1 },
  bulletText: { flex: 1, fontSize: 14, color: Colors.textSecondary, lineHeight: 20 },
  body: {
    fontSize: 14,
    color: Colors.textSecondary,
    lineHeight: 22,
    marginBottom: 4,
  },
  spacer: { height: 8 },
  cursor: { color: Colors.accent, fontSize: 18 },
});
