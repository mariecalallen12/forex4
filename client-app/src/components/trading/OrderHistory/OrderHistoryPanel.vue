<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-history mr-2 text-purple-400"></i>
        Lịch Sử Lệnh
      </h3>
      <button
        @click="refreshHistory"
        class="text-sm text-purple-400 hover:text-purple-300 transition-colors"
        :disabled="tradingStore.isLoading"
      >
        <i class="fas fa-sync-alt" :class="{ 'animate-spin': tradingStore.isLoading }"></i>
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-4 space-y-2">
      <div class="grid grid-cols-2 gap-2">
        <select
          v-model="filters.status"
          class="px-3 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="filled">Đã khớp</option>
          <option value="partial">Khớp một phần</option>
          <option value="cancelled">Đã hủy</option>
          <option value="rejected">Từ chối</option>
        </select>
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
      </div>
      <div class="flex items-center space-x-2">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Tìm kiếm..."
          class="flex-1 px-3 py-2 bg-slate-700/50 border border-purple-500/30 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          @click="applyFilters"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 transition-colors"
        >
          Lọc
        </button>
      </div>
    </div>

    <!-- Order History List -->
    <div class="space-y-2 max-h-96 overflow-y-auto">
      <div
        v-for="order in filteredOrders"
        :key="order.id"
        @click="selectOrder(order)"
        class="bg-slate-700/30 rounded-lg p-3 cursor-pointer hover:bg-slate-700/50 transition-colors"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <span
              :class="[
                'px-2 py-1 rounded text-xs font-bold',
                order.side === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              ]"
            >
              {{ order.side === 'buy' ? 'MUA' : 'BÁN' }}
            </span>
            <span class="text-white font-medium">{{ order.symbol }}</span>
          </div>
          <span
            :class="[
              'text-sm font-bold',
              getStatusColor(order.status)
            ]"
          >
            {{ getStatusText(order.status) }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs text-gray-400">
          <div>
            <span>Khối lượng:</span>
            <span class="text-white ml-1">{{ formatNumber(order.quantity) }}</span>
          </div>
          <div>
            <span>Giá:</span>
            <span class="text-white ml-1">{{ formatPrice(order.price || order.executed_price) }}</span>
          </div>
          <div>
            <span>Loại:</span>
            <span class="text-white ml-1">{{ order.order_type || 'Market' }}</span>
          </div>
          <div>
            <span>Thời gian:</span>
            <span class="text-white ml-1">{{ formatDate(order.created_at || order.timestamp) }}</span>
          </div>
        </div>
        <div v-if="order.executed_quantity" class="mt-2 text-xs text-gray-400">
          Đã khớp: {{ formatNumber(order.executed_quantity) }} / {{ formatNumber(order.quantity) }}
        </div>
      </div>

      <div v-if="filteredOrders.length === 0" class="text-center text-gray-400 py-8">
        <i class="fas fa-inbox text-4xl mb-2 opacity-50"></i>
        <p>Không có lệnh nào</p>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div
      v-if="selectedOrder"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="selectedOrder = null"
    >
      <div class="bg-slate-800 rounded-lg border border-purple-500/30 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-white">Chi Tiết Lệnh</h3>
          <button
            @click="selectedOrder = null"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-sm text-gray-400">Mã lệnh</div>
              <div class="text-white font-medium">{{ selectedOrder.id }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-400">Cặp giao dịch</div>
              <div class="text-white font-medium">{{ selectedOrder.symbol }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-400">Loại lệnh</div>
              <div class="text-white font-medium">{{ selectedOrder.order_type || 'Market' }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-400">Hướng</div>
              <span
                :class="[
                  'px-2 py-1 rounded text-sm font-bold',
                  selectedOrder.side === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                ]"
              >
                {{ selectedOrder.side === 'buy' ? 'MUA' : 'BÁN' }}
              </span>
            </div>
            <div>
              <div class="text-sm text-gray-400">Khối lượng</div>
              <div class="text-white font-medium">{{ formatNumber(selectedOrder.quantity) }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-400">Giá</div>
              <div class="text-white font-medium">{{ formatPrice(selectedOrder.price || selectedOrder.executed_price) }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-400">Trạng thái</div>
              <span :class="['text-sm font-bold', getStatusColor(selectedOrder.status)]">
                {{ getStatusText(selectedOrder.status) }}
              </span>
            </div>
            <div>
              <div class="text-sm text-gray-400">Thời gian</div>
              <div class="text-white text-sm">{{ formatDate(selectedOrder.created_at || selectedOrder.timestamp) }}</div>
            </div>
          </div>
          <div v-if="selectedOrder.executed_quantity" class="pt-4 border-t border-slate-700">
            <h4 class="text-sm font-bold text-white mb-2">Thông tin khớp lệnh</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-sm text-gray-400">Đã khớp</div>
                <div class="text-white">{{ formatNumber(selectedOrder.executed_quantity) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-400">Giá khớp trung bình</div>
                <div class="text-white">{{ formatPrice(selectedOrder.average_price || selectedOrder.executed_price) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-400">Phí giao dịch</div>
                <div class="text-white">{{ formatPrice(selectedOrder.commission || 0) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-400">Còn lại</div>
                <div class="text-white">{{ formatNumber(selectedOrder.remaining_quantity || 0) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useTradingStore } from '../../../stores/trading';

const tradingStore = useTradingStore();
const selectedOrder = ref(null);
const filters = ref({
  status: '',
  symbol: '',
  search: '',
});

// Mock data for demonstration - will be replaced with real API data
const mockOrders = ref([
  {
    id: 'ORD-001',
    symbol: 'EUR/USD',
    side: 'buy',
    order_type: 'market',
    quantity: 0.10,
    price: null,
    executed_price: 1.0842,
    executed_quantity: 0.10,
    remaining_quantity: 0,
    average_price: 1.0842,
    commission: 0.50,
    status: 'filled',
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'ORD-002',
    symbol: 'BTC/USD',
    side: 'buy',
    order_type: 'limit',
    quantity: 0.05,
    price: 43000,
    executed_price: 43000,
    executed_quantity: 0.05,
    remaining_quantity: 0,
    average_price: 43000,
    commission: 2.15,
    status: 'filled',
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: 'ORD-003',
    symbol: 'EUR/USD',
    side: 'sell',
    order_type: 'limit',
    quantity: 0.20,
    price: 1.0850,
    executed_quantity: 0,
    remaining_quantity: 0.20,
    status: 'cancelled',
    created_at: new Date(Date.now() - 10800000).toISOString(),
  },
]);

const filteredOrders = computed(() => {
  let orders = tradingStore.orderHistory.length > 0 ? tradingStore.orderHistory : mockOrders.value;
  
  if (filters.value.status) {
    orders = orders.filter(order => order.status === filters.value.status);
  }
  
  if (filters.value.symbol) {
    orders = orders.filter(order => order.symbol === filters.value.symbol);
  }
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    orders = orders.filter(order => 
      order.id.toLowerCase().includes(search) ||
      order.symbol.toLowerCase().includes(search)
    );
  }
  
  return orders.sort((a, b) => {
    const dateA = new Date(a.created_at || a.timestamp || 0);
    const dateB = new Date(b.created_at || b.timestamp || 0);
    return dateB - dateA;
  });
});

const getStatusColor = (status) => {
  const colors = {
    filled: 'text-green-400',
    partial: 'text-yellow-400',
    cancelled: 'text-gray-400',
    rejected: 'text-red-400',
    pending: 'text-blue-400',
  };
  return colors[status] || 'text-gray-400';
};

const getStatusText = (status) => {
  const texts = {
    filled: 'Đã khớp',
    partial: 'Khớp một phần',
    cancelled: 'Đã hủy',
    rejected: 'Từ chối',
    pending: 'Chờ khớp',
  };
  return texts[status] || status;
};

const formatNumber = (num) => {
  if (!num) return '0';
  return parseFloat(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
};

const formatPrice = (price) => {
  if (!price) return '-';
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

const selectOrder = (order) => {
  selectedOrder.value = order;
};

const applyFilters = () => {
  // Filters are reactive, no need for explicit action
};

const refreshHistory = async () => {
  try {
    await tradingStore.fetchOrderHistory(filters.value);
  } catch (error) {
    console.error('Error fetching order history:', error);
  }
};

onMounted(async () => {
  // Load order history on mount
  if (tradingStore.orderHistory.length === 0) {
    await refreshHistory();
  }
});

watch(() => filters.value, () => {
  // Auto-apply filters when they change
}, { deep: true });
</script>

