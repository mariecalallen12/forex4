import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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

export const accountApi = {
  async login(credentials) {
    try {
      const response = await api.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Login failed');
      }
      throw error;
    }
  },
  
  // Note: Use authApi from services/api/auth.js for full authentication features

  async getBalance() {
    try {
      const response = await api.get('/api/financial/balance');
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch balance');
      }
      throw error;
    }
  },

  async deposit(data) {
    try {
      const response = await api.post('/api/financial/deposit', data);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to deposit');
      }
      throw error;
    }
  },

  async withdraw(data) {
    try {
      const response = await api.post('/api/financial/withdraw', data);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to withdraw');
      }
      throw error;
    }
  },

  async getTransactionHistory(filters = {}) {
    try {
      const response = await api.get('/api/financial/transactions', { params: filters });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch transaction history');
      }
      throw error;
    }
  },
};
