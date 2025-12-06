import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const marketApi = {
  async getPrices(symbols = []) {
    try {
      const response = await api.get('/api/market/prices', {
        params: { symbols: symbols.join(',') },
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch prices');
      }
      throw error;
    }
  },

  async getOrderBook(symbol) {
    try {
      const response = await api.get(`/api/market/orderbook/${symbol}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch order book');
      }
      throw error;
    }
  },

  async getTradeHistory(symbol, limit = 100) {
    try {
      const response = await api.get(`/api/market/trades/${symbol}`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch trade history');
      }
      throw error;
    }
  },
};
