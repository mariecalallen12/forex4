<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-6 flex items-center">
      <i class="fas fa-lock mr-2 text-purple-400"></i>
      Cài Đặt Bảo Mật
    </h3>

    <!-- 2FA Section -->
    <div class="mb-6 pb-6 border-b border-purple-500/20">
      <div class="flex items-center justify-between mb-4">
        <div>
          <div class="text-white font-medium mb-1">Xác thực 2 yếu tố (2FA)</div>
          <div class="text-purple-300 text-xs">Bảo mật tài khoản với ứng dụng xác thực</div>
        </div>
        <StatusBadge :status="twoFAEnabled ? 'completed' : 'pending'" />
      </div>
      <button
        v-if="!twoFAEnabled"
        @click="setup2FA"
        class="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg text-sm font-medium hover:from-green-600 hover:to-emerald-600 transition-all"
      >
        <i class="fas fa-key mr-2"></i>Bật 2FA
      </button>
      <button
        v-else
        @click="disable2FA"
        class="px-4 py-2 bg-red-500/20 text-red-300 rounded-lg text-sm font-medium hover:bg-red-500/30 transition-all"
      >
        <i class="fas fa-ban mr-2"></i>Tắt 2FA
      </button>
    </div>

    <!-- Password Section -->
    <div>
      <div class="mb-4">
        <div class="text-white font-medium mb-1">Đổi mật khẩu</div>
        <div class="text-purple-300 text-xs">Mật khẩu cuối cùng thay đổi: 30 ngày trước</div>
      </div>
      <button
        @click="showChangePassword = true"
        class="px-4 py-2 bg-purple-500/20 border border-purple-500/30 text-purple-300 rounded-lg text-sm font-medium hover:bg-purple-500/30 transition-all"
      >
        <i class="fas fa-key mr-2"></i>Đổi mật khẩu
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import StatusBadge from '../shared/StatusBadge.vue';

const twoFAEnabled = ref(true);
const showChangePassword = ref(false);

const setup2FA = () => {
  // Show 2FA setup modal
  console.log('Setup 2FA');
};

const disable2FA = () => {
  // Show disable 2FA confirmation
  console.log('Disable 2FA');
};
</script>

