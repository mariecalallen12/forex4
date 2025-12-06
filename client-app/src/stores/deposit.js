import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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

export const useDepositStore = defineStore('deposit', () => {
  const deposits = ref([]);
  const currentDeposit = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  async function createDeposit(depositData) {
    isLoading.value = true;
    error.value = null;

    try {
      // Map frontend format to backend format
      const backendData = {
        amount: depositData.amount,
        currency: depositData.currency || { value: depositData.currency || 'usdt' },
        method: depositData.method || { value: depositData.method || 'crypto_deposit' },
        walletAddress: depositData.walletAddress,
        bankAccount: depositData.bankAccount,
        transactionId: depositData.transactionId,
        notes: depositData.notes
      };
      
      const response = await api.post('/api/financial/deposits', backendData);
      // Handle nested response structure
      if (response.data.data && response.data.data.deposit) {
        currentDeposit.value = response.data.data.deposit;
      } else if (response.data.deposit) {
        currentDeposit.value = response.data.deposit;
      }
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create deposit';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchDeposits(filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/api/financial/deposits', { params: filters });
      deposits.value = response.data.data?.deposits || [];
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch deposits';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function getDepositById(depositId) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/api/financial/deposits/${depositId}`);
      currentDeposit.value = response.data.data?.deposit;
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch deposit';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    deposits,
    currentDeposit,
    isLoading,
    error,
    createDeposit,
    fetchDeposits,
    getDepositById,
  };
});

