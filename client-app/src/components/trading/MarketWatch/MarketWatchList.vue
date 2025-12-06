<template>
  <div class="space-y-2 max-h-[calc(100vh-300px)] sm:max-h-[calc(100vh-250px)] overflow-y-auto">
    <div
      v-for="instrument in filteredInstruments"
      :key="instrument.symbol"
      @click="$emit('select-instrument', instrument)"
      :class="[
        'p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-700/50',
        isSelected(instrument) ? 'bg-purple-500/20 border border-purple-500/50' : 'bg-slate-700/30'
      ]"
    >
      <div class="flex items-center justify-between mb-1">
        <span class="font-bold text-white text-sm">{{ instrument.symbol }}</span>
        <span
          :class="[
            'text-sm font-bold',
            getPriceChange(instrument) >= 0 ? 'text-green-400' : 'text-red-400'
          ]"
        >
          {{ formatPrice(instrument.price) }}
        </span>
      </div>
      <div class="flex items-center justify-between text-xs">
        <span class="text-gray-400">{{ getInstrumentName(instrument.symbol) }}</span>
        <span
          :class="[
            'font-medium',
            getPriceChange(instrument) >= 0 ? 'text-green-400' : 'text-red-400'
          ]"
        >
          {{ getPriceChange(instrument) >= 0 ? '+' : '' }}{{ formatPercent(getPriceChange(instrument)) }}%
        </span>
      </div>
      <!-- Mini Sparkline Chart -->
      <div class="mt-2 h-8">
        <svg viewBox="0 0 100 30" class="w-full h-full">
          <path
            :d="generateSparkline(instrument)"
            :stroke="getPriceChange(instrument) >= 0 ? '#10B981' : '#EF4444'"
            fill="none"
            stroke-width="2"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useMarketStore } from '../../../stores/market';

const props = defineProps({
  filter: {
    type: String,
    default: 'all',
  },
});

defineEmits(['select-instrument']);

const marketStore = useMarketStore();

const filteredInstruments = computed(() => {
  return marketStore.filterInstruments(props.filter);
});

const isSelected = (instrument) => {
  return marketStore.selectedInstrument?.symbol === instrument.symbol;
};

const getPriceChange = (instrument) => {
  const priceData = marketStore.getPrice(instrument.symbol);
  return priceData.changePercent || instrument.changePercent || 0;
};

const formatPrice = (price) => {
  if (price > 1000) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  return price.toFixed(4);
};

const formatPercent = (percent) => {
  return Math.abs(percent).toFixed(2);
};

const getInstrumentName = (symbol) => {
  const names = {
    'EUR/USD': 'Euro vs US Dollar',
    'GBP/USD': 'British Pound vs USD',
    'USD/JPY': 'US Dollar vs Yen',
    'BTC/USD': 'Bitcoin',
    'ETH/USD': 'Ethereum',
    'GOLD': 'Gold Spot',
    'OIL': 'Crude Oil',
  };
  return names[symbol] || symbol;
};

const generateSparkline = (instrument) => {
  // Generate simple sparkline path
  const points = 8;
  const basePrice = instrument.price;
  const variation = basePrice * 0.002; // 0.2% variation
  
  let path = 'M 0,15';
  for (let i = 1; i <= points; i++) {
    const x = (i / points) * 100;
    const randomChange = (Math.random() - 0.5) * variation;
    const y = 15 - (randomChange / variation) * 10;
    path += ` L ${x},${y}`;
  }
  return path;
};
</script>

