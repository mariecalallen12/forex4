<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import KPICards from '../components/analytics/KPICards.vue';
import DateRangeSelector from '../components/analytics/DateRangeSelector.vue';
import Chart from '../components/ui/Chart.vue';
import Card from '../components/ui/Card.vue';
import Table from '../components/ui/Table.vue';

const dateRange = ref('7d');
const kpis = ref({
  totalRevenue: { value: 1247832, change: 15.3 },
  activeUsers: { value: 8429, change: 8.2 },
  totalTrades: { value: 47293, change: 24.7 },
  conversionRate: { value: 12.8, change: 0.7 },
});

const topAssets = ref([
  { symbol: 'BTC/USD', volume: 2450000, trades: 1200, change: 5.2 },
  { symbol: 'ETH/USD', volume: 1890000, trades: 980, change: 3.8 },
  { symbol: 'EUR/USD', volume: 1560000, trades: 750, change: 1.2 },
  { symbol: 'GBP/USD', volume: 980000, trades: 520, change: -0.8 },
  { symbol: 'SOL/USD', volume: 750000, trades: 340, change: 12.5 },
]);

const userInsights = ref({
  averageSessionTime: '24m 32s',
  retentionRate: 78.4,
  churnRate: 4.2,
  conversionRate: 12.8,
});

const fetchAnalytics = async () => {
  try {
    // TODO: API call
  } catch (error) {
    toastService.error('Không thể tải dữ liệu phân tích');
  }
};

const assetHeaders = [
  { key: 'symbol', label: 'Symbol' },
  { key: 'volume', label: 'Volume' },
  { key: 'trades', label: 'Trades' },
  { key: 'change', label: 'Change' },
];

onMounted(() => {
  fetchAnalytics();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Phân tích & Báo cáo</h1>
        <p class="text-white/60">Thống kê và phân tích hiệu suất hệ thống</p>
      </div>
      <DateRangeSelector v-model="dateRange" @update:model-value="fetchAnalytics" />
    </div>

    <!-- KPI Cards -->
    <KPICards :kpis="kpis" />

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Tăng trưởng người dùng">
        <Chart type="line" height="300px" />
      </Card>
      <Card title="Khối lượng giao dịch">
        <Chart type="bar" height="300px" />
      </Card>
      <Card title="Xu hướng doanh thu">
        <Chart type="line" height="300px" />
      </Card>
      <Card title="Top Assets">
        <Table :headers="assetHeaders" :data="topAssets">
          <template #default="{ data }">
            <tr
              v-for="asset in data"
              :key="asset.symbol"
              class="border-b border-white/5 hover:bg-white/5"
            >
              <td class="px-4 py-3 text-white font-semibold">{{ asset.symbol }}</td>
              <td class="px-4 py-3 text-white">${{ asset.volume.toLocaleString() }}</td>
              <td class="px-4 py-3 text-white/80">{{ asset.trades.toLocaleString() }}</td>
              <td :class="['px-4 py-3', asset.change >= 0 ? 'text-green-400' : 'text-red-400']">
                {{ asset.change >= 0 ? '+' : '' }}{{ asset.change }}%
              </td>
            </tr>
          </template>
        </Table>
      </Card>
    </div>

    <!-- User Insights -->
    <Card title="Thông tin người dùng">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p class="text-white/60 text-sm mb-1">Thời gian phiên trung bình</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.averageSessionTime }}</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Tỷ lệ giữ chân</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.retentionRate }}%</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Tỷ lệ rời bỏ</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.churnRate }}%</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Tỷ lệ chuyển đổi</p>
          <p class="text-white text-2xl font-bold">{{ userInsights.conversionRate }}%</p>
        </div>
      </div>
    </Card>
  </div>
</template>

