import { defineStore } from 'pinia';
import { ref } from 'vue';
import clientApi from '../services/api/client';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Fallback api instance cho các trường hợp đặc biệt nếu cần
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const useExchangeRatesStore = defineStore('exchangeRates', () => {
  const rates = ref([]);

  const isLoading = ref(false);
  const lastUpdate = ref(new Date());
  const updateStatus = ref('fresh'); // 'fresh', 'recent', 'stale'
  const error = ref(null);

  async function fetchRates() {
    isLoading.value = true;
    error.value = null;

    try {
      // Ưu tiên dùng clientApi.getExchangeRates() từ module client
      let payload;
      try {
        const clientResponse = await clientApi.getExchangeRates();
        payload = clientResponse;
      } catch {
        // Fallback: thử các endpoint cũ nếu có
        const response = await api.get('/api/financial/exchange-rates').catch(() => {
          return api.get('/api/market/market-data');
        });
        payload = response.data;
      }

      const data = payload.data || payload;

      if (Array.isArray(data)) {
        // Trường hợp client backend trả về list ExchangeRate
        rates.value = data.map((rate) => ({
          pair: `${rate.baseAsset}_${rate.targetAsset}`,
          from: rate.baseAsset,
          to: rate.targetAsset,
          rate: rate.rate,
          change24h: rate.change24h || 0,
          changeAmount: rate.changeAmount || 0,
          high: rate.high || rate.rate,
          low: rate.low || rate.rate,
        }));
      } else if (Array.isArray(data.rates) || Array.isArray(data.exchange_rates)) {
        const ratesData = data.rates || data.exchange_rates;
        rates.value = ratesData.map((rate) => ({
          pair: `${rate.from_currency}_${rate.to_currency}`,
          from: rate.from_currency,
          to: rate.to_currency,
          rate: rate.rate,
          change24h: rate.change_24h || 0,
          changeAmount: rate.change_amount || 0,
          high: rate.high_24h || rate.rate,
          low: rate.low_24h || rate.rate,
        }));
      }

      lastUpdate.value = new Date();
      updateStatus.value = 'fresh';
      
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch exchange rates';
      // Keep existing rates if fetch fails
      console.error('Error fetching exchange rates:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function updateRates(newRates) {
    rates.value = newRates;
    lastUpdate.value = new Date();
    updateStatus.value = 'fresh';
  }

  function getRate(from, to) {
    const pair = rates.value.find(r => r.from === from && r.to === to);
    return pair ? pair.rate : null;
  }

  // Auto-refresh every minute
  let refreshInterval = null;

  function startAutoRefresh() {
    // Initial fetch
    fetchRates();
    
    // Set interval based on env or default to 60 seconds
    const intervalMs = parseInt(import.meta.env.VITE_MARKET_DATA_UPDATE_INTERVAL || '60000', 10);
    
    refreshInterval = setInterval(() => {
      fetchRates().catch(err => {
        console.error('Auto-refresh exchange rates failed:', err);
        // Update status to stale if fetch fails
        const minutesSinceUpdate = (new Date() - lastUpdate.value) / 60000;
        if (minutesSinceUpdate >= 5) {
          updateStatus.value = 'stale';
        }
      });
    }, intervalMs);
  }

  function stopAutoRefresh() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  }

  return {
    rates,
    isLoading,
    lastUpdate,
    updateStatus,
    error,
    fetchRates,
    updateRates,
    getRate,
    startAutoRefresh,
    stopAutoRefresh,
  };
});
