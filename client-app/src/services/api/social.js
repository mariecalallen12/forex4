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

export const socialApi = {
  async getFeed() {
    try {
      const response = await api.get('/api/trading/social/feed');
      return response.data;
    } catch (error) {
      // Return mock data if API fails
      console.warn('Social feed API not available, using mock data');
      return {
        feed: [
          {
            id: '1',
            content: 'EUR/USD đang test resistance 1.0850, có thể breakout!',
            author: 'Trader Pro',
            likes: 12,
            comments: 3,
            timestamp: Date.now() - 3600000,
          },
          {
            id: '2',
            content: 'BTC tăng mạnh, cần cẩn thận với correction.',
            author: 'Crypto Expert',
            likes: 8,
            comments: 5,
            timestamp: Date.now() - 7200000,
          },
        ],
      };
    }
  },

  async getRankings() {
    try {
      const response = await api.get('/api/trading/social/rankings');
      return response.data;
    } catch (error) {
      console.warn('Rankings API not available');
      return { rankings: [] };
    }
  },

  async likePost(postId) {
    try {
      const response = await api.post(`/api/trading/social/posts/${postId}/like`);
      return response.data;
    } catch (error) {
      console.warn('Like post API not available');
      return { likes: 0 };
    }
  },

  async commentPost(postId, data) {
    try {
      const response = await api.post(`/api/trading/social/posts/${postId}/comment`, data);
      return response.data;
    } catch (error) {
      console.warn('Comment post API not available');
      return { comments: 0 };
    }
  },
};

