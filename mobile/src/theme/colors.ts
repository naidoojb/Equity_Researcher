export const Colors = {
  // Backgrounds
  bg: '#0A0A0F',
  bgCard: '#12121A',
  bgElevated: '#1A1A26',
  bgInput: '#1E1E2E',

  // Brand
  accent: '#6C63FF',
  accentLight: '#8B85FF',

  // Signal colors
  bullish: '#00C896',
  bearish: '#FF4757',
  neutral: '#FFA502',

  // Text
  textPrimary: '#F0F0FF',
  textSecondary: '#9090B0',
  textMuted: '#606080',

  // Borders
  border: '#2A2A3A',
  borderLight: '#3A3A4A',

  // Chart colors
  chartLine: '#6C63FF',
  chartFill: 'rgba(108,99,255,0.15)',
} as const;

export const SignalColors = {
  'STRONG BUY': Colors.bullish,
  'BUY': '#00E5A0',
  'HOLD': Colors.neutral,
  'SELL': '#FF6B6B',
  'STRONG SELL': Colors.bearish,
} as const;
