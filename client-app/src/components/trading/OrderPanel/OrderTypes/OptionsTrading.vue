<template>
  <div class="flex-1 flex flex-col space-y-4">
    <!-- Strategy Selection -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Chiến lược Options</label>
      <select
        v-model="strategy"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="call">Call Option</option>
        <option value="put">Put Option</option>
        <option value="bull_call_spread">Bull Call Spread</option>
        <option value="bear_put_spread">Bear Put Spread</option>
        <option value="iron_condor">Iron Condor</option>
        <option value="butterfly">Butterfly</option>
        <option value="straddle">Straddle</option>
        <option value="strangle">Strangle</option>
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

    <!-- Strike Price -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Strike Price</label>
      <input
        v-model.number="orderData.strikePrice"
        type="number"
        step="0.0001"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        placeholder="Nhập strike price"
      />
    </div>

    <!-- Expiry Date -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Ngày hết hạn</label>
      <select
        v-model="orderData.expiry"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="1d">1 Ngày</option>
        <option value="7d">7 Ngày</option>
        <option value="30d">30 Ngày</option>
        <option value="90d">90 Ngày</option>
      </select>
    </div>

    <!-- Quantity -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Số lượng contracts</label>
      <input
        v-model.number="orderData.quantity"
        type="number"
        step="1"
        min="1"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        placeholder="1"
      />
    </div>

    <!-- Premium -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Premium (Giá mua option)</label>
      <input
        v-model.number="orderData.premium"
        type="number"
        step="0.01"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        placeholder="0.00"
      />
    </div>

    <!-- Greeks Display -->
    <div v-if="orderData.strikePrice && orderData.premium" class="bg-slate-700/30 rounded-lg p-4">
      <h4 class="text-sm font-bold text-white mb-2">Greeks</h4>
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div>
          <span class="text-gray-400">Delta:</span>
          <span class="text-white ml-1">{{ greeks.delta.toFixed(4) }}</span>
        </div>
        <div>
          <span class="text-gray-400">Gamma:</span>
          <span class="text-white ml-1">{{ greeks.gamma.toFixed(4) }}</span>
        </div>
        <div>
          <span class="text-gray-400">Theta:</span>
          <span class="text-white ml-1">{{ greeks.theta.toFixed(4) }}</span>
        </div>
        <div>
          <span class="text-gray-400">Vega:</span>
          <span class="text-white ml-1">{{ greeks.vega.toFixed(4) }}</span>
        </div>
      </div>
    </div>

    <!-- Total Cost -->
    <div class="bg-purple-500/20 rounded-lg p-3">
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-400">Tổng chi phí</span>
        <span class="text-lg font-bold text-white">
          ${{ formatNumber(totalCost) }}
        </span>
      </div>
    </div>

    <!-- Submit Button -->
    <button
      @click="placeOptionsOrder"
      class="w-full py-3 rounded-lg font-bold text-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
    >
      Mua Option
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useTradingStore } from '../../../../stores/trading';
import { useMarketStore } from '../../../../stores/market';

const tradingStore = useTradingStore();
const marketStore = useMarketStore();

const strategy = ref('call');
const orderData = ref({
  symbol: 'EUR/USD',
  strikePrice: null,
  expiry: '7d',
  quantity: 1,
  premium: null,
  optionType: 'call',
});

const greeks = computed(() => {
  // Simplified Greeks calculation (in production, use Black-Scholes model)
  const currentPrice = marketStore.getPrice(orderData.value.symbol)?.price || 1.0842;
  const strike = orderData.value.strikePrice || currentPrice;
  const premium = orderData.value.premium || 0;
  const timeToExpiry = parseFloat(orderData.value.expiry) || 7;
  
  const delta = orderData.value.optionType === 'call' 
    ? Math.max(0, (currentPrice - strike) / strike) 
    : Math.max(0, (strike - currentPrice) / strike);
  
  return {
    delta: delta,
    gamma: 0.0001,
    theta: -premium / timeToExpiry,
    vega: premium * 0.1,
  };
});

const totalCost = computed(() => {
  return (orderData.value.premium || 0) * (orderData.value.quantity || 1);
});

const formatNumber = (num) => {
  if (!num && num !== 0) return '0.00';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const placeOptionsOrder = async () => {
  const order = {
    ...orderData.value,
    order_type: 'options',
    strategy: strategy.value,
    greeks: greeks.value,
  };

  try {
    await tradingStore.placeOrder(order);
    // Reset form
    orderData.value = {
      symbol: 'EUR/USD',
      strikePrice: null,
      expiry: '7d',
      quantity: 1,
      premium: null,
      optionType: 'call',
    };
  } catch (error) {
    console.error('Error placing options order:', error);
  }
};

// Update option type based on strategy
watch(strategy, (newStrategy) => {
  if (newStrategy.includes('call')) {
    orderData.value.optionType = 'call';
  } else if (newStrategy.includes('put')) {
    orderData.value.optionType = 'put';
  }
});
</script>
