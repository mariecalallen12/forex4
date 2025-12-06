<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-chart-bar mr-2 text-purple-400"></i>
      Performance Analytics
    </h3>
    
    <div class="space-y-4">
      <!-- P&L Breakdown -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="text-sm text-gray-400 mb-2">P&L Breakdown</div>
        <div class="text-xl font-bold text-green-400">+${{ formatNumber(analytics.totalPnl) }}</div>
      </div>

      <!-- Sharpe Ratio -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="text-sm text-gray-400 mb-2">Sharpe Ratio</div>
        <div class="text-lg font-bold text-white">{{ analytics.sharpeRatio }}</div>
      </div>

      <!-- Drawdown -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="text-sm text-gray-400 mb-2">Max Drawdown</div>
        <div class="text-lg font-bold text-red-400">-{{ analytics.maxDrawdown }}%</div>
      </div>

      <!-- Trade History -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="text-sm text-gray-400 mb-2">Total Trades</div>
        <div class="text-lg font-bold text-white">{{ analytics.totalTrades }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const analytics = ref({
  totalPnl: 2450,
  sharpeRatio: 1.85,
  maxDrawdown: 5.2,
  totalTrades: 127,
});

const formatNumber = (num) => {
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};
</script>

