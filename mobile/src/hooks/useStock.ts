import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function useOverview(ticker: string) {
  return useQuery({
    queryKey: ['overview', ticker],
    queryFn: () => api.getOverview(ticker),
    enabled: !!ticker,
    staleTime: 60_000,
    refetchInterval: 60_000,
  });
}

export function useSignals(ticker: string) {
  return useQuery({
    queryKey: ['signals', ticker],
    queryFn: () => api.getSignals(ticker),
    enabled: !!ticker,
    staleTime: 120_000,
    refetchInterval: 120_000,
  });
}

export function useNews(ticker: string) {
  return useQuery({
    queryKey: ['news', ticker],
    queryFn: () => api.getNews(ticker),
    enabled: !!ticker,
    staleTime: 900_000,
  });
}

export function useTechnicals(ticker: string) {
  return useQuery({
    queryKey: ['technicals', ticker],
    queryFn: () => api.getTechnicals(ticker),
    enabled: !!ticker,
    staleTime: 300_000,
  });
}

export function useFundamentals(ticker: string) {
  return useQuery({
    queryKey: ['fundamentals', ticker],
    queryFn: () => api.getFundamentals(ticker),
    enabled: !!ticker,
    staleTime: 3_600_000,
  });
}

export function useCompetitors(ticker: string) {
  return useQuery({
    queryKey: ['competitors', ticker],
    queryFn: () => api.getCompetitors(ticker),
    enabled: !!ticker,
    staleTime: 3_600_000,
  });
}
