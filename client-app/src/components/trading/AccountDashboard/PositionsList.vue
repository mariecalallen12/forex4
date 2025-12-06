<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-list mr-2 text-purple-400"></i>
        Vị Thế Mở
      </h3>
    </div>

    <div class="space-y-3">
      <div
        v-for="position in tradingStore.openPositions"
        :key="position.id"
        class="bg-slate-700/30 rounded-lg p-3"
      >
        <div class="flex items-center justify-between mb-2">
          <div>
            <div class="font-bold text-white">{{ position.symbol }}</div>
            <div class="text-xs text-gray-400">
              {{ position.side === 'buy' ? 'BUY' : 'SELL' }} {{ position.quantity }}
            </div>
          </div>
          <div
            :class="[
              'text-lg font-bold',
              position.pnl >= 0 ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ position.pnl >= 0 ? '+' : '' }}${{ formatNumber(position.pnl) }}
          </div>
        </div>
        <div class="text-xs text-gray-400 mb-2">
          Entry: {{ position.entryPrice }}
        </div>
        <div class="flex space-x-2">
          <button
            @click="closePosition(position.id)"
            class="flex-1 px-3 py-1 bg-red-500/20 text-red-400 rounded text-sm hover:bg-red-500/30 transition-colors"
          >
            Đóng
          </button>
          <button
            @click="editPosition(position.id)"
            class="flex-1 px-3 py-1 bg-purple-500/20 text-purple-400 rounded text-sm hover:bg-purple-500/30 transition-colors"
          >
            Sửa
          </button>
        </div>
      </div>

      <div v-if="tradingStore.openPositions.length === 0" class="text-center text-gray-400 py-8">
        Không có vị thế mở
      </div>
    </div>
  </div>
</template>

<script setup>
import { useTradingStore } from '../../../stores/trading';

const tradingStore = useTradingStore();

const formatNumber = (num) => {
  return Math.abs(num).toFixed(2);
};

const closePosition = async (positionId) => {
  await tradingStore.closePosition(positionId);
};

const editPosition = (positionId) => {
  // Handle edit position
  console.log('Edit position:', positionId);
};
</script>

