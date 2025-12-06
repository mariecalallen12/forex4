<script setup>
import Table from '../ui/Table.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  trades: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  pagination: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['view', 'approve', 'reject', 'page-change', 'sort']);

const headers = [
  { key: 'trade_id', label: 'Trade ID', sortable: true },
  { key: 'user_id', label: 'User ID', sortable: true },
  { key: 'symbol', label: 'Symbol', sortable: true },
  { key: 'side', label: 'Side', sortable: true },
  { key: 'type', label: 'Type', sortable: true },
  { key: 'quantity', label: 'Quantity', sortable: true },
  { key: 'price', label: 'Price', sortable: true },
  { key: 'value', label: 'Value', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'actions', label: 'Thao tác', sortable: false },
];

const getSideColor = (side) => {
  return side === 'buy' ? 'text-green-400' : 'text-red-400';
};

const getStatusType = (status) => {
  const statusMap = {
    pending: 'pending',
    approved: 'approved',
    rejected: 'rejected',
  };
  return statusMap[status] || 'default';
};

const getStatusText = (status) => {
  const textMap = {
    pending: 'Chờ phê duyệt',
    approved: 'Đã phê duyệt',
    rejected: 'Đã từ chối',
  };
  return textMap[status] || status;
};
</script>

<template>
  <Table
    :headers="headers"
    :data="trades"
    :loading="loading"
    :pagination="pagination"
    @page-change="emit('page-change', $event)"
    @sort="emit('sort', $event)"
  >
    <template #default="{ data }">
      <tr
        v-for="trade in data"
        :key="trade.id"
        class="border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <td class="px-4 py-3 text-white/80 text-sm font-mono">{{ trade.trade_id || trade.id }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ trade.user_id }}</td>
        <td class="px-4 py-3 text-white/80 text-sm font-semibold">{{ trade.symbol }}</td>
        <td :class="['px-4 py-3 text-sm font-semibold', getSideColor(trade.side)]">
          {{ trade.side === 'buy' ? 'Mua' : 'Bán' }}
        </td>
        <td class="px-4 py-3 text-white/60 text-sm">{{ trade.type || 'Market' }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">{{ trade.quantity }}</td>
        <td class="px-4 py-3 text-white/80 text-sm">${{ trade.price?.toLocaleString() }}</td>
        <td class="px-4 py-3 text-white font-semibold">${{ trade.value?.toLocaleString() }}</td>
        <td class="px-4 py-3">
          <Badge :type="getStatusType(trade.status)">
            {{ getStatusText(trade.status) }}
          </Badge>
        </td>
        <td class="px-4 py-3">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon="fas fa-eye"
              @click="emit('view', trade.id)"
            >
            </Button>
            <Button
              v-if="trade.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-check text-green-400"
              @click="emit('approve', trade.id)"
            >
            </Button>
            <Button
              v-if="trade.status === 'pending'"
              variant="ghost"
              size="sm"
              icon="fas fa-times text-red-400"
              @click="emit('reject', trade.id)"
            >
            </Button>
          </div>
        </td>
      </tr>
    </template>
  </Table>
</template>

