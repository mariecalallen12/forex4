<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4 h-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-chart-line mr-2 text-purple-400"></i>
        Market Watch
      </h2>
    </div>

    <!-- Filter Tabs -->
    <MarketWatchFilter v-model="activeFilter" />

    <!-- Market Watch List -->
    <MarketWatchList :filter="activeFilter" @select-instrument="handleSelectInstrument" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useMarketStore } from '../../../stores/market';
import MarketWatchFilter from './MarketWatchFilter.vue';
import MarketWatchList from './MarketWatchList.vue';

const marketStore = useMarketStore();
const activeFilter = ref('all');

const handleSelectInstrument = (instrument) => {
  marketStore.selectInstrument(instrument);
};
</script>

