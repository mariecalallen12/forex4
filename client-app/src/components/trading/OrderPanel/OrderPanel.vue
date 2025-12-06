<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4 h-full flex flex-col">
    <!-- Order Type Tabs -->
    <div class="flex space-x-2 mb-4 overflow-x-auto">
      <button
        v-for="tab in orderTabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        :class="[
          'px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
          activeTab === tab.value
            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
            : 'bg-slate-700/50 text-purple-200 hover:bg-slate-700'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Order Form Component -->
    <component :is="currentOrderComponent" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import SpotTrading from './OrderTypes/SpotTrading.vue';
import OptionsTrading from './OrderTypes/OptionsTrading.vue';
import FuturesTrading from './OrderTypes/FuturesTrading.vue';
import CopyTrading from './OrderTypes/CopyTrading.vue';
import AITrading from './OrderTypes/AITrading.vue';
import SocialTrading from './OrderTypes/SocialTrading.vue';
import DerivativesTrading from './OrderTypes/DerivativesTrading.vue';
import MultiCurrencyTrading from './OrderTypes/MultiCurrencyTrading.vue';

const activeTab = ref('spot');

const orderTabs = [
  { value: 'spot', label: 'Spot' },
  { value: 'options', label: 'Option' },
  { value: 'futures', label: 'Future' },
  { value: 'copy', label: 'Copy' },
  { value: 'ai', label: 'AI' },
  { value: 'social', label: 'Social' },
  { value: 'derivatives', label: 'Derivatives' },
  { value: 'multicurrency', label: 'Multi-Currency' },
];

const orderComponents = {
  spot: SpotTrading,
  options: OptionsTrading,
  futures: FuturesTrading,
  copy: CopyTrading,
  ai: AITrading,
  social: SocialTrading,
  derivatives: DerivativesTrading,
  multicurrency: MultiCurrencyTrading,
};

const currentOrderComponent = computed(() => {
  return orderComponents[activeTab.value] || SpotTrading;
});
</script>

