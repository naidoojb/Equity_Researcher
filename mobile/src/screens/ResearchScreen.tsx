import React, { useEffect } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, SafeAreaView, ActivityIndicator,
} from 'react-native';
import { Colors } from '../theme/colors';
import { useLocalSearchParams } from 'expo-router';
import { useResearchStream } from '../hooks/useResearchStream';
import { StreamingText } from '../components/StreamingText';

export function ResearchScreen() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const { content, isStreaming, isThinking, toolsUsed, error, isDone, startResearch } =
    useResearchStream(ticker);

  useEffect(() => {
    startResearch();
  }, [ticker]);

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Deep Research</Text>
          <Text style={styles.subtitle}>{ticker} · AI Analysis by Claude</Text>
        </View>
        {isDone && (
          <TouchableOpacity style={styles.refreshBtn} onPress={startResearch}>
            <Text style={styles.refreshText}>↺ Refresh</Text>
          </TouchableOpacity>
        )}
      </View>

      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>⚠️ {error}</Text>
          <TouchableOpacity onPress={startResearch} style={styles.retryBtn}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {!content && isStreaming && !isThinking && toolsUsed.length === 0 && (
        <View style={styles.initialLoading}>
          <ActivityIndicator size="large" color={Colors.accent} />
          <Text style={styles.loadingText}>Connecting to research engine...</Text>
        </View>
      )}

      {(content.length > 0 || toolsUsed.length > 0 || isThinking) && (
        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          <StreamingText
            content={content}
            isStreaming={isStreaming}
            isThinking={isThinking}
            toolsUsed={toolsUsed}
          />
          {isDone && (
            <View style={styles.doneFooter}>
              <Text style={styles.doneText}>
                ✓ Research complete · Powered by Claude Opus
              </Text>
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  title: { fontSize: 22, fontWeight: '800', color: Colors.textPrimary },
  subtitle: { fontSize: 13, color: Colors.accent, marginTop: 3 },
  refreshBtn: {
    backgroundColor: Colors.bgElevated,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  refreshText: { color: Colors.accent, fontWeight: '600', fontSize: 14 },
  errorBox: {
    margin: 20,
    padding: 16,
    backgroundColor: `${Colors.bearish}15`,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.bearish,
  },
  errorText: { color: Colors.bearish, fontSize: 14 },
  retryBtn: {
    marginTop: 10,
    backgroundColor: Colors.bearish,
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
  },
  retryText: { color: '#fff', fontWeight: '700' },
  initialLoading: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 16 },
  loadingText: { color: Colors.textSecondary, fontSize: 14 },
  scroll: { flex: 1 },
  scrollContent: { padding: 20, paddingBottom: 40 },
  doneFooter: {
    marginTop: 24,
    padding: 12,
    backgroundColor: `${Colors.bullish}10`,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: `${Colors.bullish}40`,
    alignItems: 'center',
  },
  doneText: { color: Colors.bullish, fontSize: 13, fontWeight: '500' },
});
