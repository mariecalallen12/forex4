import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { indicatorsApi } from '../services/api/indicators';

export const useIndicatorsStore = defineStore('indicators', () => {
  const indicators = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const lastUpdate = ref(null);

  // Mock economic indicators data
  const mockIndicators = [
    {
      id: 'gdp',
      name: 'GDP',
      country: 'US',
      value: 2.1,
      unit: '%',
      change: 0.2,
      changePercent: 10.5,
      status: 'positive',
      trend: [2.0, 2.1, 2.05, 2.1, 2.15, 2.1],
      updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
      description: 'Tổng sản phẩm quốc nội',
    },
    {
      id: 'inflation',
      name: 'Lạm phát',
      country: 'US',
      value: 3.2,
      unit: '%',
      change: -0.1,
      changePercent: -3.0,
      status: 'positive',
      trend: [3.5, 3.4, 3.3, 3.2, 3.2, 3.2],
      updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      description: 'Chỉ số giá tiêu dùng (CPI)',
    },
    {
      id: 'interest-rate',
      name: 'Lãi suất',
      country: 'US',
      value: 5.25,
      unit: '%',
      change: 0,
      changePercent: 0,
      status: 'neutral',
      trend: [5.25, 5.25, 5.25, 5.25, 5.25, 5.25],
      updatedAt: new Date(Date.now() - 30 * 60 * 1000),
      description: 'Lãi suất cơ bản của Fed',
    },
    {
      id: 'unemployment',
      name: 'Tỷ lệ thất nghiệp',
      country: 'US',
      value: 3.7,
      unit: '%',
      change: -0.1,
      changePercent: -2.6,
      status: 'positive',
      trend: [3.8, 3.7, 3.8, 3.7, 3.7, 3.7],
      updatedAt: new Date(Date.now() - 3 * 60 * 60 * 1000),
      description: 'Tỷ lệ thất nghiệp',
    },
    {
      id: 'gdp-eu',
      name: 'GDP',
      country: 'EU',
      value: 1.5,
      unit: '%',
      change: 0.1,
      changePercent: 7.1,
      status: 'positive',
      trend: [1.4, 1.5, 1.4, 1.5, 1.5, 1.5],
      updatedAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
      description: 'Tổng sản phẩm quốc nội Châu Âu',
    },
    {
      id: 'inflation-eu',
      name: 'Lạm phát',
      country: 'EU',
      value: 2.9,
      unit: '%',
      change: -0.2,
      changePercent: -6.5,
      status: 'positive',
      trend: [3.1, 3.0, 2.9, 2.9, 2.9, 2.9],
      updatedAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
      description: 'Chỉ số giá tiêu dùng Châu Âu',
    },
  ];

  indicators.value = mockIndicators;
  lastUpdate.value = new Date();

  const indicatorsByCountry = computed(() => {
    const grouped = {};
    indicators.value.forEach(indicator => {
      if (!grouped[indicator.country]) {
        grouped[indicator.country] = [];
      }
      grouped[indicator.country].push(indicator);
    });
    return grouped;
  });

  async function fetchIndicators() {
    loading.value = true;
    error.value = null;
    try {
      const data = await indicatorsApi.getIndicators();
      indicators.value = data;
      lastUpdate.value = new Date();
    } catch (err) {
      error.value = err.message;
      console.error('Failed to fetch indicators:', err);
    } finally {
      loading.value = false;
    }
  }

  function getIndicatorById(id) {
    return indicators.value.find(ind => ind.id === id);
  }

  function getIndicatorsByCountry(country) {
    return indicators.value.filter(ind => ind.country === country);
  }

  return {
    indicators,
    indicatorsByCountry,
    loading,
    error,
    lastUpdate,
    fetchIndicators,
    getIndicatorById,
    getIndicatorsByCountry,
  };
});

