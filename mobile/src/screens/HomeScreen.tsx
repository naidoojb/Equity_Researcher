import React, { useState, useCallback } from 'react';
import {
  View, Text, TextInput, FlatList, TouchableOpacity,
  StyleSheet, SafeAreaView, ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Colors } from '../theme/colors';
import { api, SearchResult } from '../services/api';

const TRENDING = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'META', 'AMZN', 'JPM'];

export function HomeScreen() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [debounceTimer, setDebounceTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  const handleSearch = useCallback((text: string) => {
    setQuery(text);
    if (debounceTimer) clearTimeout(debounceTimer);

    if (!text.trim()) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await api.search(text.trim());
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    setDebounceTimer(timer);
  }, [debounceTimer]);

  const navigateToStock = (ticker: string) => {
    setQuery('');
    setResults([]);
    router.push(`/stock/${ticker}`);
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.brand}>Equity Researcher</Text>
        <Text style={styles.tagline}>AI-powered daily signals & deep research</Text>

        {/* Search bar */}
        <View style={styles.searchRow}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.input}
            placeholder="Search ticker or company..."
            placeholderTextColor={Colors.textMuted}
            value={query}
            onChangeText={handleSearch}
            autoCapitalize="characters"
            autoCorrect={false}
          />
          {loading && <ActivityIndicator size="small" color={Colors.accent} />}
          {query.length > 0 && !loading && (
            <TouchableOpacity onPress={() => { setQuery(''); setResults([]); }}>
              <Text style={styles.clearBtn}>✕</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Search results */}
        {results.length > 0 && (
          <View style={styles.resultsCard}>
            {results.map(r => (
              <TouchableOpacity
                key={r.ticker}
                style={styles.resultRow}
                onPress={() => navigateToStock(r.ticker)}
              >
                <View>
                  <Text style={styles.resultTicker}>{r.ticker}</Text>
                  <Text style={styles.resultName}>{r.name}</Text>
                </View>
                <View style={styles.resultMeta}>
                  <Text style={styles.resultExchange}>{r.exchange}</Text>
                  {r.sector && <Text style={styles.resultSector}>{r.sector}</Text>}
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Trending */}
        {results.length === 0 && (
          <>
            <Text style={styles.sectionTitle}>Trending</Text>
            <View style={styles.trendingGrid}>
              {TRENDING.map(ticker => (
                <TouchableOpacity
                  key={ticker}
                  style={styles.trendingChip}
                  onPress={() => navigateToStock(ticker)}
                >
                  <Text style={styles.trendingText}>{ticker}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={styles.sectionTitle}>Sectors</Text>
            {[
              { label: '🤖 Technology', tickers: ['AAPL', 'MSFT', 'NVDA'] },
              { label: '🏥 Healthcare', tickers: ['JNJ', 'UNH', 'PFE'] },
              { label: '⚡ Energy', tickers: ['XOM', 'CVX', 'COP'] },
              { label: '💰 Financials', tickers: ['JPM', 'BAC', 'GS'] },
            ].map(sector => (
              <View key={sector.label} style={styles.sectorRow}>
                <Text style={styles.sectorLabel}>{sector.label}</Text>
                <View style={styles.sectorTickers}>
                  {sector.tickers.map(t => (
                    <TouchableOpacity
                      key={t}
                      style={styles.sectorChip}
                      onPress={() => navigateToStock(t)}
                    >
                      <Text style={styles.sectorChipText}>{t}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            ))}
          </>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  container: { flex: 1, padding: 20 },
  brand: { fontSize: 28, fontWeight: '800', color: Colors.textPrimary, marginBottom: 4 },
  tagline: { fontSize: 14, color: Colors.textMuted, marginBottom: 24 },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: 14,
    marginBottom: 16,
  },
  searchIcon: { fontSize: 16, marginRight: 8 },
  input: { flex: 1, height: 48, fontSize: 16, color: Colors.textPrimary },
  clearBtn: { fontSize: 16, color: Colors.textMuted, padding: 4 },
  resultsCard: {
    backgroundColor: Colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: 'hidden',
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  resultTicker: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary },
  resultName: { fontSize: 13, color: Colors.textSecondary, marginTop: 2 },
  resultMeta: { alignItems: 'flex-end' },
  resultExchange: { fontSize: 12, color: Colors.textMuted },
  resultSector: { fontSize: 11, color: Colors.accent, marginTop: 2 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: Colors.textPrimary, marginBottom: 12, marginTop: 8 },
  trendingGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 24 },
  trendingChip: {
    backgroundColor: Colors.bgCard,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  trendingText: { fontSize: 15, fontWeight: '700', color: Colors.textPrimary },
  sectorRow: { marginBottom: 14 },
  sectorLabel: { fontSize: 14, fontWeight: '600', color: Colors.textSecondary, marginBottom: 8 },
  sectorTickers: { flexDirection: 'row', gap: 8 },
  sectorChip: {
    backgroundColor: Colors.bgElevated,
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  sectorChipText: { fontSize: 13, fontWeight: '600', color: Colors.accent },
});
