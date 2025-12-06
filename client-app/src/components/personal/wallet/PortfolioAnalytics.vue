<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-chart-pie mr-2 text-purple-400"></i>
      Phân Tích Portfolio
    </h3>

    <!-- Total Portfolio Value -->
    <div class="mb-6 p-4 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 border border-purple-500/30 rounded-lg">
      <div class="text-purple-300 text-sm mb-1">Tổng giá trị portfolio</div>
      <div class="font-orbitron text-3xl font-bold text-white">{{ formatVND(totalValue) }}</div>
    </div>

    <!-- Top Assets -->
    <div class="mb-6">
      <div class="text-white font-medium mb-4">Top 5 tài sản lớn nhất</div>
      <div class="space-y-3">
        <div
          v-for="(asset, index) in topAssets"
          :key="asset.currency"
          class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
        >
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <span class="text-purple-300 font-bold">{{ index + 1 }}</span>
            </div>
            <div>
              <div class="text-white font-medium">{{ asset.currency }}</div>
              <div class="text-purple-300 text-xs">{{ asset.percentage }}%</div>
            </div>
          </div>
          <div class="text-white font-medium">{{ formatAmount(asset.value) }}</div>
        </div>
      </div>
    </div>

    <!-- Allocation Chart Placeholder -->
    <div class="p-4 bg-slate-800/50 rounded-lg">
      <div class="text-purple-300 text-sm mb-2">Phân bổ theo asset</div>
      <div class="flex items-end space-x-2 h-32">
        <div
          v-for="asset in topAssets"
          :key="asset.currency"
          class="flex-1 bg-gradient-to-t from-purple-500/50 to-indigo-500/50 rounded-t"
          :style="{ height: `${asset.percentage}%` }"
          :title="`${asset.currency}: ${asset.percentage}%`"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAccountStore } from '../../../stores/account';
import { formatCurrency, formatNumber } from '../../../services/utils/formatters';

const accountStore = useAccountStore();
const exchangeRateUSDTtoVND = 24850;

const totalValue = computed(() => {
  let total = 0;
  
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      if (currency === 'USDT') {
        total += (data.value || 0) * exchangeRateUSDTtoVND;
      } else if (currency === 'BTC') {
        total += (data.value || 0) * exchangeRateUSDTtoVND * 43000;
      } else if (currency === 'ETH') {
        total += (data.value || 0) * exchangeRateUSDTtoVND * 2650;
      }
    });
  }
  
  if (accountStore.currencies?.fiat) {
    if (accountStore.currencies.fiat.VND) {
      total += accountStore.currencies.fiat.VND.value || 0;
    }
    if (accountStore.currencies.fiat.USD) {
      total += (accountStore.currencies.fiat.USD.value || 0) * exchangeRateUSDTtoVND;
    }
  }
  
  return total;
});

const topAssets = computed(() => {
  const assets = [];
  
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      let value = 0;
      if (currency === 'USDT') {
        value = (data.value || 0) * exchangeRateUSDTtoVND;
      } else if (currency === 'BTC') {
        value = (data.value || 0) * exchangeRateUSDTtoVND * 43000;
      } else if (currency === 'ETH') {
        value = (data.value || 0) * exchangeRateUSDTtoVND * 2650;
      }
      assets.push({ currency, value });
    });
  }
  
  if (accountStore.currencies?.fiat) {
    Object.entries(accountStore.currencies.fiat).forEach(([currency, data]) => {
      let value = 0;
      if (currency === 'VND') {
        value = data.value || 0;
      } else if (currency === 'USD') {
        value = (data.value || 0) * exchangeRateUSDTtoVND;
      }
      if (value > 0) {
        assets.push({ currency, value });
      }
    });
  }
  
  assets.sort((a, b) => b.value - a.value);
  const top5 = assets.slice(0, 5);
  const total = top5.reduce((sum, a) => sum + a.value, 0);
  
  return top5.map(asset => ({
    ...asset,
    percentage: total > 0 ? Math.round((asset.value / total) * 100) : 0,
  }));
});

const formatVND = (amount) => {
  return `${formatNumber(amount)} ₫`;
};

const formatAmount = (amount) => {
  return formatCurrency(amount / exchangeRateUSDTtoVND, 'USD');
};
</script>

