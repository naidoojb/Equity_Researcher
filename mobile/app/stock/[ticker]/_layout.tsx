import React from 'react';
import { Tabs, useLocalSearchParams } from 'expo-router';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Colors } from '../../../src/theme/colors';
import { useOverview } from '../../../src/hooks/useStock';

export default function StockTabLayout() {
  const { ticker } = useLocalSearchParams<{ ticker: string }>();
  const router = useRouter();
  const { data: overview } = useOverview(ticker);

  return (
    <>
      {/* Stock header bar */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backArrow}>‹</Text>
        </TouchableOpacity>
        <View style={styles.tickerInfo}>
          <Text style={styles.tickerText}>{ticker}</Text>
          {overview && (
            <Text
              style={[
                styles.priceText,
                { color: overview.change >= 0 ? Colors.bullish : Colors.bearish },
              ]}
            >
              ${overview.price.toFixed(2)}{' '}
              {overview.change >= 0 ? '▲' : '▼'}{Math.abs(overview.change_pct).toFixed(2)}%
            </Text>
          )}
        </View>
      </View>

      <Tabs
        screenOptions={{
          tabBarStyle: styles.tabBar,
          tabBarLabelStyle: styles.tabLabel,
          tabBarActiveTintColor: Colors.accent,
          tabBarInactiveTintColor: Colors.textMuted,
          headerShown: false,
        }}
      >
        <Tabs.Screen
          name="index"
          options={{ title: 'Overview', tabBarLabel: 'Overview' }}
        />
        <Tabs.Screen
          name="signals"
          options={{ title: 'Signals', tabBarLabel: 'Signals' }}
        />
        <Tabs.Screen
          name="news"
          options={{ title: 'News', tabBarLabel: 'News' }}
        />
        <Tabs.Screen
          name="technicals"
          options={{ title: 'Technicals', tabBarLabel: 'Tech' }}
        />
        <Tabs.Screen
          name="fundamentals"
          options={{ title: 'Fundamentals', tabBarLabel: 'Fundmtls' }}
        />
        <Tabs.Screen
          name="competitors"
          options={{ title: 'Competitors', tabBarLabel: 'Peers' }}
        />
        <Tabs.Screen
          name="research"
          options={{ title: 'AI Report', tabBarLabel: 'AI' }}
        />
      </Tabs>
    </>
  );
}

const styles = StyleSheet.create({
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.bgCard,
    paddingTop: 52,
    paddingBottom: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  backBtn: { marginRight: 12, padding: 4 },
  backArrow: { fontSize: 28, color: Colors.accent, lineHeight: 28 },
  tickerInfo: { flex: 1 },
  tickerText: { fontSize: 20, fontWeight: '800', color: Colors.textPrimary },
  priceText: { fontSize: 14, fontWeight: '600', marginTop: 2 },
  tabBar: {
    backgroundColor: Colors.bgCard,
    borderTopColor: Colors.border,
    borderTopWidth: 1,
    height: 56,
    paddingBottom: 6,
  },
  tabLabel: { fontSize: 10, fontWeight: '600' },
});
