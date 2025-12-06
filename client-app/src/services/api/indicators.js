import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const indicatorsApi = {
  async getIndicators(country = null) {
    try {
      const response = await api.get('/api/market/indicators', {
        params: country ? { country } : {},
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch indicators');
      }
      // Return mock data if API fails
      return [];
    }
  },

  async getIndicatorById(id) {
    try {
      const response = await api.get(`/api/market/indicators/${id}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch indicator');
      }
      throw error;
    }
  },
};

