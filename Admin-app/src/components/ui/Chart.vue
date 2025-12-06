<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'pie', 'doughnut'].includes(value),
  },
  data: {
    type: Object,
    default: () => ({}),
  },
  options: {
    type: Object,
    default: () => ({}),
  },
  height: {
    type: String,
    default: '300px',
  },
});

const chartRef = ref(null);
const chartInstance = ref(null);

onMounted(() => {
  // Placeholder for Chart.js integration
  // This will be implemented when Chart.js is added
  if (chartRef.value) {
    // TODO: Initialize Chart.js here
    console.log('Chart placeholder initialized', props.type, props.data);
  }
});

watch(
  () => [props.data, props.options],
  () => {
    if (chartInstance.value) {
      // TODO: Update chart
      chartInstance.value.update();
    }
  },
  { deep: true }
);
</script>

<template>
  <div
    ref="chartRef"
    :style="{ height }"
    class="w-full flex items-center justify-center bg-white/5 rounded-lg p-4"
  >
    <!-- Placeholder for chart -->
    <div class="text-center text-white/40">
      <i class="fas fa-chart-line text-4xl mb-2"></i>
      <p class="text-sm">Chart sẽ được tích hợp Chart.js</p>
      <p class="text-xs mt-1">Type: {{ type }}</p>
    </div>
  </div>
</template>

