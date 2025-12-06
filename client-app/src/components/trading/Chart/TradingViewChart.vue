<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4 h-full flex flex-col">
    <!-- Chart Header -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-bold text-white">
          {{ selectedSymbol }} {{ currentPrice }}
          <span
            :class="[
              'ml-2 text-sm',
              priceChange >= 0 ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
          </span>
        </h2>
      </div>
      <ChartControls v-model="timeframe" />
    </div>

    <!-- Chart Container -->
    <div ref="chartContainer" class="flex-1 min-h-[300px] sm:min-h-[400px] bg-slate-900/50 rounded-lg"></div>

    <!-- Chart Info -->
    <div class="grid grid-cols-4 gap-2 mt-4">
      <div class="bg-purple-500/20 rounded-lg p-2">
        <div class="text-xs text-gray-400">Mở cửa</div>
        <div class="text-sm font-bold text-green-400">{{ formatPrice(ohlcData.open) }}</div>
      </div>
      <div class="bg-purple-500/20 rounded-lg p-2">
        <div class="text-xs text-gray-400">Cao nhất</div>
        <div class="text-sm font-bold text-red-400">{{ formatPrice(ohlcData.high) }}</div>
      </div>
      <div class="bg-purple-500/20 rounded-lg p-2">
        <div class="text-xs text-gray-400">Thấp nhất</div>
        <div class="text-sm font-bold text-red-400">{{ formatPrice(ohlcData.low) }}</div>
      </div>
      <div class="bg-purple-500/20 rounded-lg p-2">
        <div class="text-xs text-gray-400">Đóng cửa</div>
        <div class="text-sm font-bold text-purple-400">{{ formatPrice(ohlcData.close) }}</div>
      </div>
    </div>

    <!-- AI Prediction -->
    <div class="mt-4 flex items-center justify-between text-sm">
      <div class="flex items-center space-x-2">
        <span class="text-gray-400">AI Prediction:</span>
        <span class="text-green-400 font-bold">{{ aiPrediction }}</span>
        <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-gray-400">Sentiment:</span>
        <span class="text-yellow-400 font-bold">{{ sentiment }}</span>
        <div class="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { createChart, ColorType } from 'lightweight-charts';
import { useMarketStore } from '../../../stores/market';
import { useWebSocketStore } from '../../../stores/websocket';
import ChartControls from './ChartControls.vue';

const marketStore = useMarketStore();
const wsStore = useWebSocketStore();
const chartContainer = ref(null);
let chart = null;
let candlestickSeries = null;
let resizeHandler = null;
let updateInterval = null;
let wsPriceUpdateHandler = null;

const timeframe = ref('1H');
const selectedSymbol = computed(() => marketStore.selectedInstrument?.symbol || 'EUR/USD');
const currentPrice = computed(() => {
  const priceData = marketStore.getPrice(selectedSymbol.value);
  return priceData.price || marketStore.selectedInstrument?.price || 1.0842;
});
const priceChange = computed(() => {
  const priceData = marketStore.getPrice(selectedSymbol.value);
  return priceData.changePercent || 0;
});

const ohlcData = ref({
  open: 1.0832,
  high: 1.0856,
  low: 1.0825,
  close: 1.0845,
});

const aiPrediction = ref('Tăng');
const sentiment = ref('Bullish');

const formatPrice = (price) => {
  return price.toFixed(4);
};

const initChart = () => {
  if (!chartContainer.value) return;

  chart = createChart(chartContainer.value, {
    layout: {
      background: { type: ColorType.Solid, color: '#1e293b' },
      textColor: '#e2e8f0',
    },
    grid: {
      vertLines: { color: '#334155' },
      horzLines: { color: '#334155' },
    },
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  });

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10B981',
    downColor: '#EF4444',
    borderVisible: false,
    wickUpColor: '#10B981',
    wickDownColor: '#EF4444',
  });

  // Generate sample data
  const generateSampleData = () => {
    const data = [];
    const basePrice = currentPrice.value;
    let currentTime = Math.floor(Date.now() / 1000) - 100 * 3600; // 100 hours ago
    
    for (let i = 0; i < 100; i++) {
      const open = basePrice + (Math.random() - 0.5) * 0.01;
      const close = open + (Math.random() - 0.5) * 0.01;
      const high = Math.max(open, close) + Math.random() * 0.005;
      const low = Math.min(open, close) - Math.random() * 0.005;
      
      data.push({
        time: currentTime,
        open: open,
        high: high,
        low: low,
        close: close,
      });
      
      currentTime += 3600; // 1 hour
    }
    
    return data;
  };

  candlestickSeries.setData(generateSampleData());
  chart.timeScale().fitContent();
};

const updateChart = () => {
  if (!candlestickSeries) return;
  
  const price = currentPrice.value;
  const time = Math.floor(Date.now() / 1000);
  
  // Update last candle
  candlestickSeries.update({
    time: time,
    open: ohlcData.value.open,
    high: Math.max(ohlcData.value.high, price),
    low: Math.min(ohlcData.value.low, price),
    close: price,
  });
  
  ohlcData.value.close = price;
  ohlcData.value.high = Math.max(ohlcData.value.high, price);
  ohlcData.value.low = Math.min(ohlcData.value.low, price);
};

watch([selectedSymbol, currentPrice], () => {
  updateChart();
});

watch(timeframe, () => {
  // Reload chart data for new timeframe
  if (candlestickSeries) {
    initChart();
  }
});

onMounted(() => {
  initChart();
  
  // Update chart on window resize
  resizeHandler = () => {
    if (chart && chartContainer.value) {
      chart.applyOptions({
        width: chartContainer.value.clientWidth,
        height: chartContainer.value.clientHeight,
      });
    }
  };
  
  window.addEventListener('resize', resizeHandler);
  
  // Subscribe to WebSocket price updates for real-time chart updates
  if (wsStore.isConnected) {
    wsPriceUpdateHandler = (data) => {
      if (data.symbol === selectedSymbol.value && data.price !== undefined) {
        updateChart();
      }
    };
    wsStore.subscribe(selectedSymbol.value, wsPriceUpdateHandler);
  }
  
  // Update chart periodically (fallback if WebSocket not available)
  updateInterval = setInterval(updateChart, 2000);
});

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
  }
  if (updateInterval) {
    clearInterval(updateInterval);
  }
  if (wsPriceUpdateHandler && wsStore.isConnected) {
    wsStore.unsubscribe(selectedSymbol.value, wsPriceUpdateHandler);
  }
  if (chart) {
    chart.remove();
    chart = null;
  }
  candlestickSeries = null;
});
</script>

