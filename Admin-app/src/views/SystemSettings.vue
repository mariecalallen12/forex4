<script setup>
import { ref, onMounted } from 'vue';
import { useAppStore } from '../store/app';
import api from '../services/api';
import toastService from '../services/toast';
import GeneralSettings from '../components/settings/GeneralSettings.vue';
import ToggleSwitch from '../components/settings/ToggleSwitch.vue';
import Input from '../components/ui/Input.vue';
import Card from '../components/ui/Card.vue';
import Button from '../components/ui/Button.vue';

const appStore = useAppStore();
const activeTab = ref('general');
const settings = ref({ ...appStore.settings });
const loading = ref(false);

const tabs = [
  { id: 'general', label: 'Chung', icon: 'fa-cog' },
  { id: 'security', label: 'Bảo mật', icon: 'fa-shield-alt' },
  { id: 'trading', label: 'Giao dịch', icon: 'fa-exchange-alt' },
  { id: 'notifications', label: 'Thông báo', icon: 'fa-bell' },
  { id: 'api', label: 'API', icon: 'fa-code' },
  { id: 'system', label: 'Hệ thống', icon: 'fa-info-circle' },
];

const fetchSettings = async () => {
  loading.value = true;
  try {
    // TODO: API call
    // const response = await api.get('/api/admin/settings');
    // settings.value = response;
  } catch (error) {
    toastService.error('Không thể tải cài đặt');
  } finally {
    loading.value = false;
  }
};

const saveSettings = async () => {
  loading.value = true;
  try {
    // await api.put('/api/admin/settings', settings.value);
    await appStore.updateSettings(settings.value);
    toastService.success('Đã lưu cài đặt');
  } catch (error) {
    toastService.error('Không thể lưu cài đặt');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSettings();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Cài đặt hệ thống</h1>
        <p class="text-white/60">Cấu hình và quản lý hệ thống</p>
      </div>
      <Button variant="primary" @click="saveSettings" :loading="loading">
        <i class="fas fa-save mr-2"></i>
        Lưu cài đặt
      </Button>
    </div>

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

    <!-- General Settings -->
    <GeneralSettings
      v-if="activeTab === 'general'"
      :settings="settings"
      @update:settings="settings = { ...settings, ...$event }"
    />

    <!-- Security Settings -->
    <Card v-if="activeTab === 'security'" title="Cài đặt bảo mật">
      <div class="space-y-4">
        <Input v-model="settings.sessionTimeout" label="Thời gian chờ phiên (phút)" type="number" />
        <Input v-model="settings.passwordMinLength" label="Độ dài mật khẩu tối thiểu" type="number" />
        <Input v-model="settings.maxLoginAttempts" label="Số lần đăng nhập tối đa" type="number" />
        <Input v-model="settings.lockoutDuration" label="Thời gian khóa (phút)" type="number" />
        <div class="border-t border-white/10 pt-4 space-y-2">
          <ToggleSwitch v-model="settings.twoFactorRequired" label="Yêu cầu 2FA" />
          <ToggleSwitch v-model="settings.emailVerification" label="Xác thực email" />
          <ToggleSwitch v-model="settings.socialLogin" label="Cho phép đăng nhập mạng xã hội" />
        </div>
      </div>
    </Card>

    <!-- Trading Settings -->
    <Card v-if="activeTab === 'trading'" title="Cài đặt giao dịch">
      <div class="space-y-4">
        <Input v-model="settings.minDeposit" label="Nạp tiền tối thiểu ($)" type="number" />
        <Input v-model="settings.maxDeposit" label="Nạp tiền tối đa ($)" type="number" />
        <Input v-model="settings.minWithdrawal" label="Rút tiền tối thiểu ($)" type="number" />
        <Input v-model="settings.maxWithdrawal" label="Rút tiền tối đa ($)" type="number" />
        <Input v-model="settings.tradingFee" label="Phí giao dịch (%)" type="number" />
        <Input v-model="settings.withdrawalFee" label="Phí rút tiền ($)" type="number" />
        <Input v-model="settings.maxLeverage" label="Đòn bẩy tối đa (x)" type="number" />
        <Input v-model="settings.maxOpenPositions" label="Vị thế mở tối đa" type="number" />
        <ToggleSwitch v-model="settings.autoApproval" label="Tự động phê duyệt giao dịch nhỏ" />
      </div>
    </Card>

    <!-- Notification Settings -->
    <Card v-if="activeTab === 'notifications'" title="Cài đặt thông báo">
      <div class="space-y-2">
        <ToggleSwitch v-model="settings.emailNotifications" label="Thông báo email" />
        <ToggleSwitch v-model="settings.smsNotifications" label="Thông báo SMS" />
        <ToggleSwitch v-model="settings.pushNotifications" label="Thông báo đẩy" />
        <ToggleSwitch v-model="settings.dailyReports" label="Báo cáo hàng ngày" />
        <ToggleSwitch v-model="settings.weeklyReports" label="Báo cáo hàng tuần" />
        <ToggleSwitch v-model="settings.monthlyReports" label="Báo cáo hàng tháng" />
      </div>
    </Card>

    <!-- API Settings -->
    <Card v-if="activeTab === 'api'" title="Cài đặt API">
      <div class="space-y-4">
        <Input v-model="settings.rateLimit" label="Giới hạn tốc độ (requests/hour)" type="number" />
        <Input v-model="settings.webhookURL" label="Webhook URL" />
        <Input v-model="settings.apiVersion" label="Phiên bản API" />
        <ToggleSwitch v-model="settings.enableWebhooks" label="Bật webhook" />
        <ToggleSwitch v-model="settings.enableCORS" label="Bật CORS" />
      </div>
    </Card>

    <!-- System Info -->
    <Card v-if="activeTab === 'system'" title="Thông tin hệ thống">
      <div class="space-y-3">
        <div class="flex items-center justify-between py-2 border-b border-white/10">
          <span class="text-white/60">Phiên bản</span>
          <span class="text-white font-semibold">v2.0.0</span>
        </div>
        <div class="flex items-center justify-between py-2 border-b border-white/10">
          <span class="text-white/60">Ngày build</span>
          <span class="text-white font-semibold">2024-12-05</span>
        </div>
        <div class="flex items-center justify-between py-2">
          <span class="text-white/60">Môi trường</span>
          <span class="text-white font-semibold">Production</span>
        </div>
      </div>
    </Card>
  </div>
</template>

