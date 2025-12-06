<template>
  <div class="flex-1 flex flex-col space-y-4">
    <!-- Derivative Type -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Loại Derivatives</label>
      <select
        v-model="derivativeType"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="cfd">CFD (Contract for Difference)</option>
        <option value="swap">Swap</option>
        <option value="forward">Forward Contract</option>
        <option value="swaption">Swaption</option>
      </select>
    </div>

    <!-- Symbol Selection -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Cặp giao dịch</label>
      <select
        v-model="orderData.symbol"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="EUR/USD">EUR/USD</option>
        <option value="GBP/USD">GBP/USD</option>
        <option value="BTC/USD">BTC/USD</option>
        <option value="ETH/USD">ETH/USD</option>
      </select>
    </div>

    <!-- Contract Size -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Kích thước contract</label>
      <input
        v-model.number="orderData.contractSize"
        type="number"
        step="1"
        min="1"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        placeholder="1"
      />
    </div>

    <!-- Leverage -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Đòn bẩy</label>
      <select
        v-model="orderData.leverage"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="1">1x</option>
        <option value="5">5x</option>
        <option value="10">10x</option>
        <option value="20">20x</option>
        <option value="50">50x</option>
        <option value="100">100x</option>
        <option value="200">200x</option>
      </select>
    </div>

    <!-- Entry Price -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Giá vào</label>
      <input
        v-model.number="orderData.price"
        type="number"
        step="0.0001"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        placeholder="Nhập giá"
      />
    </div>

    <!-- Risk Analytics -->
    <div class="bg-slate-700/30 rounded-lg p-4">
      <h4 class="text-sm font-bold text-white mb-2">Phân tích rủi ro</h4>
      <div class="space-y-2 text-xs">
        <div class="flex items-center justify-between">
          <span class="text-gray-400">VaR (1 day):</span>
          <span class="text-yellow-400 font-bold">${{ formatNumber(riskMetrics.var) }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Expected Return:</span>
          <span class="text-green-400 font-bold">{{ riskMetrics.expectedReturn.toFixed(2) }}%</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Max Drawdown:</span>
          <span class="text-red-400 font-bold">{{ riskMetrics.maxDrawdown.toFixed(2) }}%</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Sharpe Ratio:</span>
          <span class="text-white font-bold">{{ riskMetrics.sharpeRatio.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Stop Loss & Take Profit -->
    <div class="grid grid-cols-2 gap-2">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Stop Loss</label>
        <input
          v-model.number="orderData.stopLoss"
          type="number"
          step="0.01"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="0.00"
        />
      </div>
      <div>
        <label class="block text-sm text-gray-400 mb-2">Take Profit</label>
        <input
          v-model.number="orderData.takeProfit"
          type="number"
          step="0.01"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="0.00"
        />
      </div>
    </div>

    <!-- Submit Buttons -->
    <div class="grid grid-cols-2 gap-2">
      <button
        @click="placeDerivativesOrder('buy')"
        class="py-3 rounded-lg font-bold bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 transition-all"
      >
        MUA
      </button>
      <button
        @click="placeDerivativesOrder('sell')"
        class="py-3 rounded-lg font-bold bg-gradient-to-r from-red-500 to-pink-500 text-white hover:from-red-600 hover:to-pink-600 transition-all"
      >
        BÁN
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTradingStore } from '../../../../stores/trading';
import { useMarketStore } from '../../../../stores/market';

const tradingStore = useTradingStore();
const marketStore = useMarketStore();

const derivativeType = ref('cfd');
const orderData = ref({
  symbol: 'EUR/USD',
  contractSize: 1,
  leverage: 10,
  price: null,
  stopLoss: null,
  takeProfit: null,
});

const riskMetrics = computed(() => {
  // Simplified risk metrics calculation
  const leverage = parseFloat(orderData.value.leverage || 1);
  const contractValue = (orderData.value.price || 1.0842) * (orderData.value.contractSize || 1);
  
  return {
    var: contractValue * leverage * 0.02, // 2% VaR
    expectedReturn: leverage * 0.5,
    maxDrawdown: leverage * 0.1,
    sharpeRatio: 1.2 + (leverage / 100),
  };
});

const formatNumber = (num) => {
  if (!num && num !== 0) return '0.00';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const placeDerivativesOrder = async (side) => {
  const order = {
    ...orderData.value,
    side: side,
    order_type: 'derivatives',
    derivative_type: derivativeType.value,
    risk_metrics: riskMetrics.value,
  };

  try {
    await tradingStore.placeOrder(order);
    // Reset form
    orderData.value = {
      symbol: 'EUR/USD',
      contractSize: 1,
      leverage: 10,
      price: null,
      stopLoss: null,
      takeProfit: null,
    };
  } catch (error) {
    console.error('Error placing derivatives order:', error);
  }
};
</script>
