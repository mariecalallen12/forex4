import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { newsApi } from '../services/api/news';

export const useNewsStore = defineStore('news', () => {
  const newsItems = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const filters = ref({
    category: 'all',
    impact: 'all',
    timeframe: '24h',
  });

  // Mock news data
  const mockNews = [
    {
      id: 1,
      title: 'Fed giữ nguyên lãi suất, thị trường phản ứng tích cực',
      thumbnail: '/assets/images/news/fed-rates.jpg',
      category: 'monetary',
      impact: 'high',
      publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      summary: 'Cục Dự trữ Liên bang Mỹ quyết định giữ nguyên lãi suất ở mức 5.25-5.50%, phù hợp với kỳ vọng của thị trường.',
      marketImpact: 'positive',
    },
    {
      id: 2,
      title: 'Bitcoin vượt mốc $45,000 sau khi ETF được phê duyệt',
      thumbnail: '/assets/images/news/bitcoin-etf.jpg',
      category: 'crypto',
      impact: 'high',
      publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
      summary: 'Giá Bitcoin tăng mạnh sau khi SEC phê duyệt các ETF Bitcoin spot, mở ra cơ hội đầu tư mới.',
      marketImpact: 'positive',
    },
    {
      id: 3,
      title: 'Dữ liệu việc làm Mỹ tháng 12 vượt kỳ vọng',
      thumbnail: '/assets/images/news/jobs-data.jpg',
      category: 'economic',
      impact: 'medium',
      publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
      summary: 'Nền kinh tế Mỹ tạo thêm 216,000 việc làm trong tháng 12, cao hơn dự báo 170,000.',
      marketImpact: 'neutral',
    },
    {
      id: 4,
      title: 'Giá vàng giảm do đồng USD mạnh lên',
      thumbnail: '/assets/images/news/gold-price.jpg',
      category: 'commodity',
      impact: 'medium',
      publishedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
      summary: 'Giá vàng giảm xuống dưới $2,040/ounce khi đồng USD tăng giá trị so với các đồng tiền chính.',
      marketImpact: 'negative',
    },
    {
      id: 5,
      title: 'ECB cảnh báo về lạm phát dai dẳng',
      thumbnail: '/assets/images/news/ecb-inflation.jpg',
      category: 'monetary',
      impact: 'high',
      publishedAt: new Date(Date.now() - 15 * 60 * 60 * 1000),
      summary: 'Ngân hàng Trung ương Châu Âu cảnh báo lạm phát có thể vẫn ở mức cao trong năm 2024.',
      marketImpact: 'negative',
    },
  ];

  newsItems.value = mockNews;

  const filteredNews = computed(() => {
    let filtered = [...newsItems.value];

    if (filters.value.category !== 'all') {
      filtered = filtered.filter(item => item.category === filters.value.category);
    }

    if (filters.value.impact !== 'all') {
      filtered = filtered.filter(item => item.impact === filters.value.impact);
    }

    return filtered.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  });

  async function fetchNews() {
    loading.value = true;
    error.value = null;
    try {
      const data = await newsApi.getNews(filters.value);
      newsItems.value = data;
    } catch (err) {
      error.value = err.message;
      console.error('Failed to fetch news:', err);
    } finally {
      loading.value = false;
    }
  }

  function setFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function getNewsById(id) {
    return newsItems.value.find(item => item.id === id);
  }

  return {
    newsItems,
    filteredNews,
    loading,
    error,
    filters,
    fetchNews,
    setFilters,
    getNewsById,
  };
});

