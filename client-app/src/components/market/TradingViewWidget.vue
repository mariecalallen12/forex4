<template>
  <section class="mb-8">
    <div class="market-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-white">Biểu đồ TradingView</h2>
        <div class="flex items-center space-x-2">
          <select
            v-model="selectedTimeframe"
            @change="updateTimeframe"
            class="market-search-input px-3 py-1 text-sm"
          >
            <option value="1">1 phút</option>
            <option value="5">5 phút</option>
            <option value="15">15 phút</option>
            <option value="60">1 giờ</option>
            <option value="240">4 giờ</option>
            <option value="D">1 ngày</option>
          </select>
        </div>
      </div>
      
      <div class="w-full h-96 bg-slate-900 rounded-lg overflow-hidden">
        <!-- TradingView Widget -->
        <div
          v-if="showTradingView"
          ref="tradingViewContainer"
          class="w-full h-full"
        ></div>
        
        <!-- Lightweight Charts Fallback -->
        <div
          v-else
          ref="chartContainer"
          class="w-full h-full"
        ></div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useMarketStore } from '../../stores/market';
import { createChart } from 'lightweight-charts';

const marketStore = useMarketStore();
const tradingViewContainer = ref(null);
const chartContainer = ref(null);
const selectedTimeframe = ref('60');
const showTradingView = ref(false);
let chart = null;

const initializeTradingView = () => {
  // TradingView widget integration
  // Note: This requires TradingView widget script to be loaded
  if (window.TradingView && tradingViewContainer.value) {
    showTradingView.value = true;
    new window.TradingView.widget({
      autosize: true,
      symbol: marketStore.selectedInstrument?.symbol || 'BINANCE:BTCUSDT',
      interval: selectedTimeframe.value,
      theme: 'dark',
      style: '1',
      locale: 'vi',
      toolbar_bg: '#1a0b2e',
      enable_publishing: false,
      hide_top_toolbar: true,
      hide_legend: false,
      save_image: false,
      container_id: tradingViewContainer.value,
    });
  } else {
    // Fallback to Lightweight Charts
    initializeLightweightChart();
  }
};

const initializeLightweightChart = () => {
  if (!chartContainer.value) return;
  
  showTradingView.value = false;
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    layout: {
      background: { color: '#1a0b2e' },
      textColor: '#d1d5db',
    },
    grid: {
      vertLines: { color: '#374151' },
      horzLines: { color: '#374151' },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  });

  const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#ef4444',
    borderVisible: false,
    wickUpColor: '#10b981',
    wickDownColor: '#ef4444',
  });

  // Mock data
  const mockData = generateMockData();
  candlestickSeries.setData(mockData);

  chart.timeScale().fitContent();
};

const generateMockData = () => {
  const data = [];
  const now = Date.now();
  const basePrice = marketStore.selectedInstrument?.price || 50000;
  
  for (let i = 100; i >= 0; i--) {
    const time = (now - i * 60 * 60 * 1000) / 1000;
    const open = basePrice + (Math.random() - 0.5) * 1000;
    const close = open + (Math.random() - 0.5) * 500;
    const high = Math.max(open, close) + Math.random() * 200;
    const low = Math.min(open, close) - Math.random() * 200;
    
    data.push({
      time,
      open,
      high,
      low,
      close,
    });
  }
  
  return data;
};

const updateTimeframe = () => {
  if (chart) {
    chart.remove();
    chart = null;
  }
  initializeLightweightChart();
};

watch(() => marketStore.selectedInstrument, () => {
  if (chart) {
    chart.remove();
    chart = null;
  }
  initializeLightweightChart();
});

onMounted(() => {
  // Try TradingView first, fallback to Lightweight Charts
  setTimeout(() => {
    initializeTradingView();
  }, 100);
});

onUnmounted(() => {
  if (chart) {
    chart.remove();
  }
});
</script>

