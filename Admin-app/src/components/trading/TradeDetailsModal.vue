<script setup>
import Modal from '../ui/Modal.vue';
import Card from '../ui/Card.vue';
import Badge from '../ui/Badge.vue';
import Button from '../ui/Button.vue';

const props = defineProps({
  show: Boolean,
  trade: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'update:show', 'approve', 'reject']);

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
</script>

<template>
  <Modal
    :show="show"
    title="Chi tiết giao dịch"
    size="lg"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div v-if="trade" class="space-y-4">
      <!-- Trade Info -->
      <div class="grid grid-cols-2 gap-4">
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Trade ID</p>
          <p class="text-white font-mono font-semibold">{{ trade.trade_id || trade.id }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">User ID</p>
          <p class="text-white font-semibold">{{ trade.user_id }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Symbol</p>
          <p class="text-white font-semibold text-lg">{{ trade.symbol }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Side</p>
          <p :class="['font-semibold text-lg', getSideColor(trade.side)]">
            {{ trade.side === 'buy' ? 'Mua' : 'Bán' }}
          </p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Type</p>
          <p class="text-white font-semibold">{{ trade.type || 'Market' }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Status</p>
          <Badge :type="getStatusType(trade.status)">
            {{ trade.status }}
          </Badge>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Quantity</p>
          <p class="text-white font-semibold text-lg">{{ trade.quantity }}</p>
        </Card>
        <Card padding="p-4">
          <p class="text-white/60 text-sm mb-1">Price</p>
          <p class="text-white font-semibold text-lg">${{ trade.price?.toLocaleString() }}</p>
        </Card>
        <Card padding="p-4" class="col-span-2">
          <p class="text-white/60 text-sm mb-1">Total Value</p>
          <p class="text-white font-bold text-2xl">${{ trade.value?.toLocaleString() }}</p>
        </Card>
      </div>

      <!-- Actions -->
      <div v-if="trade.status === 'pending'" class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Đóng</Button>
        <Button variant="danger" @click="emit('reject')">
          <i class="fas fa-times mr-2"></i>
          Từ chối
        </Button>
        <Button variant="primary" @click="emit('approve')">
          <i class="fas fa-check mr-2"></i>
          Phê duyệt
        </Button>
      </div>
      <div v-else class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Đóng</Button>
      </div>
    </div>
  </Modal>
</template>

