<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { useAuthStore } from '../store/auth';
import api from '../services/api';
import toastService from '../services/toast';
import UserTable from '../components/users/UserTable.vue';
import UserFilters from '../components/users/UserFilters.vue';
import UserBulkActions from '../components/users/UserBulkActions.vue';
import UserProfileModal from '../components/users/UserProfileModal.vue';
import Button from '../components/ui/Button.vue';
import Card from '../components/ui/Card.vue';

const userStore = useUserStore();
const authStore = useAuthStore();

const selectedUsers = ref([]);
const showUserModal = ref(false);
const selectedUser = ref(null);
const loading = ref(false);

const filters = ref({
  search: '',
  status: 'all',
  sortBy: 'created_at',
  sortOrder: 'desc',
});

const pagination = ref({
  page: 1,
  limit: 50,
  total: 0,
});

const fetchUsers = async () => {
  loading.value = true;
  try {
    await userStore.fetchUsers({
      ...filters.value,
      page: pagination.value.page,
      limit: pagination.value.limit,
    });
    pagination.value.total = userStore.pagination.total;
  } catch (error) {
    toastService.error('Không thể tải danh sách người dùng');
  } finally {
    loading.value = false;
  }
};

const handleSelect = (userId) => {
  const index = selectedUsers.value.indexOf(userId);
  if (index > -1) {
    selectedUsers.value.splice(index, 1);
  } else {
    selectedUsers.value.push(userId);
  }
};

const handleSelectAll = () => {
  if (selectedUsers.value.length === userStore.users.length) {
    selectedUsers.value = [];
  } else {
    selectedUsers.value = userStore.users.map(u => u.id);
  }
};

const handleView = async (userId) => {
  loading.value = true;
  try {
    await userStore.fetchUserById(userId);
    selectedUser.value = userStore.currentUser;
    showUserModal.value = true;
  } catch (error) {
    toastService.error('Không thể tải thông tin người dùng');
  } finally {
    loading.value = false;
  }
};

const handleUpdateStatus = async (userId, status) => {
  try {
    await userStore.updateUserStatus(userId, status);
    toastService.success('Cập nhật trạng thái thành công');
    await fetchUsers();
    if (showUserModal.value) {
      showUserModal.value = false;
    }
  } catch (error) {
    toastService.error('Không thể cập nhật trạng thái');
  }
};

const handleBulkAction = async (action) => {
  if (selectedUsers.value.length === 0) {
    toastService.warning('Vui lòng chọn ít nhất một người dùng');
    return;
  }

  try {
    await userStore.bulkUpdateStatus(selectedUsers.value, action);
    toastService.success(`Đã ${action} ${selectedUsers.value.length} người dùng`);
    selectedUsers.value = [];
    await fetchUsers();
  } catch (error) {
    toastService.error('Không thể thực hiện thao tác hàng loạt');
  }
};

const handleExport = () => {
  toastService.info('Tính năng xuất dữ liệu đang được phát triển');
};

const handlePageChange = (page) => {
  pagination.value.page = page;
  fetchUsers();
};

const handleFilterUpdate = (newFilters) => {
  filters.value = { ...filters.value, ...newFilters };
  pagination.value.page = 1;
  fetchUsers();
};

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Quản lý người dùng</h1>
        <p class="text-white/60">Quản lý và theo dõi người dùng hệ thống</p>
      </div>
      <Button variant="primary" icon="fas fa-plus">
        Thêm người dùng
      </Button>
    </div>

    <!-- Filters -->
    <UserFilters
      :filters="filters"
      @update:filters="handleFilterUpdate"
      @export="handleExport"
    />

    <!-- Bulk Actions -->
    <UserBulkActions
      :selected-count="selectedUsers.length"
      @bulk-activate="handleBulkAction('active')"
      @bulk-suspend="handleBulkAction('suspended')"
      @bulk-ban="handleBulkAction('banned')"
      @clear-selection="selectedUsers = []"
    />

    <!-- User Table -->
    <Card>
      <UserTable
        :users="userStore.users"
        :loading="loading"
        :selected-users="selectedUsers"
        :pagination="pagination"
        @select="handleSelect"
        @select-all="handleSelectAll"
        @view="handleView"
        @update-status="handleUpdateStatus"
        @page-change="handlePageChange"
      />
    </Card>

    <!-- User Profile Modal -->
    <UserProfileModal
      :show="showUserModal"
      :user="selectedUser"
      :loading="loading"
      @update:show="showUserModal = $event"
      @close="showUserModal = false"
      @update-status="handleUpdateStatus"
    />
  </div>
</template>

