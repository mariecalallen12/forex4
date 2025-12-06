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

export const useWithdrawStore = defineStore('withdraw', () => {
  const withdrawals = ref([]);
  const currentWithdrawal = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  async function createWithdrawal(withdrawalData) {
    isLoading.value = true;
    error.value = null;

    try {
      // Map frontend format to backend format
      const backendData = {
        amount: withdrawalData.amount,
        currency: withdrawalData.currency || { value: withdrawalData.currency || 'usdt' },
        method: withdrawalData.method || { value: withdrawalData.method || 'bank_transfer' },
        walletAddress: withdrawalData.walletAddress,
        bankAccount: withdrawalData.bankAccount,
        notes: withdrawalData.notes
      };
      
      const response = await api.post('/api/financial/withdrawals', backendData);
      // Handle nested response structure
      if (response.data.data && response.data.data.withdrawal) {
        currentWithdrawal.value = response.data.data.withdrawal;
      } else if (response.data.withdrawal) {
        currentWithdrawal.value = response.data.withdrawal;
      }
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create withdrawal';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchWithdrawals(filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/api/financial/withdrawals', { params: filters });
      withdrawals.value = response.data.data?.withdrawals || [];
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch withdrawals';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function getWithdrawalById(withdrawalId) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/api/financial/withdrawals/${withdrawalId}`);
      currentWithdrawal.value = response.data.data?.withdrawal;
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch withdrawal';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    withdrawals,
    currentWithdrawal,
    isLoading,
    error,
    createWithdrawal,
    fetchWithdrawals,
    getWithdrawalById,
  };
});

