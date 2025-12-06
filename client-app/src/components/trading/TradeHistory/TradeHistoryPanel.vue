<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-chart-line mr-2 text-purple-400"></i>
        Lịch Sử Giao Dịch
      </h3>
      <div class="flex items-center space-x-2">
        <button
          @click="exportToCSV"
          class="text-sm text-purple-400 hover:text-purple-300 transition-colors"
          title="Xuất CSV"
        >
          <i class="fas fa-download"></i>
        </button>
        <button
          @click="refreshTrades"
          class="text-sm text-purple-400 hover:text-purple-300 transition-colors"
          :disabled="isLoading"
        >
          <i class="fas fa-sync-alt" :class="{ 'animate-spin': isLoading }"></i>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-3 gap-2 mb-4">
      <div class="bg-slate-700/30 rounded-lg p-3">
        <div class="text-xs text-gray-400 mb-1">Tổng P&L</div>
        <div :class="['text-lg font-bold', totalPnl >= 0 ? 'text-green-400' : 'text-red-400']">
          {{ totalPnl >= 0 ? '+' : '' }}${{ formatNumber(totalPnl) }}
        </div>
      </div>
      <div class="bg-slate-700/30 rounded-lg p-3">
        <div class="text-xs text-gray-400 mb-1">Tổng giao dịch</div>
        <div class="text-lg font-bold text-white">{{ tradeHistory.length }}</div>
      </div>
      <div class="bg-slate-700/30 rounded-lg p-3">
        <div class="text-xs text-gray-400 mb-1">Tỷ lệ thắng</div>
        <div class="text-lg font-bold text-white">{{ winRate }}%</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-4 space-y-2">
      <div class="grid grid-cols-2 gap-2">
        <select
          v-model="filters.symbol"
          class="px-3 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Tất cả cặp</option>
          <option value="EUR/USD">EUR/USD</option>
          <option value="GBP/USD">GBP/USD</option>
          <option value="BTC/USD">BTC/USD</option>
          <option value="ETH/USD">ETH/USD</option>
        </select>
        <select
          v-model="filters.period"
          class="px-3 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">Tất cả thời gian</option>
          <option value="today">Hôm nay</option>
          <option value="week">Tuần này</option>
          <option value="month">Tháng này</option>
        </select>
      </div>
    </div>

    <!-- Trade History List -->
    <div class="space-y-2 max-h-96 overflow-y-auto">
      <div
        v-for="trade in filteredTrades"
        :key="trade.id"
        class="bg-slate-700/30 rounded-lg p-3 hover:bg-slate-700/50 transition-colors"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <span
              :class="[
                'px-2 py-1 rounded text-xs font-bold',
                trade.side === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              ]"
            >
              {{ trade.side === 'buy' ? 'MUA' : 'BÁN' }}
            </span>
            <span class="text-white font-medium">{{ trade.symbol }}</span>
          </div>
          <div
            :class="[
              'text-sm font-bold',
              trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ trade.pnl >= 0 ? '+' : '' }}${{ formatNumber(trade.pnl) }}
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs text-gray-400">
          <div>
            <span>Khối lượng:</span>
            <span class="text-white ml-1">{{ formatNumber(trade.quantity) }}</span>
          </div>
          <div>
            <span>Giá vào:</span>
            <span class="text-white ml-1">{{ formatPrice(trade.entry_price) }}</span>
          </div>
          <div>
            <span>Giá ra:</span>
            <span class="text-white ml-1">{{ formatPrice(trade.exit_price) }}</span>
          </div>
          <div>
            <span>Thời gian:</span>
            <span class="text-white ml-1">{{ formatDate(trade.closed_at || trade.timestamp) }}</span>
          </div>
        </div>
        <div v-if="trade.commission" class="mt-2 text-xs text-gray-400">
          Phí: ${{ formatNumber(trade.commission) }}
        </div>
      </div>

      <div v-if="filteredTrades.length === 0" class="text-center text-gray-400 py-8">
        <i class="fas fa-chart-line text-4xl mb-2 opacity-50"></i>
        <p>Không có giao dịch nào</p>
      </div>
    </div>

    <!-- P&L Chart (Simple visualization) -->
    <div v-if="filteredTrades.length > 0" class="mt-4 pt-4 border-t border-slate-700">
      <h4 class="text-sm font-bold text-white mb-2">Biểu đồ P&L</h4>
      <div class="h-32 bg-slate-900/50 rounded-lg p-2 flex items-end justify-between space-x-1">
        <div
          v-for="(trade, index) in filteredTrades.slice(0, 20)"
          :key="index"
          :class="[
            'flex-1 rounded-t transition-all hover:opacity-80',
            trade.pnl >= 0 ? 'bg-green-500' : 'bg-red-500'
          ]"
          :style="{ height: `${Math.abs(trade.pnl) / maxPnl * 100}%` }"
          :title="`${trade.symbol}: $${formatNumber(trade.pnl)}`"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTradingStore } from '../../../stores/trading';

const tradingStore = useTradingStore();
const isLoading = ref(false);
const filters = ref({
  symbol: '',
  period: 'all',
});

// Mock trade history data
const tradeHistory = ref([
  {
    id: 'TRADE-001',
    symbol: 'EUR/USD',
    side: 'buy',
    quantity: 0.10,
    entry_price: 1.0832,
    exit_price: 1.0845,
    pnl: 13.00,
    commission: 0.50,
    closed_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'TRADE-002',
    symbol: 'BTC/USD',
    side: 'buy',
    quantity: 0.05,
    entry_price: 42100,
    exit_price: 43250,
    pnl: 575.00,
    commission: 2.15,
    closed_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: 'TRADE-003',
    symbol: 'EUR/USD',
    side: 'sell',
    quantity: 0.15,
    entry_price: 1.0850,
    exit_price: 1.0835,
    pnl: 22.50,
    commission: 0.75,
    closed_at: new Date(Date.now() - 10800000).toISOString(),
  },
  {
    id: 'TRADE-004',
    symbol: 'GBP/USD',
    side: 'buy',
    quantity: 0.20,
    entry_price: 1.2600,
    exit_price: 1.2580,
    pnl: -40.00,
    commission: 1.00,
    closed_at: new Date(Date.now() - 14400000).toISOString(),
  },
]);

const filteredTrades = computed(() => {
  let trades = tradeHistory.value;
  
  if (filters.value.symbol) {
    trades = trades.filter(trade => trade.symbol === filters.value.symbol);
  }
  
  if (filters.value.period !== 'all') {
    const now = new Date();
    const periodMap = {
      today: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
      week: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
      month: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000),
    };
    const cutoff = periodMap[filters.value.period];
    trades = trades.filter(trade => new Date(trade.closed_at || trade.timestamp) >= cutoff);
  }
  
  return trades.sort((a, b) => {
    const dateA = new Date(a.closed_at || a.timestamp || 0);
    const dateB = new Date(b.closed_at || b.timestamp || 0);
    return dateB - dateA;
  });
});

const totalPnl = computed(() => {
  return filteredTrades.value.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
});

const winRate = computed(() => {
  if (filteredTrades.value.length === 0) return 0;
  const wins = filteredTrades.value.filter(trade => trade.pnl > 0).length;
  return Math.round((wins / filteredTrades.value.length) * 100);
});

const maxPnl = computed(() => {
  if (filteredTrades.value.length === 0) return 1;
  return Math.max(...filteredTrades.value.map(t => Math.abs(t.pnl || 0)), 1);
});

const formatNumber = (num) => {
  if (!num && num !== 0) return '0';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
};

const formatPrice = (price) => {
  if (!price && price !== 0) return '-';
  return parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
};

const formatDate = (date) => {
  if (!date) return '-';
  const d = new Date(date);
  return d.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const refreshTrades = async () => {
  isLoading.value = true;
  try {
    // In the future, fetch from API
    // await tradingStore.fetchTradeHistory(filters.value);
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
  } catch (error) {
    console.error('Error fetching trade history:', error);
  } finally {
    isLoading.value = false;
  }
};

const exportToCSV = () => {
  const headers = ['ID', 'Symbol', 'Side', 'Quantity', 'Entry Price', 'Exit Price', 'P&L', 'Commission', 'Date'];
  const rows = filteredTrades.value.map(trade => [
    trade.id,
    trade.symbol,
    trade.side,
    trade.quantity,
    trade.entry_price,
    trade.exit_price,
    trade.pnl,
    trade.commission || 0,
    new Date(trade.closed_at || trade.timestamp).toLocaleString('vi-VN'),
  ]);
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `trade_history_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

onMounted(() => {
  // Load trade history on mount
  refreshTrades();
});
</script>

