<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-wallet mr-2 text-purple-400"></i>
        Tài Khoản
      </h3>
    </div>

    <!-- Available Balance -->
    <div class="mb-4">
      <div class="text-sm text-gray-400 mb-1">Số dư khả dụng</div>
      <div class="text-2xl font-bold text-white">${{ formatNumber(accountStore.balance.available) }}</div>
    </div>

    <!-- Used Margin -->
    <div class="mb-4">
      <div class="text-sm text-gray-400 mb-1">Margin sử dụng</div>
      <div class="text-xl font-bold text-purple-400">${{ formatNumber(accountStore.balance.usedMargin) }}</div>
    </div>

    <!-- P&L Today -->
    <div class="mb-4">
      <div class="text-sm text-gray-400 mb-1">P&L hôm nay</div>
      <div
        :class="[
          'text-xl font-bold',
          accountStore.pnlToday >= 0 ? 'text-green-400' : 'text-red-400'
        ]"
      >
        {{ accountStore.pnlToday >= 0 ? '+' : '' }}${{ formatNumber(accountStore.pnlToday) }}
      </div>
    </div>

    <!-- Equity -->
    <div class="mb-4">
      <div class="text-sm text-gray-400 mb-1">Equity</div>
      <div class="text-xl font-bold text-white">${{ formatNumber(accountStore.equity) }}</div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-2 gap-2">
      <button
        @click="showDepositModal = true"
        class="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-medium hover:from-green-600 hover:to-emerald-600 transition-all"
      >
        + Nạp tiền
      </button>
      <button
        @click="showWithdrawModal = true"
        class="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-medium hover:from-blue-600 hover:to-cyan-600 transition-all"
      >
        — Rút tiền
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAccountStore } from '../../../stores/account';

const accountStore = useAccountStore();
const showDepositModal = ref(false);
const showWithdrawModal = ref(false);

const formatNumber = (num) => {
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};
</script>

