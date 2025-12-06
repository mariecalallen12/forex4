import { defineStore } from 'pinia';
import { ref } from 'vue';
import clientApi from '../services/api/client';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Giữ lại instance api cũ cho export /financial/transactions/export nếu backend đã hỗ trợ
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

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref([]);
  const deposits = ref([]);
  const withdrawals = ref([]);
  const orders = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    limit: 50,
    total: 0,
  });

  async function fetchTransactions(filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const params = {
        ...filters,
        page: filters.page || pagination.value.page,
        limit: filters.limit || pagination.value.limit,
      };

      // Ưu tiên dùng clientApi.getTransactions (module client),
      // fallback sang /api/financial/transactions nếu cần.
      let data;
      try {
        const clientResponse = await clientApi.getTransactions(params);
        data = clientResponse;
      } catch {
        const response = await api.get('/api/financial/transactions', { params });
        data = response.data;
      }

      const payload = data.data || data;

      if (payload.transactions) {
        transactions.value = payload.transactions;
      } else if (Array.isArray(payload)) {
        transactions.value = payload;
      } else if (Array.isArray(payload.items)) {
        transactions.value = payload.items;
      } else {
        transactions.value = [];
      }

      if (payload.pagination?.total !== undefined) {
        pagination.value.total = payload.pagination.total;
      } else if (payload.total !== undefined) {
        pagination.value.total = payload.total;
      } else if (payload.count !== undefined) {
        pagination.value.total = payload.count;
      }

      // Separate by type
      deposits.value = transactions.value.filter(t => t.type === 'deposit' || t.transaction_type === 'deposit');
      withdrawals.value = transactions.value.filter(t => t.type === 'withdrawal' || t.transaction_type === 'withdrawal');
      
      return data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to fetch transactions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function exportTransactions(format = 'csv', filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const params = {
        ...filters,
        format,
      };
      const response = await api.get('/api/financial/transactions/export', {
        params,
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to export transactions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    transactions,
    deposits,
    withdrawals,
    orders,
    isLoading,
    error,
    pagination,
    fetchTransactions,
    exportTransactions,
  };
});
