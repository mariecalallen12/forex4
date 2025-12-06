<template>
  <div class="flex-1 flex flex-col space-y-4">
    <!-- Social Feed -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Tín hiệu từ cộng đồng</label>
      <div class="space-y-2 max-h-48 overflow-y-auto">
        <div
          v-for="signal in socialSignals"
          :key="signal.id"
          @click="selectSignal(signal)"
          :class="[
            'p-3 rounded-lg border cursor-pointer transition-all',
            selectedSignal?.id === signal.id
              ? 'bg-purple-500/20 border-purple-500'
              : 'bg-slate-700/30 border-slate-600 hover:bg-slate-700/50'
          ]"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <div class="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center text-white text-xs font-bold">
                {{ signal.user.charAt(0) }}
              </div>
              <div>
                <div class="text-white text-sm font-medium">{{ signal.user }}</div>
                <div class="text-xs text-gray-400">{{ formatTime(signal.timestamp) }}</div>
              </div>
            </div>
            <span
              :class="[
                'px-2 py-1 rounded text-xs font-bold',
                signal.side === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              ]"
            >
              {{ signal.side === 'buy' ? 'MUA' : 'BÁN' }}
            </span>
          </div>
          <div class="text-xs text-gray-300 mb-1">{{ signal.symbol }} @ {{ formatPrice(signal.price) }}</div>
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-400">{{ signal.likes }} likes</span>
            <span class="text-purple-400">{{ signal.followers }} followers</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Signal Details -->
    <div v-if="selectedSignal" class="bg-slate-700/30 rounded-lg p-4 space-y-3">
      <h4 class="text-sm font-bold text-white">Chi tiết tín hiệu</h4>
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div>
          <span class="text-gray-400">Cặp:</span>
          <span class="text-white ml-1">{{ selectedSignal.symbol }}</span>
        </div>
        <div>
          <span class="text-gray-400">Giá:</span>
          <span class="text-white ml-1">{{ formatPrice(selectedSignal.price) }}</span>
        </div>
        <div>
          <span class="text-gray-400">Hướng:</span>
          <span :class="['ml-1 font-bold', selectedSignal.side === 'buy' ? 'text-green-400' : 'text-red-400']">
            {{ selectedSignal.side === 'buy' ? 'MUA' : 'BÁN' }}
          </span>
        </div>
        <div>
          <span class="text-gray-400">Người đăng:</span>
          <span class="text-white ml-1">{{ selectedSignal.user }}</span>
        </div>
      </div>

      <!-- Copy Amount -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Số tiền copy</label>
        <input
          v-model.number="copyAmount"
          type="number"
          step="0.01"
          min="10"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="100.00"
        />
      </div>
    </div>

    <!-- Submit Button -->
    <button
      v-if="selectedSignal"
      @click="followSignal"
      class="w-full py-3 rounded-lg font-bold text-lg bg-gradient-to-r from-blue-600 to-cyan-600 text-white hover:from-blue-700 hover:to-cyan-700 transition-all shadow-lg"
    >
      Follow Signal
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTradingStore } from '../../../../stores/trading';

const tradingStore = useTradingStore();
const selectedSignal = ref(null);
const copyAmount = ref(100);

// Mock social signals
const socialSignals = ref([
  {
    id: 'SIG-001',
    user: 'TraderPro',
    symbol: 'EUR/USD',
    side: 'buy',
    price: 1.0845,
    likes: 45,
    followers: 23,
    timestamp: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: 'SIG-002',
    user: 'CryptoMaster',
    symbol: 'BTC/USD',
    side: 'buy',
    price: 43200,
    likes: 128,
    followers: 67,
    timestamp: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'SIG-003',
    user: 'ForexExpert',
    symbol: 'GBP/USD',
    side: 'sell',
    price: 1.2600,
    likes: 32,
    followers: 15,
    timestamp: new Date(Date.now() - 5400000).toISOString(),
  },
]);

const selectSignal = (signal) => {
  selectedSignal.value = signal;
  copyAmount.value = 100;
};

const formatPrice = (price) => {
  if (!price && price !== 0) return '0.00';
  return parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
};

const formatTime = (timestamp) => {
  const now = new Date();
  const time = new Date(timestamp);
  const diff = now - time;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes} phút trước`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} giờ trước`;
  return `${Math.floor(hours / 24)} ngày trước`;
};

const followSignal = async () => {
  const order = {
    order_type: 'social_trading',
    signal_id: selectedSignal.value.id,
    symbol: selectedSignal.value.symbol,
    side: selectedSignal.value.side,
    price: selectedSignal.value.price,
    amount: copyAmount.value,
  };

  try {
    await tradingStore.placeOrder(order);
    alert(`Đã follow tín hiệu từ ${selectedSignal.value.user}`);
  } catch (error) {
    console.error('Error following signal:', error);
  }
};
</script>
