<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Tỷ Giá Hối Đoái</h1>
      <p class="text-purple-300">Tỷ giá USDT với các loại tiền tệ khác</p>
    </div>

    <!-- Rate Cards -->
    <RateCards />

    <!-- Currency Converter -->
    <CurrencyConverter />

    <!-- Update Status -->
    <div class="glass-panel rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div
            :class="[
              'w-3 h-3 rounded-full',
              updateStatus === 'fresh' ? 'bg-green-500' : updateStatus === 'recent' ? 'bg-yellow-500' : 'bg-red-500'
            ]"
          ></div>
          <div class="text-purple-300 text-sm">
            Cập nhật lần cuối: {{ formatLastUpdate }}
          </div>
        </div>
        <div class="text-purple-300 text-xs">
          Nguồn: Binance • Tự động cập nhật mỗi phút
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useExchangeRatesStore } from '../../stores/exchangeRates';
import RateCards from '../../components/personal/rates/RateCards.vue';
import CurrencyConverter from '../../components/personal/rates/CurrencyConverter.vue';

const exchangeRatesStore = useExchangeRatesStore();
const updateStatus = computed(() => exchangeRatesStore.updateStatus);

const formatLastUpdate = computed(() => {
  const date = exchangeRatesStore.lastUpdate;
  return date.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
});

onMounted(() => {
  exchangeRatesStore.startAutoRefresh();
});
</script>

