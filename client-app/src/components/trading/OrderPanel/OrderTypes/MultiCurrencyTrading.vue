<template>
  <div class="flex-1 flex flex-col space-y-4">
    <!-- Base Currency -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Tiền tệ cơ sở</label>
      <select
        v-model="baseCurrency"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="USD">USD - US Dollar</option>
        <option value="EUR">EUR - Euro</option>
        <option value="GBP">GBP - British Pound</option>
        <option value="JPY">JPY - Japanese Yen</option>
        <option value="CNY">CNY - Chinese Yuan</option>
        <option value="VND">VND - Vietnamese Dong</option>
        <option value="BTC">BTC - Bitcoin</option>
        <option value="ETH">ETH - Ethereum</option>
      </select>
    </div>

    <!-- Quote Currency -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Tiền tệ đích</label>
      <select
        v-model="quoteCurrency"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="USD">USD - US Dollar</option>
        <option value="EUR">EUR - Euro</option>
        <option value="GBP">GBP - British Pound</option>
        <option value="JPY">JPY - Japanese Yen</option>
        <option value="CNY">CNY - Chinese Yuan</option>
        <option value="VND">VND - Vietnamese Dong</option>
        <option value="BTC">BTC - Bitcoin</option>
        <option value="ETH">ETH - Ethereum</option>
      </select>
    </div>

    <!-- Exchange Rate Display -->
    <div class="bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-lg p-4 border border-purple-500/30">
      <div class="text-center">
        <div class="text-xs text-gray-400 mb-1">Tỷ giá hiện tại</div>
        <div class="text-2xl font-bold text-white mb-2">
          1 {{ baseCurrency }} = {{ formatRate(exchangeRate) }} {{ quoteCurrency }}
        </div>
        <div class="text-xs text-gray-400">
          Cập nhật: {{ formatTime(new Date()) }}
        </div>
      </div>
    </div>

    <!-- Amount -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Số lượng ({{ baseCurrency }})</label>
      <input
        v-model.number="orderData.amount"
        type="number"
        step="0.01"
        min="0.01"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        placeholder="100.00"
      />
    </div>

    <!-- Converted Amount -->
    <div class="bg-slate-700/30 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-400">Số tiền nhận được</span>
        <span class="text-lg font-bold text-white">
          {{ formatNumber(convertedAmount) }} {{ quoteCurrency }}
        </span>
      </div>
      <div class="text-xs text-gray-500 mt-1">
        Phí giao dịch: {{ formatNumber(fee) }} {{ quoteCurrency }}
      </div>
    </div>

    <!-- Order Type -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Loại lệnh</label>
      <select
        v-model="orderData.orderType"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="market">Market (Khớp ngay)</option>
        <option value="limit">Limit (Giá chỉ định)</option>
      </select>
    </div>

    <!-- Limit Price (if limit order) -->
    <div v-if="orderData.orderType === 'limit'">
      <label class="block text-sm text-gray-400 mb-2">Giá limit</label>
      <input
        v-model.number="orderData.limitPrice"
        type="number"
        step="0.0001"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        :placeholder="exchangeRate.toString()"
      />
    </div>

    <!-- Currency Pairs Info -->
    <div class="bg-slate-700/30 rounded-lg p-4">
      <h4 class="text-sm font-bold text-white mb-2">Thông tin cặp tiền</h4>
      <div class="space-y-1 text-xs">
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Symbol:</span>
          <span class="text-white">{{ baseCurrency }}/{{ quoteCurrency }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Spread:</span>
          <span class="text-purple-400">{{ spread.toFixed(4) }}%</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Min Amount:</span>
          <span class="text-white">10 {{ baseCurrency }}</span>
        </div>
      </div>
    </div>

    <!-- Submit Button -->
    <button
      @click="placeMultiCurrencyOrder"
      class="w-full py-3 rounded-lg font-bold text-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
    >
      Đổi {{ baseCurrency }} → {{ quoteCurrency }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useTradingStore } from '../../../../stores/trading';

const tradingStore = useTradingStore();

const baseCurrency = ref('USD');
const quoteCurrency = ref('EUR');
const orderData = ref({
  amount: 100,
  orderType: 'market',
  limitPrice: null,
});

// Mock exchange rates (in production, fetch from API)
const exchangeRates = ref({
  'USD/EUR': 0.92,
  'USD/GBP': 0.79,
  'USD/JPY': 149.8,
  'USD/CNY': 7.15,
  'USD/VND': 24500,
  'USD/BTC': 0.000023,
  'USD/ETH': 0.00038,
  'EUR/USD': 1.084,
  'EUR/GBP': 0.86,
  'GBP/USD': 1.26,
  'BTC/USD': 43250,
  'ETH/USD': 2650,
});

const exchangeRate = computed(() => {
  const pair = `${baseCurrency.value}/${quoteCurrency.value}`;
  const reversePair = `${quoteCurrency.value}/${baseCurrency.value}`;
  
  if (exchangeRates.value[pair]) {
    return exchangeRates.value[pair];
  } else if (exchangeRates.value[reversePair]) {
    return 1 / exchangeRates.value[reversePair];
  }
  
  // Default fallback
  return baseCurrency.value === 'USD' && quoteCurrency.value === 'EUR' ? 0.92 : 1.0;
});

const spread = computed(() => {
  // Typical spread is 0.1-0.5% for major pairs
  return 0.2;
});

const fee = computed(() => {
  // 0.1% fee
  return (orderData.value.amount || 0) * exchangeRate.value * 0.001;
});

const convertedAmount = computed(() => {
  const amount = orderData.value.amount || 0;
  return amount * exchangeRate.value - fee.value;
});

const formatRate = (rate) => {
  if (!rate && rate !== 0) return '0.0000';
  return parseFloat(rate).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 8 });
};

const formatNumber = (num) => {
  if (!num && num !== 0) return '0.00';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
};

const formatTime = (date) => {
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

const placeMultiCurrencyOrder = async () => {
  if (baseCurrency.value === quoteCurrency.value) {
    alert('Vui lòng chọn hai loại tiền tệ khác nhau');
    return;
  }

  const order = {
    order_type: 'multi_currency',
    base_currency: baseCurrency.value,
    quote_currency: quoteCurrency.value,
    symbol: `${baseCurrency.value}/${quoteCurrency.value}`,
    amount: orderData.value.amount,
    exchange_rate: exchangeRate.value,
    fee: fee.value,
    converted_amount: convertedAmount.value,
    order_type_detail: orderData.value.orderType,
    limit_price: orderData.value.limitPrice,
  };

  try {
    await tradingStore.placeOrder(order);
    alert(`Đã đặt lệnh đổi ${orderData.value.amount} ${baseCurrency.value} sang ${quoteCurrency.value}`);
    // Reset form
    orderData.value = {
      amount: 100,
      orderType: 'market',
      limitPrice: null,
    };
  } catch (error) {
    console.error('Error placing multi-currency order:', error);
  }
};

watch([baseCurrency, quoteCurrency], () => {
  if (orderData.value.orderType === 'limit' && !orderData.value.limitPrice) {
    orderData.value.limitPrice = exchangeRate.value;
  }
});
</script>
