import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const newsApi = {
  async getNews(filters = {}) {
    try {
      const response = await api.get('/api/market/news', {
        params: filters,
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch news');
      }
      // Return mock data if API fails
      return [];
    }
  },

  async getNewsById(id) {
    try {
      const response = await api.get(`/api/market/news/${id}`);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch news item');
      }
      throw error;
    }
  },
};

