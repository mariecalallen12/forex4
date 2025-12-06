<script setup>
import { ref } from 'vue';
import Input from '../ui/Input.vue';
import Select from '../ui/Select.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({
      symbol: '',
      status: 'all',
      dateFrom: '',
      dateTo: '',
    }),
  },
});

const emit = defineEmits(['update:filters', 'search']);

const statusOptions = [
  { value: 'all', label: 'Tất cả' },
  { value: 'pending', label: 'Chờ phê duyệt' },
  { value: 'approved', label: 'Đã phê duyệt' },
  { value: 'rejected', label: 'Đã từ chối' },
];

const symbolOptions = [
  { value: '', label: 'Tất cả' },
  { value: 'BTC/USD', label: 'BTC/USD' },
  { value: 'ETH/USD', label: 'ETH/USD' },
  { value: 'EUR/USD', label: 'EUR/USD' },
  { value: 'GBP/USD', label: 'GBP/USD' },
];

const localFilters = ref({ ...props.filters });

const updateFilter = (key, value) => {
  localFilters.value[key] = value;
  emit('update:filters', { ...localFilters.value });
};

const handleSearch = () => {
  emit('search', localFilters.value);
};
</script>

<template>
  <div class="glass-effect rounded-xl p-4 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <Select
        v-model="localFilters.symbol"
        :options="symbolOptions"
        placeholder="Lọc theo Symbol"
        @update:model-value="updateFilter('symbol', $event)"
      />
      <Select
        v-model="localFilters.status"
        :options="statusOptions"
        placeholder="Lọc theo trạng thái"
        @update:model-value="updateFilter('status', $event)"
      />
      <Input
        v-model="localFilters.dateFrom"
        type="date"
        placeholder="Từ ngày"
        @update:model-value="updateFilter('dateFrom', $event)"
      />
      <Input
        v-model="localFilters.dateTo"
        type="date"
        placeholder="Đến ngày"
        @update:model-value="updateFilter('dateTo', $event)"
      />
      <Button variant="primary" @click="handleSearch" icon="fas fa-search">
        Tìm kiếm
      </Button>
    </div>
  </div>
</template>

<style scoped>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

