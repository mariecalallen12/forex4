<template>
  <div class="flex space-x-2">
    <button
      v-for="tf in timeframes"
      :key="tf.value"
      @click="$emit('update:modelValue', tf.value)"
      :class="[
        'px-3 py-1 rounded-lg text-xs font-medium transition-all',
        modelValue === tf.value
          ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
          : 'bg-slate-700/50 text-purple-200 hover:bg-slate-700'
      ]"
    >
      {{ tf.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: '1H',
  },
});

defineEmits(['update:modelValue']);

const timeframes = [
  { value: '1M', label: '1M' },
  { value: '5M', label: '5M' },
  { value: '1H', label: '1H' },
  { value: '1D', label: '1D' },
];
</script>

