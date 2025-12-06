<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-book mr-2 text-purple-400"></i>
        Order Book
      </h3>
      <div class="flex items-center space-x-2">
        <select
          v-model="selectedSymbol"
          class="px-2 py-1 bg-slate-700/50 border border-purple-500/30 rounded text-white text-xs focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="EUR/USD">EUR/USD</option>
          <option value="GBP/USD">GBP/USD</option>
          <option value="BTC/USD">BTC/USD</option>
          <option value="ETH/USD">ETH/USD</option>
        </select>
        <button
          @click="refreshOrderBook"
          class="text-sm text-purple-400 hover:text-purple-300 transition-colors"
          :disabled="isLoading"
        >
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': isLoading }"></i>
        </button>
      </div>
    </div>

    <!-- Spread Display -->
    <div class="mb-4 p-3 bg-slate-700/30 rounded-lg">
      <div class="flex items-center justify-between">
        <div class="text-xs text-gray-400">Spread</div>
        <div class="text-sm font-bold text-purple-400">
          {{ formatPrice(spread) }} ({{ spreadPercent.toFixed(2) }}%)
        </div>
      </div>
      <div class="flex items-center justify-between mt-2">
        <div>
          <div class="text-xs text-gray-400">Bid</div>
          <div class="text-sm font-bold text-red-400">{{ formatPrice(bestBid) }}</div>
        </div>
        <div class="text-gray-500">|</div>
        <div>
          <div class="text-xs text-gray-400">Ask</div>
          <div class="text-sm font-bold text-green-400">{{ formatPrice(bestAsk) }}</div>
        </div>
      </div>
    </div>

    <!-- Order Book Table -->
    <div class="space-y-2">
      <!-- Asks (Sell Orders) -->
      <div>
        <div class="text-xs text-gray-400 mb-2 flex items-center">
          <i class="fas fa-arrow-up text-red-400 mr-1"></i>
          ASK (Bán)
        </div>
        <div class="space-y-1 max-h-48 overflow-y-auto">
          <div
            v-for="(ask, index) in asks"
            :key="`ask-${index}`"
            class="flex items-center justify-between p-2 bg-red-500/10 rounded hover:bg-red-500/20 transition-colors cursor-pointer"
            :style="{ background: `linear-gradient(to left, rgba(239, 68, 68, ${ask.volume / maxVolume}), transparent)` }"
          >
            <div class="flex-1 text-left">
              <div class="text-sm font-medium text-red-400">{{ formatPrice(ask.price) }}</div>
            </div>
            <div class="flex-1 text-center">
              <div class="text-xs text-gray-300">{{ formatNumber(ask.volume) }}</div>
            </div>
            <div class="flex-1 text-right">
              <div class="text-xs text-gray-400">{{ formatPrice(ask.total) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Price -->
      <div class="py-2 border-y border-purple-500/30">
        <div class="text-center">
          <div class="text-xs text-gray-400 mb-1">Giá hiện tại</div>
          <div class="text-lg font-bold text-white">{{ formatPrice(currentPrice) }}</div>
        </div>
      </div>

      <!-- Bids (Buy Orders) -->
      <div>
        <div class="text-xs text-gray-400 mb-2 flex items-center">
          <i class="fas fa-arrow-down text-green-400 mr-1"></i>
          BID (Mua)
        </div>
        <div class="space-y-1 max-h-48 overflow-y-auto">
          <div
            v-for="(bid, index) in bids"
            :key="`bid-${index}`"
            class="flex items-center justify-between p-2 bg-green-500/10 rounded hover:bg-green-500/20 transition-colors cursor-pointer"
            :style="{ background: `linear-gradient(to left, rgba(16, 185, 129, ${bid.volume / maxVolume}), transparent)` }"
          >
            <div class="flex-1 text-left">
              <div class="text-sm font-medium text-green-400">{{ formatPrice(bid.price) }}</div>
            </div>
            <div class="flex-1 text-center">
              <div class="text-xs text-gray-300">{{ formatNumber(bid.volume) }}</div>
            </div>
            <div class="flex-1 text-right">
              <div class="text-xs text-gray-400">{{ formatPrice(bid.total) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Depth Chart Visualization -->
    <div class="mt-4 pt-4 border-t border-slate-700">
      <h4 class="text-xs font-bold text-white mb-2">Market Depth</h4>
      <div class="relative h-32 bg-slate-900/50 rounded-lg overflow-hidden">
        <!-- Ask side (top) -->
        <div class="absolute top-0 left-0 right-0 h-1/2">
          <div
            v-for="(ask, index) in asks.slice(0, 10)"
            :key="`depth-ask-${index}`"
            class="absolute bg-red-500/50"
            :style="{
              right: '0',
              top: `${(index / 10) * 100}%`,
              width: `${(ask.total / maxTotal) * 100}%`,
              height: `${100 / 10}%`,
            }"
          ></div>
        </div>
        <!-- Bid side (bottom) -->
        <div class="absolute bottom-0 left-0 right-0 h-1/2">
          <div
            v-for="(bid, index) in bids.slice(0, 10)"
            :key="`depth-bid-${index}`"
            class="absolute bg-green-500/50"
            :style="{
              left: '0',
              bottom: `${(index / 10) * 100}%`,
              width: `${(bid.total / maxTotal) * 100}%`,
              height: `${100 / 10}%`,
            }"
          ></div>
        </div>
        <!-- Center line -->
        <div class="absolute top-1/2 left-0 right-0 h-px bg-purple-500/50"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useMarketStore } from '../../../stores/market';

const marketStore = useMarketStore();
const selectedSymbol = ref('EUR/USD');
const isLoading = ref(false);

// Mock order book data
const orderBook = ref({
  bids: [],
  asks: [],
});

// Generate mock order book data
const generateMockOrderBook = (basePrice) => {
  const bids = [];
  const asks = [];
  let bidTotal = 0;
  let askTotal = 0;

  // Generate bids (buy orders) - prices below current
  for (let i = 0; i < 10; i++) {
    const price = basePrice - (i + 1) * (basePrice * 0.0001);
    const volume = Math.random() * 0.5 + 0.1;
    bidTotal += volume;
    bids.push({
      price: price,
      volume: volume,
      total: bidTotal,
    });
  }

  // Generate asks (sell orders) - prices above current
  for (let i = 0; i < 10; i++) {
    const price = basePrice + (i + 1) * (basePrice * 0.0001);
    const volume = Math.random() * 0.5 + 0.1;
    askTotal += volume;
    asks.push({
      price: price,
      volume: volume,
      total: askTotal,
    });
  }

  // Sort bids descending, asks ascending
  bids.sort((a, b) => b.price - a.price);
  asks.sort((a, b) => a.price - b.price);

  return { bids, asks };
};

const currentPrice = computed(() => {
  const priceData = marketStore.getPrice(selectedSymbol.value);
  return priceData.price || (selectedSymbol.value.includes('EUR') ? 1.0842 : selectedSymbol.value.includes('BTC') ? 43250 : 1.26);
});

const bids = computed(() => orderBook.value.bids);
const asks = computed(() => orderBook.value.asks);

const bestBid = computed(() => {
  return bids.value.length > 0 ? bids.value[0].price : currentPrice.value;
});

const bestAsk = computed(() => {
  return asks.value.length > 0 ? asks.value[0].price : currentPrice.value;
});

const spread = computed(() => {
  return bestAsk.value - bestBid.value;
});

const spreadPercent = computed(() => {
  return (spread.value / currentPrice.value) * 100;
});

const maxVolume = computed(() => {
  const allVolumes = [...bids.value, ...asks.value].map(o => o.volume);
  return Math.max(...allVolumes, 1);
});

const maxTotal = computed(() => {
  const bidMax = bids.value.length > 0 ? Math.max(...bids.value.map(b => b.total)) : 0;
  const askMax = asks.value.length > 0 ? Math.max(...asks.value.map(a => a.total)) : 0;
  return Math.max(bidMax, askMax, 1);
});

const formatPrice = (price) => {
  if (!price && price !== 0) return '-';
  const decimals = selectedSymbol.value.includes('EUR') || selectedSymbol.value.includes('GBP') ? 4 : 2;
  return parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
};

const formatNumber = (num) => {
  if (!num && num !== 0) return '0';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
};

const refreshOrderBook = async () => {
  isLoading.value = true;
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 300));
    const price = currentPrice.value;
    orderBook.value = generateMockOrderBook(price);
  } catch (error) {
    console.error('Error fetching order book:', error);
  } finally {
    isLoading.value = false;
  }
};

watch([selectedSymbol, currentPrice], () => {
  refreshOrderBook();
}, { immediate: true });

onMounted(() => {
  refreshOrderBook();
  
  // Simulate real-time updates
  const interval = setInterval(() => {
    const price = currentPrice.value;
    orderBook.value = generateMockOrderBook(price);
  }, 2000);
  
  // Cleanup on unmount
  return () => clearInterval(interval);
});
</script>

