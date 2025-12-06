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

export const clientApi = {
  async getDashboard() {
    const response = await api.get('/api/client/dashboard');
    // Chuẩn hoá: trả về object dạng { overview, stats, recentTransactions, riskScore, complianceStatus, exchangeRates, ... }
    const data = response.data;
    if (data.data) {
      // Trường hợp backend bọc trong { success, data, exchangeRates, ... }
      return {
        ...data,
        data: {
          ...data.data,
          exchangeRates: data.exchangeRates || data.data.exchangeRates,
        },
      };
    }
    return data;
  },

  async getWalletBalances(params = {}) {
    const response = await api.get('/api/client/wallet-balances', { params });
    return response.data;
  },

  async getTransactions(params = {}) {
    const response = await api.get('/api/client/transactions', { params });
    return response.data;
  },

  async getExchangeRates() {
    const response = await api.get('/api/client/exchange-rates');
    return response.data;
  },

  /**
   * Create crypto deposit address based on selected currency and network
   * Returns the inner data object when available.
   */
  async createCryptoDepositAddress(payload) {
    const response = await api.post('/api/client/crypto-deposit-address', payload);
    const data = response.data;
    return data?.data || data;
  },

  /**
   * Generate VietQR payment data for bank transfer deposits
   * Returns the inner data object when available.
   */
  async generateVietQR(payload) {
    const response = await api.post('/api/client/generate-vietqr', payload);
    const data = response.data;
    return data?.data || data;
  },
};

export default clientApi;
