<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import Card from '../components/ui/Card.vue';
import Input from '../components/ui/Input.vue';
import Button from '../components/ui/Button.vue';
import Table from '../components/ui/Table.vue';

const platformStats = ref({
  totalUsers: 12483,
  totalPositions: 5420,
  averageWinRate: 67.3,
  platformVolume: 2450000,
});

const riskMetrics = ref({
  highRiskUsers: 23,
  averageLeverage: 45.2,
  marginCallRisk: 12.5,
});

const topPerformers = ref([
  { rank: 1, userId: 'USR-001', winRate: 85.5, trades: 120 },
  { rank: 2, userId: 'USR-002', winRate: 82.3, trades: 98 },
  { rank: 3, userId: 'USR-003', winRate: 79.1, trades: 156 },
]);

const winRateControl = ref({
  userId: '',
  targetWinRate: 50,
});

const positionOverride = ref({
  positionId: '',
  outcome: 'profit',
  amount: 0,
});

const fetchData = async () => {
  try {
    // TODO: API calls
  } catch (error) {
    toastService.error('Không thể tải dữ liệu');
  }
};

const handleSetWinRate = async () => {
  try {
    // await api.post('/api/admin/trading-adjustments/win-rate', winRateControl.value);
    toastService.success('Đã thiết lập win rate');
  } catch (error) {
    toastService.error('Không thể thiết lập win rate');
  }
};

const handlePositionOverride = async () => {
  try {
    // await api.post('/api/admin/trading-adjustments/position-override', positionOverride.value);
    toastService.success('Đã ghi đè vị thế');
  } catch (error) {
    toastService.error('Không thể ghi đè vị thế');
  }
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Điều khiển giao dịch</h1>
      <p class="text-white/60">Quản lý và điều chỉnh giao dịch hệ thống</p>
    </div>

    <!-- Platform Overview -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <p class="text-white/60 text-sm mb-1">Tổng số user</p>
        <p class="text-3xl font-bold text-white">{{ platformStats.totalUsers.toLocaleString() }}</p>
      </Card>
      <Card>
        <p class="text-white/60 text-sm mb-1">Tổng số vị thế</p>
        <p class="text-3xl font-bold text-white">{{ platformStats.totalPositions.toLocaleString() }}</p>
      </Card>
      <Card>
        <p class="text-white/60 text-sm mb-1">Tỷ lệ thắng trung bình</p>
        <p class="text-3xl font-bold text-white">{{ platformStats.averageWinRate }}%</p>
      </Card>
      <Card>
        <p class="text-white/60 text-sm mb-1">Khối lượng platform</p>
        <p class="text-3xl font-bold text-white">${{ platformStats.platformVolume.toLocaleString() }}</p>
      </Card>
    </div>

    <!-- Risk Management -->
    <Card title="Quản lý rủi ro">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p class="text-white/60 text-sm mb-1">User rủi ro cao</p>
          <p class="text-2xl font-bold text-white">{{ riskMetrics.highRiskUsers }}</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Đòn bẩy trung bình</p>
          <p class="text-2xl font-bold text-white">{{ riskMetrics.averageLeverage }}x</p>
        </div>
        <div>
          <p class="text-white/60 text-sm mb-1">Rủi ro call margin</p>
          <p class="text-2xl font-bold text-white">{{ riskMetrics.marginCallRisk }}%</p>
        </div>
      </div>
    </Card>

    <!-- Win Rate Control -->
    <Card title="Điều khiển Win Rate">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          v-model="winRateControl.userId"
          label="User ID"
          placeholder="Nhập User ID"
        />
        <Input
          v-model="winRateControl.targetWinRate"
          label="Target Win Rate (%)"
          type="number"
        />
        <div class="flex items-end">
          <Button variant="primary" @click="handleSetWinRate" full-width>
            Thiết lập Win Rate
          </Button>
        </div>
      </div>
    </Card>

    <!-- Position Override -->
    <Card title="Ghi đè vị thế">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Input
          v-model="positionOverride.positionId"
          label="Position ID"
          placeholder="Nhập Position ID"
        />
        <div>
          <label class="block text-sm font-medium text-white/80 mb-2">Kết quả</label>
          <select
            v-model="positionOverride.outcome"
            class="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white"
          >
            <option value="profit">Profit</option>
            <option value="loss">Loss</option>
          </select>
        </div>
        <Input
          v-model="positionOverride.amount"
          label="Số tiền"
          type="number"
        />
        <div class="flex items-end">
          <Button variant="primary" @click="handlePositionOverride" full-width>
            Ghi đè
          </Button>
        </div>
      </div>
    </Card>

    <!-- Top Performers -->
    <Card title="Top Performers">
      <Table
        :headers="[
          { key: 'rank', label: 'Rank' },
          { key: 'userId', label: 'User ID' },
          { key: 'winRate', label: 'Win Rate' },
          { key: 'trades', label: 'Trades' },
        ]"
        :data="topPerformers"
      >
        <template #default="{ data }">
          <tr
            v-for="performer in data"
            :key="performer.rank"
            class="border-b border-white/5 hover:bg-white/5"
          >
            <td class="px-4 py-3 text-white font-semibold">#{{ performer.rank }}</td>
            <td class="px-4 py-3 text-white/80">{{ performer.userId }}</td>
            <td class="px-4 py-3 text-green-400 font-semibold">{{ performer.winRate }}%</td>
            <td class="px-4 py-3 text-white/80">{{ performer.trades }}</td>
          </tr>
        </template>
      </Table>
    </Card>
  </div>
</template>

