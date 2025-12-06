<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import toastService from '../services/toast';
import DashboardStats from '../components/dashboard/DashboardStats.vue';
import SystemStatus from '../components/dashboard/SystemStatus.vue';
import SystemHealth from '../components/dashboard/SystemHealth.vue';
import RecentActivities from '../components/dashboard/RecentActivities.vue';
import TradingVolumeChart from '../components/dashboard/TradingVolumeChart.vue';

const stats = ref({
  totalUsers: 12483,
  activeUsers: 8429,
  totalTrades: 47293,
  revenueToday: 1247832,
});

const systemStatus = ref({
  uptime: 99.9,
  systemLoad: 45,
});

const services = ref([
  { name: 'Database', status: 'operational', icon: 'fa-database' },
  { name: 'API Services', status: 'active', icon: 'fa-server' },
  { name: 'Trading Engine', status: 'high-load', icon: 'fa-cogs' },
]);

const activities = ref([
  {
    id: 1,
    type: 'user_registration',
    message: 'Người dùng mới đăng ký',
    user: 'user@example.com',
    time: '2 phút trước',
    icon: 'fa-user-plus',
    color: 'text-green-400',
  },
  {
    id: 2,
    type: 'large_trade',
    message: 'Giao dịch lớn',
    amount: '$50,000',
    time: '5 phút trước',
    icon: 'fa-exchange-alt',
    color: 'text-blue-400',
  },
  {
    id: 3,
    type: 'deposit_approval',
    message: 'Phê duyệt nạp tiền',
    amount: '$10,000',
    time: '10 phút trước',
    icon: 'fa-check-circle',
    color: 'text-green-400',
  },
  {
    id: 4,
    type: 'system_backup',
    message: 'Backup hệ thống',
    time: '15 phút trước',
    icon: 'fa-database',
    color: 'text-purple-primary',
  },
  {
    id: 5,
    type: 'warning',
    message: 'Cảnh báo khối lượng giao dịch cao',
    time: '20 phút trước',
    icon: 'fa-exclamation-triangle',
    color: 'text-yellow-400',
  },
]);

const chartData = ref({
  labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
  datasets: [
    {
      label: 'Trading Volume 24h',
      data: [120, 190, 300, 500, 200, 300, 450],
    },
  ],
});

const loading = ref(false);

const fetchDashboardData = async () => {
  loading.value = true;
  try {
    // Fetch dashboard stats
    const [dashboardResponse, platformStatsResponse, logsResponse, analyticsResponse] = await Promise.all([
      api.get('/api/admin/dashboard').catch(() => ({ data: {} })),
      api.get('/api/admin/platform/stats').catch(() => ({ data: {} })),
      api.get('/api/admin/logs', { limit: 10 }).catch(() => ({ data: { logs: [] } })),
      api.get('/api/admin/analytics').catch(() => ({ data: {} }))
    ]);
    
    // Update stats
    const dashboardData = dashboardResponse.data?.data || dashboardResponse.data || {};
    const platformData = platformStatsResponse.data?.data || platformStatsResponse.data || {};
    
    if (dashboardData.stats || platformData) {
      stats.value = {
        totalUsers: dashboardData.stats?.total_users || platformData.total_users || 0,
        activeUsers: dashboardData.stats?.active_users || platformData.active_users || 0,
        totalTrades: dashboardData.stats?.total_trades || platformData.total_trades || 0,
        revenueToday: dashboardData.stats?.revenue_today || platformData.revenue_today || 0,
      };
    }
    
    // Update system status
    if (platformData) {
      systemStatus.value = {
        uptime: platformData.uptime || 99.9,
        systemLoad: platformData.system_load || 45,
      };
    }
    
    // Update activities from logs
    const logsData = logsResponse.data?.data?.logs || logsResponse.data?.logs || [];
    if (logsData.length > 0) {
      activities.value = logsData.slice(0, 10).map(log => ({
        id: log.id,
        type: log.action_type || 'info',
        message: log.description || log.action_type,
        user: log.user_email || '',
        time: new Date(log.created_at).toLocaleString('vi-VN'),
        icon: 'fa-info-circle',
        color: 'text-blue-400',
      }));
    }
    
    // Update chart data from analytics
    const analyticsData = analyticsResponse.data?.data || analyticsResponse.data || {};
    if (analyticsData.trading_volume_chart) {
      chartData.value = analyticsData.trading_volume_chart;
    }
  } catch (error) {
    toastService.error('Không thể tải dữ liệu dashboard');
    console.error('Dashboard error:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Dashboard</h1>
      <p class="text-white/60">Tổng quan hệ thống và thống kê</p>
    </div>

    <!-- Stats Cards -->
    <DashboardStats :stats="stats" />

    <!-- Charts and Status -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Trading Volume Chart -->
      <div class="lg:col-span-2">
        <TradingVolumeChart :data="chartData" />
      </div>

      <!-- System Status -->
      <div class="space-y-6">
        <SystemStatus :uptime="systemStatus.uptime" :system-load="systemStatus.systemLoad" />
        <SystemHealth :services="services" />
      </div>
    </div>

    <!-- Recent Activities -->
    <RecentActivities :activities="activities" />
  </div>
</template>

