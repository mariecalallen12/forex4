<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-users mr-2 text-purple-400"></i>
        Social Feed
      </h3>
    </div>

    <div class="space-y-4 max-h-64 overflow-y-auto">
      <FeedItem
        v-for="item in socialFeed"
        :key="item.id"
        :item="item"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import FeedItem from './FeedItem.vue';
import { useSocialStore } from '../../../stores/social';

const socialStore = useSocialStore();
const socialFeed = ref([]);

onMounted(async () => {
  await socialStore.fetchFeed();
  socialFeed.value = socialStore.feed;
});
</script>

