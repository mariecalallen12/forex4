import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const tradingApi = {
  async placeOrder(orderData) {
    try {
      const response = await api.post('/api/trading/orders', orderData);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to place order');
      }
      throw error;
    }
  },

  async cancelOrder(orderId) {
    try {
      // Try PUT first (cancel endpoint), fallback to DELETE
      const response = await api.put(`/api/trading/orders/${orderId}/cancel`).catch(() => {
        return api.delete(`/api/trading/orders/${orderId}`);
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to cancel order');
      }
      throw error;
    }
  },

  async getOrders(filters = {}) {
    try {
      const response = await api.get('/api/trading/orders', { params: filters });
      // Handle nested response structure
      if (response.data.orders) {
        return response.data;
      }
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch orders');
      }
      throw error;
    }
  },

  async getPositions(symbol = null) {
    try {
      const params = symbol ? { symbol } : {};
      const response = await api.get('/api/trading/positions', { params });
      // Handle nested response structure
      if (response.data.positions) {
        return response.data;
      }
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch positions');
      }
      throw error;
    }
  },

  async closePosition(positionId) {
    try {
      // Try POST first, fallback to DELETE
      const response = await api.post(`/api/trading/positions/${positionId}/close`).catch(() => {
        return api.delete(`/api/trading/positions/${positionId}`);
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to close position');
      }
      throw error;
    }
  },

  async getOrderHistory(filters = {}) {
    try {
      const response = await api.get('/api/trading/orders/history', { params: filters });
      // Handle nested response structure
      if (response.data.orders) {
        return response.data;
      }
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch order history');
      }
      throw error;
    }
  },

  async getStatistics() {
    try {
      const response = await api.get('/api/trading/statistics');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch statistics');
      }
      throw error;
    }
  },

  async getOrderbook(symbol) {
    try {
      const response = await api.get('/api/trading/orderbook', { params: { symbol } });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch orderbook');
      }
      throw error;
    }
  },

  async getTrades(filters = {}) {
    try {
      const response = await api.get('/api/trading/trades', { params: filters });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch trades');
      }
      throw error;
    }
  },

  async getPairs() {
    try {
      const response = await api.get('/api/trading/pairs');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch pairs');
      }
      throw error;
    }
  },

  async getRules() {
    try {
      const response = await api.get('/api/trading/rules');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch rules');
      }
      throw error;
    }
  },

  async getRiskAssessment() {
    try {
      const response = await api.get('/api/trading/risk-assessment');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch risk assessment');
      }
      throw error;
    }
  },
};
