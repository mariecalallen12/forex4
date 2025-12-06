<script setup>
import Card from '../ui/Card.vue';
import Chart from '../ui/Chart.vue';

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      datasets: [
        {
          label: 'Trading Volume 24h',
          data: [120, 190, 300, 500, 200, 300, 450],
        },
      ],
    }),
  },
});
</script>

<template>
  <Card title="Khối lượng giao dịch 24h" subtitle="Biểu đồ khối lượng giao dịch trong 24 giờ qua">
    <Chart type="line" :data="data" height="300px" />
  </Card>
</template>

