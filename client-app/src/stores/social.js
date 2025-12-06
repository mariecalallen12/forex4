import { defineStore } from 'pinia';
import { ref } from 'vue';
import { socialApi } from '../services/api/social';

export const useSocialStore = defineStore('social', () => {
  const feed = ref([
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
  ]);

  const traderRankings = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchFeed() {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await socialApi.getFeed();
      feed.value = response.feed || feed.value;
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch feed';
      // Use mock data if API fails
      console.warn('Using mock social feed data');
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchRankings() {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await socialApi.getRankings();
      traderRankings.value = response.rankings || [];
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch rankings';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function likePost(postId) {
    try {
      const response = await socialApi.likePost(postId);
      const post = feed.value.find(p => p.id === postId);
      if (post) {
        post.likes = response.likes || post.likes + 1;
      }
      return response;
    } catch (err) {
      console.error('Failed to like post:', err);
    }
  }

  async function commentPost(postId, comment) {
    try {
      const response = await socialApi.commentPost(postId, { comment });
      const post = feed.value.find(p => p.id === postId);
      if (post) {
        post.comments = response.comments || post.comments + 1;
      }
      return response;
    } catch (err) {
      console.error('Failed to comment on post:', err);
    }
  }

  return {
    feed,
    traderRankings,
    isLoading,
    error,
    fetchFeed,
    fetchRankings,
    likePost,
    commentPost,
  };
});

