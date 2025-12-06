<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import FinancialStatsCards from '../components/financial/FinancialStatsCards.vue';
import DepositTable from '../components/financial/DepositTable.vue';
import WithdrawalTable from '../components/financial/WithdrawalTable.vue';
import ReceiptViewer from '../components/financial/ReceiptViewer.vue';
import Card from '../components/ui/Card.vue';

const stats = ref({
  totalDeposits: 5000000,
  totalWithdrawals: 2000000,
  pendingDeposits: 50000,
  pendingWithdrawals: 30000,
});

const activeTab = ref('deposits');
const deposits = ref([]);
const withdrawals = ref([]);
const invoices = ref([]);
const payments = ref([]);
const loading = ref(false);
const showReceiptModal = ref(false);
const receiptUrl = ref('');

const pagination = ref({
  page: 1,
  limit: 50,
  total: 0,
});

const tabs = [
  { id: 'deposits', label: 'Nạp tiền', icon: 'fa-arrow-down' },
  { id: 'withdrawals', label: 'Rút tiền', icon: 'fa-arrow-up' },
  { id: 'invoices', label: 'Hóa đơn', icon: 'fa-file-invoice' },
  { id: 'payments', label: 'Thanh toán', icon: 'fa-credit-card' },
];

const fetchDeposits = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/deposits', {
      page: pagination.value.page,
      limit: pagination.value.limit,
    });
    
    const data = response.data?.data || response.data || {};
    deposits.value = data.deposits || data.transactions || [];
    if (data.total !== undefined) {
      pagination.value.total = data.total;
    }
    
    // Update stats
    if (data.stats) {
      stats.value.pendingDeposits = data.stats.pending || 0;
      stats.value.totalDeposits = data.stats.total || 0;
    }
  } catch (error) {
    toastService.error('Không thể tải danh sách nạp tiền');
    console.error('Fetch deposits error:', error);
  } finally {
    loading.value = false;
  }
};

const fetchWithdrawals = async () => {
  loading.value = true;
  try {
    const response = await api.get('/api/admin/withdrawals', {
      page: pagination.value.page,
      limit: pagination.value.limit,
    });
    
    const data = response.data?.data || response.data || {};
    withdrawals.value = data.withdrawals || data.transactions || [];
    if (data.total !== undefined) {
      pagination.value.total = data.total;
    }
    
    // Update stats
    if (data.stats) {
      stats.value.pendingWithdrawals = data.stats.pending || 0;
      stats.value.totalWithdrawals = data.stats.total || 0;
    }
  } catch (error) {
    toastService.error('Không thể tải danh sách rút tiền');
    console.error('Fetch withdrawals error:', error);
  } finally {
    loading.value = false;
  }
};

const handleApproveDeposit = async (id) => {
  try {
    await api.post(`/api/admin/deposits/${id}/approve`);
    toastService.success('Đã phê duyệt nạp tiền');
    await fetchDeposits();
  } catch (error) {
    toastService.error('Không thể phê duyệt');
    console.error('Approve deposit error:', error);
  }
};

const handleRejectDeposit = async (id) => {
  try {
    await api.post(`/api/admin/deposits/${id}/reject`);
    toastService.success('Đã từ chối nạp tiền');
    await fetchDeposits();
  } catch (error) {
    toastService.error('Không thể từ chối');
    console.error('Reject deposit error:', error);
  }
};

const handleApproveWithdrawal = async (id) => {
  try {
    await api.post(`/api/admin/withdrawals/${id}/approve`);
    toastService.success('Đã phê duyệt rút tiền');
    await fetchWithdrawals();
  } catch (error) {
    toastService.error('Không thể phê duyệt');
    console.error('Approve withdrawal error:', error);
  }
};

const handleRejectWithdrawal = async (id) => {
  try {
    await api.post(`/api/admin/withdrawals/${id}/reject`);
    toastService.success('Đã từ chối rút tiền');
    await fetchWithdrawals();
  } catch (error) {
    toastService.error('Không thể từ chối');
    console.error('Reject withdrawal error:', error);
  }
};

const handleViewReceipt = (depositId) => {
  const deposit = deposits.value.find(d => d.id === depositId);
  if (deposit?.receipt_url) {
    receiptUrl.value = deposit.receipt_url;
    showReceiptModal.value = true;
  }
};

onMounted(() => {
  if (activeTab.value === 'deposits') fetchDeposits();
  if (activeTab.value === 'withdrawals') fetchWithdrawals();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Quản lý tài chính</h1>
      <p class="text-white/60">Quản lý nạp tiền, rút tiền, hóa đơn và thanh toán</p>
    </div>

    <!-- Stats Cards -->
    <FinancialStatsCards :stats="stats" />

    <!-- Tabs -->
    <div class="flex items-center gap-2 border-b border-white/10">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="[
          'px-4 py-2 font-medium transition-colors border-b-2 flex items-center gap-2',
          activeTab === tab.id
            ? 'text-primary border-primary'
            : 'text-white/60 border-transparent hover:text-white',
        ]"
        @click="activeTab = tab.id"
      >
        <i :class="['fas', tab.icon]"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- Deposits Tab -->
    <Card v-if="activeTab === 'deposits'">
      <DepositTable
        :deposits="deposits"
        :loading="loading"
        :pagination="pagination"
        @approve="handleApproveDeposit"
        @reject="handleRejectDeposit"
        @view-receipt="handleViewReceipt"
      />
    </Card>

    <!-- Withdrawals Tab -->
    <Card v-if="activeTab === 'withdrawals'">
      <WithdrawalTable
        :withdrawals="withdrawals"
        :loading="loading"
        :pagination="pagination"
        @approve="handleApproveWithdrawal"
        @reject="handleRejectWithdrawal"
      />
    </Card>

    <!-- Invoices Tab -->
    <Card v-if="activeTab === 'invoices'">
      <div class="text-center py-8 text-white/60">
        Tính năng hóa đơn đang được phát triển
      </div>
    </Card>

    <!-- Payments Tab -->
    <Card v-if="activeTab === 'payments'">
      <div class="text-center py-8 text-white/60">
        Tính năng thanh toán đang được phát triển
      </div>
    </Card>

    <!-- Receipt Viewer Modal -->
    <ReceiptViewer
      :show="showReceiptModal"
      :receipt-url="receiptUrl"
      @update:show="showReceiptModal = $event"
      @close="showReceiptModal = false"
    />
  </div>
</template>

