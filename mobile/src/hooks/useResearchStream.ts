import { useState, useCallback, useRef } from 'react';
import { api } from '../services/api';
import { Platform } from 'react-native';

interface StreamState {
  content: string;
  isStreaming: boolean;
  isThinking: boolean;
  toolsUsed: string[];
  error: string | null;
  isDone: boolean;
}

export function useResearchStream(ticker: string) {
  const [state, setState] = useState<StreamState>({
    content: '',
    isStreaming: false,
    isThinking: false,
    toolsUsed: [],
    error: null,
    isDone: false,
  });
  const abortRef = useRef<(() => void) | null>(null);

  const startResearch = useCallback(async () => {
    // Cancel any in-progress stream
    abortRef.current?.();

    setState({
      content: '',
      isStreaming: true,
      isThinking: false,
      toolsUsed: [],
      error: null,
      isDone: false,
    });

    const url = api.getResearchStreamUrl(ticker);
    let aborted = false;
    abortRef.current = () => { aborted = true; };

    try {
      if (Platform.OS === 'web') {
        // Web: use native EventSource
        await streamWithEventSource(url, aborted, setState, abortRef);
      } else {
        // Native: use fetch with streaming body reader
        await streamWithFetch(url, aborted, setState);
      }
    } catch (err) {
      if (!aborted) {
        setState(prev => ({
          ...prev,
          isStreaming: false,
          error: err instanceof Error ? err.message : 'Stream failed',
        }));
      }
    }
  }, [ticker]);

  const cancel = useCallback(() => {
    abortRef.current?.();
    setState(prev => ({ ...prev, isStreaming: false }));
  }, []);

  return { ...state, startResearch, cancel };
}


async function streamWithFetch(
  url: string,
  aborted: boolean,
  setState: React.Dispatch<React.SetStateAction<StreamState>>,
) {
  const controller = new AbortController();
  const res = await fetch(url, { signal: controller.signal });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  if (!res.body) throw new Error('No response body');

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (!aborted) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (!line.startsWith('data:')) continue;
      const payload = line.slice(5).trim();
      if (!payload) continue;
      processEvent(payload, setState);
    }
  }
}


async function streamWithEventSource(
  url: string,
  aborted: boolean,
  setState: React.Dispatch<React.SetStateAction<StreamState>>,
  abortRef: React.MutableRefObject<(() => void) | null>,
) {
  return new Promise<void>((resolve, reject) => {
    const es = new EventSource(url);
    abortRef.current = () => {
      es.close();
      resolve();
    };

    es.onmessage = (event) => {
      processEvent(event.data, setState);
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'done') {
          es.close();
          resolve();
        }
      } catch {}
    };

    es.onerror = () => {
      es.close();
      reject(new Error('EventSource error'));
    };
  });
}


function processEvent(
  payload: string,
  setState: React.Dispatch<React.SetStateAction<StreamState>>,
) {
  try {
    const data = JSON.parse(payload);

    if (data.type === 'text') {
      setState(prev => ({
        ...prev,
        content: prev.content + (data.content ?? ''),
        isThinking: false,
      }));
    } else if (data.type === 'thinking') {
      setState(prev => ({ ...prev, isThinking: true }));
    } else if (data.type === 'tool_call') {
      setState(prev => ({
        ...prev,
        toolsUsed: prev.toolsUsed.includes(data.tool)
          ? prev.toolsUsed
          : [...prev.toolsUsed, data.tool],
      }));
    } else if (data.type === 'done') {
      setState(prev => ({
        ...prev,
        isStreaming: false,
        isThinking: false,
        isDone: true,
      }));
    }
  } catch {
    // Non-JSON line, ignore
  }
}
