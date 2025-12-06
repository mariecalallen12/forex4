<template>
  <div class="flex-1 flex flex-col">
    <!-- Buy/Sell Buttons -->
    <div class="grid grid-cols-2 gap-2 mb-4">
      <button
        @click="orderSide = 'buy'"
        :class="[
          'py-3 rounded-lg font-bold text-lg transition-all',
          orderSide === 'buy'
            ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
            : 'bg-slate-700/50 text-gray-400 hover:bg-slate-700'
        ]"
      >
        ↑ MUA
      </button>
      <button
        @click="orderSide = 'sell'"
        :class="[
          'py-3 rounded-lg font-bold text-lg transition-all',
          orderSide === 'sell'
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
            : 'bg-slate-700/50 text-gray-400 hover:bg-slate-700'
        ]"
      >
        ↓ BÁN
      </button>
    </div>

    <!-- Order Form -->
    <div class="space-y-4 flex-1">
      <!-- Volume -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Khối lượng</label>
        <input
          v-model="orderData.quantity"
          type="number"
          step="0.01"
          min="0.01"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="0.01"
        />
      </div>

      <!-- Price -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Giá</label>
        <input
          v-model="orderData.price"
          type="number"
          step="0.0001"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          :placeholder="currentPrice.toString()"
        />
      </div>

      <!-- Stop Loss & Take Profit -->
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-sm text-gray-400 mb-2">Stop Loss</label>
          <input
            v-model="orderData.stopLoss"
            type="number"
            step="0.0001"
            class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="0.00"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">Take Profit</label>
          <input
            v-model="orderData.takeProfit"
            type="number"
            step="0.0001"
            class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="0.00"
          />
        </div>
      </div>

      <!-- Order Type -->
      <div>
        <label class="block text-sm text-gray-400 mb-2">Loại lệnh</label>
        <select
          v-model="orderData.type"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="market">Market</option>
          <option value="limit">Limit</option>
          <option value="stop">Stop</option>
        </select>
      </div>

      <!-- Submit Button -->
      <button
        @click="placeOrder"
        :class="[
          'w-full py-4 rounded-lg font-bold text-lg transition-all shadow-lg',
          orderSide === 'buy'
            ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600'
            : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600'
        ]"
      >
        ĐẶT LỆNH {{ orderSide === 'buy' ? 'MUA' : 'BÁN' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useMarketStore } from '../../../../stores/market';
import { useTradingStore } from '../../../../stores/trading';

const marketStore = useMarketStore();
const tradingStore = useTradingStore();

const orderSide = ref('buy');
const orderData = ref({
  quantity: 0.01,
  price: null,
  stopLoss: 0,
  takeProfit: 0,
  type: 'market',
});

const currentPrice = computed(() => {
  const selected = marketStore.selectedInstrument;
  if (selected) {
    const priceData = marketStore.getPrice(selected.symbol);
    return priceData.price || selected.price || 1.0842;
  }
  return 1.0842;
});

// Watch current price and update order price
watch(() => currentPrice.value, (newPrice) => {
  if (!orderData.value.price) {
    orderData.value.price = newPrice;
  }
}, { immediate: true });

const placeOrder = async () => {
  const order = {
    symbol: marketStore.selectedInstrument?.symbol || 'EUR/USD',
    side: orderSide.value,
    type: orderData.value.type,
    quantity: parseFloat(orderData.value.quantity),
    price: orderData.value.type === 'market' ? null : parseFloat(orderData.value.price),
    stopLoss: parseFloat(orderData.value.stopLoss) || null,
    takeProfit: parseFloat(orderData.value.takeProfit) || null,
  };

  try {
    await tradingStore.placeOrder(order);
    // Reset form
    orderData.value = {
      quantity: 0.01,
      price: currentPrice.value,
      stopLoss: 0,
      takeProfit: 0,
      type: 'market',
    };
  } catch (error) {
    console.error('Error placing order:', error);
  }
};
</script>


