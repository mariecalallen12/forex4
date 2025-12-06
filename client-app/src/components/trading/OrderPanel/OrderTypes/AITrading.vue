<template>
  <div class="flex-1 flex flex-col space-y-4">
    <!-- AI Model Selection -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Mô hình AI</label>
      <select
        v-model="aiSettings.model"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="lstm">LSTM Neural Network</option>
        <option value="transformer">Transformer Model</option>
        <option value="ensemble">Ensemble Model</option>
        <option value="reinforcement">Reinforcement Learning</option>
      </select>
    </div>

    <!-- Symbol Selection -->
    <div>
      <label class="block text-sm text-gray-400 mb-2">Cặp giao dịch</label>
      <select
        v-model="aiSettings.symbol"
        class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        <option value="EUR/USD">EUR/USD</option>
        <option value="GBP/USD">GBP/USD</option>
        <option value="BTC/USD">BTC/USD</option>
        <option value="ETH/USD">ETH/USD</option>
      </select>
    </div>

    <!-- AI Prediction Display -->
    <div class="bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-lg p-4 border border-purple-500/30">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-400">Dự đoán AI</span>
        <span class="text-sm font-bold text-purple-400">{{ aiPrediction.direction }}</span>
      </div>
      <div class="text-2xl font-bold text-white mb-2">
        {{ formatPrice(aiPrediction.price) }}
      </div>
      <div class="flex items-center justify-between text-xs">
        <div>
          <span class="text-gray-400">Confidence:</span>
          <span class="text-green-400 font-bold ml-1">{{ aiPrediction.confidence }}%</span>
        </div>
        <div>
          <span class="text-gray-400">Timeframe:</span>
          <span class="text-white ml-1">{{ aiPrediction.timeframe }}</span>
        </div>
      </div>
    </div>

    <!-- Trading Parameters -->
    <div class="space-y-3">
      <div>
        <label class="block text-sm text-gray-400 mb-2">Số tiền đầu tư</label>
        <input
          v-model.number="aiSettings.amount"
          type="number"
          step="0.01"
          min="10"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="1000.00"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Ngưỡng confidence tối thiểu (%)</label>
        <input
          v-model.number="aiSettings.minConfidence"
          type="number"
          step="1"
          min="50"
          max="100"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="70"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Stop Loss (%)</label>
        <input
          v-model.number="aiSettings.stopLoss"
          type="number"
          step="0.1"
          min="0.1"
          max="10"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="2.0"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-2">Take Profit (%)</label>
        <input
          v-model.number="aiSettings.takeProfit"
          type="number"
          step="0.1"
          min="0.1"
          max="20"
          class="w-full px-4 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="5.0"
        />
      </div>
    </div>

    <!-- Risk Management -->
    <div class="bg-slate-700/30 rounded-lg p-4">
      <h4 class="text-sm font-bold text-white mb-2">Quản lý rủi ro</h4>
      <div class="space-y-2 text-xs">
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Max Risk per Trade:</span>
          <span class="text-white">{{ aiSettings.maxRisk }}%</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Daily Loss Limit:</span>
          <span class="text-white">${{ formatNumber(aiSettings.dailyLossLimit) }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">Max Positions:</span>
          <span class="text-white">{{ aiSettings.maxPositions }}</span>
        </div>
      </div>
    </div>

    <!-- Auto Trading Toggle -->
    <div class="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
      <div>
        <div class="text-sm font-bold text-white">Tự động giao dịch</div>
        <div class="text-xs text-gray-400">AI sẽ tự động đặt lệnh khi đạt ngưỡng confidence</div>
      </div>
      <label class="relative inline-flex items-center cursor-pointer">
        <input
          v-model="aiSettings.autoTrade"
          type="checkbox"
          class="sr-only peer"
        />
        <div class="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
      </label>
    </div>

    <!-- Submit Button -->
    <button
      @click="startAITrading"
      :disabled="aiPrediction.confidence < aiSettings.minConfidence"
      :class="[
        'w-full py-3 rounded-lg font-bold text-lg transition-all shadow-lg',
        aiPrediction.confidence >= aiSettings.minConfidence
          ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700'
          : 'bg-slate-600 text-gray-400 cursor-not-allowed'
      ]"
    >
      {{ aiSettings.autoTrade ? 'Bật AI Trading' : 'Đặt lệnh theo AI' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTradingStore } from '../../../../stores/trading';
import { useMarketStore } from '../../../../stores/market';

const tradingStore = useTradingStore();
const marketStore = useMarketStore();

const aiSettings = ref({
  model: 'lstm',
  symbol: 'EUR/USD',
  amount: 1000,
  minConfidence: 70,
  stopLoss: 2.0,
  takeProfit: 5.0,
  maxRisk: 2,
  dailyLossLimit: 500,
  maxPositions: 5,
  autoTrade: false,
});

const aiPrediction = computed(() => {
  // Mock AI prediction - in production, this would come from API
  const currentPrice = marketStore.getPrice(aiSettings.value.symbol)?.price || 1.0842;
  const confidence = 75 + Math.floor(Math.random() * 20); // 75-95%
  const direction = confidence > 80 ? 'TĂNG' : confidence > 70 ? 'ỔN ĐỊNH' : 'GIẢM';
  const predictedChange = (confidence - 75) / 100;
  const predictedPrice = currentPrice * (1 + predictedChange * 0.01);
  
  return {
    price: predictedPrice,
    direction: direction,
    confidence: confidence,
    timeframe: '1H',
  };
});

const formatPrice = (price) => {
  if (!price && price !== 0) return '0.00';
  return parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
};

const formatNumber = (num) => {
  if (!num && num !== 0) return '0.00';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const startAITrading = async () => {
  if (aiPrediction.value.confidence < aiSettings.value.minConfidence) {
    alert(`Confidence ${aiPrediction.value.confidence}% thấp hơn ngưỡng tối thiểu ${aiSettings.value.minConfidence}%`);
    return;
  }

  const order = {
    order_type: 'ai_trading',
    symbol: aiSettings.value.symbol,
    model: aiSettings.value.model,
    prediction: aiPrediction.value,
    ...aiSettings.value,
  };

  try {
    await tradingStore.placeOrder(order);
    alert('Đã đặt lệnh theo dự đoán AI');
  } catch (error) {
    console.error('Error starting AI trading:', error);
  }
};
</script>
