<template>
  <div class="bg-slate-700/30 rounded-lg p-3">
    <div class="text-sm text-white mb-2">{{ item.content }}</div>
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <button class="flex items-center space-x-1 text-gray-400 hover:text-purple-400 transition-colors">
          <i class="fas fa-heart"></i>
          <span>{{ item.likes }}</span>
        </button>
        <button class="flex items-center space-x-1 text-gray-400 hover:text-purple-400 transition-colors">
          <i class="fas fa-comment"></i>
          <span>{{ item.comments }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true,
  },
});
</script>

