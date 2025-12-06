<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import TradingStatsCards from '../components/trading/TradingStatsCards.vue';
import TradeTable from '../components/trading/TradeTable.vue';
import TradeFilters from '../components/trading/TradeFilters.vue';
import TradeDetailsModal from '../components/trading/TradeDetailsModal.vue';
import Card from '../components/ui/Card.vue';
import Button from '../components/ui/Button.vue';

const stats = ref({
  totalTrades: 47293,
  pendingTrades: 23,
  approvedToday: 1247,
  totalVolume: 2450000,
});

const trades = ref([]);
const selectedTrade = ref(null);
const showTradeModal = ref(false);
const loading = ref(false);
const activeTab = ref('all');

const filters = ref({
  symbol: '',
  status: 'all',
  dateFrom: '',
  dateTo: '',
});

const pagination = ref({
  page: 1,
  limit: 50,
  total: 0,
});

const fetchTrades = async () => {
  loading.value = true;
  try {
    // TODO: Replace with actual API call
    // const response = await api.get('/api/admin/trades', {
    //   ...filters.value,
    //   page: pagination.value.page,
    //   limit: pagination.value.limit,
    //   status: activeTab.value !== 'all' ? activeTab.value : undefined,
    // });
    // trades.value = response.data || response.trades || [];
    // pagination.value.total = response.pagination?.total || 0;
    
    // Mock data
    trades.value = [
      {
        id: 1,
        trade_id: 'TRD-001',
        user_id: 'USR-001',
        symbol: 'BTC/USD',
        side: 'buy',
        type: 'Market',
        quantity: 0.5,
        price: 45000,
        value: 22500,
        status: 'pending',
      },
    ];
  } catch (error) {
    toastService.error('Không thể tải danh sách giao dịch');
  } finally {
    loading.value = false;
  }
};

const handleView = (tradeId) => {
  selectedTrade.value = trades.value.find(t => t.id === tradeId);
  showTradeModal.value = true;
};

const handleApprove = async (tradeId) => {
  try {
    // await api.post(`/api/admin/trades/${tradeId}/approve`);
    toastService.success('Đã phê duyệt giao dịch');
    await fetchTrades();
    showTradeModal.value = false;
  } catch (error) {
    toastService.error('Không thể phê duyệt giao dịch');
  }
};

const handleReject = async (tradeId) => {
  try {
    // await api.post(`/api/admin/trades/${tradeId}/reject`);
    toastService.success('Đã từ chối giao dịch');
    await fetchTrades();
    showTradeModal.value = false;
  } catch (error) {
    toastService.error('Không thể từ chối giao dịch');
  }
};

const handleBatchApprove = async () => {
  const pendingTrades = trades.value.filter(t => t.status === 'pending');
  if (pendingTrades.length === 0) {
    toastService.warning('Không có giao dịch chờ phê duyệt');
    return;
  }
  
  try {
    // await api.post('/api/admin/trades/batch-approve', {
    //   trade_ids: pendingTrades.map(t => t.id),
    // });
    toastService.success(`Đã phê duyệt ${pendingTrades.length} giao dịch`);
    await fetchTrades();
  } catch (error) {
    toastService.error('Không thể phê duyệt hàng loạt');
  }
};

const handlePageChange = (page) => {
  pagination.value.page = page;
  fetchTrades();
};

const handleFilterUpdate = (newFilters) => {
  filters.value = { ...filters.value, ...newFilters };
  pagination.value.page = 1;
  fetchTrades();
};

const tabs = [
  { id: 'all', label: 'Tất cả' },
  { id: 'pending', label: 'Chờ phê duyệt' },
  { id: 'approved', label: 'Đã phê duyệt' },
  { id: 'rejected', label: 'Đã từ chối' },
];

onMounted(() => {
  fetchTrades();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Quản lý giao dịch</h1>
        <p class="text-white/60">Quản lý và phê duyệt giao dịch</p>
      </div>
      <Button
        v-if="activeTab === 'pending'"
        variant="primary"
        icon="fas fa-check-double"
        @click="handleBatchApprove"
      >
        Phê duyệt hàng loạt
      </Button>
    </div>

    <!-- Stats Cards -->
    <TradingStatsCards :stats="stats" />

    <!-- Tabs -->
    <div class="flex items-center gap-2 border-b border-white/10">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="[
          'px-4 py-2 font-medium transition-colors border-b-2',
          activeTab === tab.id
            ? 'text-primary border-primary'
            : 'text-white/60 border-transparent hover:text-white',
        ]"
        @click="activeTab = tab.id; fetchTrades()"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Filters -->
    <TradeFilters
      :filters="filters"
      @update:filters="handleFilterUpdate"
    />

    <!-- Trade Table -->
    <Card>
      <TradeTable
        :trades="trades"
        :loading="loading"
        :pagination="pagination"
        @view="handleView"
        @approve="handleApprove"
        @reject="handleReject"
        @page-change="handlePageChange"
      />
    </Card>

    <!-- Trade Details Modal -->
    <TradeDetailsModal
      :show="showTradeModal"
      :trade="selectedTrade"
      @update:show="showTradeModal = $event"
      @close="showTradeModal = false"
      @approve="handleApprove(selectedTrade?.id)"
      @reject="handleReject(selectedTrade?.id)"
    />
  </div>
</template>

