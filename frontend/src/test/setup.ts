import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Leaflet CSS and window methods if needed in jsdom
window.scrollTo = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock fetch for JSDOM test environment
globalThis.fetch = vi.fn().mockImplementation(async (url: string) => {
  return {
    ok: true,
    status: 200,
    json: async () => {
      if (url.includes('/api/v1/properties')) {
        return [];
      }
      if (url.includes('/api/v1/recommendations')) {
        return {
          results: [],
          count: 0,
          total_eligible_candidates: 0,
          inference_time_ms: 1.0,
          model_name: 'test_model',
          model_version: '1.0',
          model_type: 'ml_ranker',
        };
      }
      return {};
    },
    text: async () => '',
  } as unknown as Response;
});
