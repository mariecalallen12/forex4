<script setup>
import Card from '../ui/Card.vue';

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      totalTrades: 0,
      pendingTrades: 0,
      approvedToday: 0,
      totalVolume: 0,
    }),
  },
});
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Total Trades -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Tổng số giao dịch</p>
          <p class="text-3xl font-bold text-white">{{ stats.totalTrades.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-exchange-alt text-blue-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <!-- Pending Trades -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Giao dịch chờ phê duyệt</p>
          <p class="text-3xl font-bold text-white">{{ stats.pendingTrades.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-clock text-yellow-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <!-- Approved Today -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Đã phê duyệt hôm nay</p>
          <p class="text-3xl font-bold text-white">{{ stats.approvedToday.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-check-circle text-green-400 text-xl"></i>
        </div>
      </div>
    </Card>

    <!-- Total Volume -->
    <Card class="relative overflow-hidden">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white/60 text-sm mb-1">Tổng giá trị</p>
          <p class="text-3xl font-bold text-white">${{ stats.totalVolume.toLocaleString() }}</p>
        </div>
        <div class="w-12 h-12 bg-purple-primary/20 rounded-lg flex items-center justify-center">
          <i class="fas fa-chart-line text-purple-primary text-xl"></i>
        </div>
      </div>
    </Card>
  </div>
</template>

