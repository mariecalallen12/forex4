<template>
  <div class="flex space-x-2 mb-4">
    <button
      v-for="filter in filters"
      :key="filter.value"
      @click="$emit('update:modelValue', filter.value)"
      :class="[
        'px-3 py-1 rounded-lg text-sm font-medium transition-all',
        modelValue === filter.value
          ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
          : 'bg-slate-700/50 text-purple-200 hover:bg-slate-700'
      ]"
    >
      {{ filter.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: 'all',
  },
});

defineEmits(['update:modelValue']);

const filters = [
  { value: 'all', label: 'Tất cả' },
  { value: 'forex', label: 'Forex' },
  { value: 'crypto', label: 'Crypto' },
  { value: 'commodity', label: 'Hàng hóa' },
  { value: 'derivatives', label: 'Phái sinh' },
];
</script>

