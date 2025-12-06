<template>
  <div class="flex-1 flex flex-col space-y-4">
    <!-- Trader Search -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Tìm kiếm Trader</label>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Tên trader hoặc ID..."
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      />
    </div>

    <!-- Trader List -->
    <div class="space-y-2 max-h-64 overflow-y-auto">
      <div
        v-for="trader in filteredTraders"
        :key="trader.id"
        @click="selectTrader(trader)"
        :class="[
          'p-3 rounded-lg border transition-all cursor-pointer',
          selectedTrader?.id === trader.id
            ? 'bg-purple-500/20 border-purple-500'
            : 'bg-slate-700/30 border-slate-600 hover:bg-slate-700/50'
        ]"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 flex items-center justify-center text-white font-bold">
              {{ trader.name.charAt(0) }}
            </div>
            <div>
              <div class="text-white font-medium">{{ trader.name }}</div>
              <div class="text-xs text-gray-400">ID: {{ trader.id }}</div>
            </div>
          </div>
          <div
            :class="[
              'text-sm font-bold',
              trader.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'
            ]"
          >
            {{ trader.totalReturn >= 0 ? '+' : '' }}{{ trader.totalReturn.toFixed(2) }}%
          </div>
        </div>
        <div class="grid grid-cols-3 gap-2 text-xs">
          <div>
            <span class="text-gray-400">Win Rate:</span>
            <span class="text-white ml-1">{{ trader.winRate }}%</span>
          </div>
          <div>
            <span class="text-gray-400">Trades:</span>
            <span class="text-white ml-1">{{ trader.totalTrades }}</span>
          </div>
          <div>
            <span class="text-gray-400">Followers:</span>
            <span class="text-white ml-1">{{ trader.followers }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Settings -->
    <div v-if="selectedTrader" class="bg-slate-700/30 rounded-lg p-4 space-y-4">
      <h4 class="text-sm font-bold text-white">Cài đặt Copy Trading</h4>
      
      <!-- Copy Amount -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Số tiền copy mỗi lệnh</label>
        <input
          v-model.number="copySettings.amount"
          type="number"
          step="0.01"
          min="10"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="100.00"
        />
      </div>

      <!-- Multiplier -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Hệ số nhân</label>
        <input
          v-model.number="copySettings.multiplier"
          type="number"
          step="0.1"
          min="0.1"
          max="10"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="1.0"
        />
        <div class="text-xs text-gray-500 mt-1">Nhân khối lượng lệnh của trader (0.1x - 10x)</div>
      </div>

      <!-- Max Loss -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Giới hạn lỗ tối đa (%)</label>
        <input
          v-model.number="copySettings.maxLoss"
          type="number"
          step="1"
          min="0"
          max="100"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="20"
        />
      </div>

      <!-- Auto Copy Toggle -->
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-400">Tự động copy lệnh mới</span>
        <label class="relative inline-flex items-center cursor-pointer">
          <input
            v-model="copySettings.autoCopy"
            type="checkbox"
            class="sr-only peer"
          />
          <div class="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
        </label>
      </div>
    </div>

    <!-- Submit Button -->
    <button
      v-if="selectedTrader"
      @click="startCopyTrading"
      class="w-full py-3 rounded-lg font-bold text-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
    >
      Bắt đầu Copy Trading
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTradingStore } from '../../../../stores/trading';

const tradingStore = useTradingStore();
const searchQuery = ref('');
const selectedTrader = ref(null);
const copySettings = ref({
  amount: 100,
  multiplier: 1.0,
  maxLoss: 20,
  autoCopy: true,
});

// Mock traders data
const traders = ref([
  {
    id: 'TRADER-001',
    name: 'Trader Pro',
    totalReturn: 45.2,
    winRate: 68,
    totalTrades: 234,
    followers: 1250,
  },
  {
    id: 'TRADER-002',
    name: 'Crypto Master',
    totalReturn: 32.5,
    winRate: 72,
    totalTrades: 189,
    followers: 890,
  },
  {
    id: 'TRADER-003',
    name: 'Forex Expert',
    totalReturn: 28.7,
    winRate: 65,
    totalTrades: 312,
    followers: 2100,
  },
  {
    id: 'TRADER-004',
    name: 'Day Trader',
    totalReturn: 15.3,
    winRate: 58,
    totalTrades: 456,
    followers: 567,
  },
]);

const filteredTraders = computed(() => {
  if (!searchQuery.value) return traders.value;
  const query = searchQuery.value.toLowerCase();
  return traders.value.filter(trader =>
    trader.name.toLowerCase().includes(query) ||
    trader.id.toLowerCase().includes(query)
  );
});

const selectTrader = (trader) => {
  selectedTrader.value = trader;
};

const startCopyTrading = async () => {
  const order = {
    order_type: 'copy_trading',
    trader_id: selectedTrader.value.id,
    trader_name: selectedTrader.value.name,
    ...copySettings.value,
  };

  try {
    await tradingStore.placeOrder(order);
    // Show success message
    alert(`Đã bắt đầu copy trading với ${selectedTrader.value.name}`);
  } catch (error) {
    console.error('Error starting copy trading:', error);
  }
};
</script>
