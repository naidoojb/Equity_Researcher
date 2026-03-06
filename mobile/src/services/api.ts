const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

// ─── Types ─────────────────────────────────────────────────────────────────

export interface StockOverview {
  ticker: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  avg_volume: number;
  market_cap: number | null;
  week_52_high: number;
  week_52_low: number;
  currency: string;
  exchange: string;
  sector: string | null;
  industry: string | null;
}

export interface Signal {
  label: string;
  value: string;
  direction: 'bullish' | 'bearish' | 'neutral';
}

export interface SignalsResponse {
  ticker: string;
  signal: 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
  score: number;
  signals: Signal[];
  updated_at: string;
}

export interface NewsItem {
  title: string;
  source: string;
  url: string;
  published_at: string;
  sentiment: number;
  sentiment_label: 'Positive' | 'Negative' | 'Neutral';
  summary: string | null;
}

export interface NewsResponse {
  ticker: string;
  articles: NewsItem[];
  avg_sentiment: number;
}

export interface TechnicalIndicators {
  ticker: string;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_hist: number | null;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  bb_upper: number | null;
  bb_lower: number | null;
  bb_middle: number | null;
  price: number;
  signals: Signal[];
}

export interface Fundamentals {
  ticker: string;
  pe_ratio: number | null;
  forward_pe: number | null;
  eps: number | null;
  revenue: number | null;
  revenue_growth: number | null;
  gross_margin: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  debt_to_equity: number | null;
  current_ratio: number | null;
  dividend_yield: number | null;
  book_value: number | null;
  price_to_book: number | null;
  beta: number | null;
}

export interface Competitor {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  market_cap: number | null;
  pe_ratio: number | null;
}

export interface CompetitorsResponse {
  ticker: string;
  sector: string | null;
  competitors: Competitor[];
}

export interface SearchResult {
  ticker: string;
  name: string;
  exchange: string;
  sector: string | null;
}

// ─── API helpers ───────────────────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }
  return res.json() as Promise<T>;
}

// ─── Endpoints ─────────────────────────────────────────────────────────────

export const api = {
  search: (q: string) =>
    get<SearchResult[]>(`/api/search?q=${encodeURIComponent(q)}`),

  getOverview: (ticker: string) =>
    get<StockOverview>(`/api/stock/${ticker}`),

  getSignals: (ticker: string) =>
    get<SignalsResponse>(`/api/stock/${ticker}/signals`),

  getNews: (ticker: string) =>
    get<NewsResponse>(`/api/stock/${ticker}/news`),

  getTechnicals: (ticker: string) =>
    get<TechnicalIndicators>(`/api/stock/${ticker}/technicals`),

  getFundamentals: (ticker: string) =>
    get<Fundamentals>(`/api/stock/${ticker}/fundamentals`),

  getCompetitors: (ticker: string) =>
    get<CompetitorsResponse>(`/api/stock/${ticker}/competitors`),

  /** Returns the SSE URL for the research stream */
  getResearchStreamUrl: (ticker: string) =>
    `${API_URL}/api/stock/${ticker}/research`,
};

// ─── Formatting helpers ────────────────────────────────────────────────────

export function formatMarketCap(cap: number | null): string {
  if (cap == null) return 'N/A';
  if (cap >= 1e12) return `$${(cap / 1e12).toFixed(2)}T`;
  if (cap >= 1e9) return `$${(cap / 1e9).toFixed(2)}B`;
  if (cap >= 1e6) return `$${(cap / 1e6).toFixed(2)}M`;
  return `$${cap.toLocaleString()}`;
}

export function formatVolume(vol: number): string {
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(1)}B`;
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(1)}M`;
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(0)}K`;
  return vol.toString();
}

export function formatPct(val: number | null, decimals = 1): string {
  if (val == null) return 'N/A';
  return `${(val * 100).toFixed(decimals)}%`;
}
