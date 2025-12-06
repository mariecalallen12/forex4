<template>
  <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-4">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-shield-alt mr-2 text-purple-400"></i>
      Risk Management
    </h3>
    
    <div class="space-y-4">
      <!-- Margin Level -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-400">Margin Level</span>
          <span :class="['text-lg font-bold', marginLevel >= 200 ? 'text-green-400' : 'text-yellow-400']">
            {{ marginLevel }}%
          </span>
        </div>
        <div class="h-2 bg-slate-600 rounded-full overflow-hidden">
          <div
            :class="['h-full transition-all', marginLevel >= 200 ? 'bg-green-500' : 'bg-yellow-500']"
            :style="{ width: `${Math.min(marginLevel, 100)}%` }"
          ></div>
        </div>
      </div>

      <!-- Position Sizing -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="text-sm text-gray-400 mb-2">Position Sizing</div>
        <div class="text-xs text-gray-400">Automated position management</div>
      </div>

      <!-- Stop Loss Automation -->
      <div class="bg-slate-700/30 rounded-lg p-4">
        <div class="text-sm text-gray-400 mb-2">Stop Loss Automation</div>
        <div class="text-xs text-gray-400">Trailing stop enabled</div>
      </div>

      <!-- Risk Alerts -->
      <div class="bg-red-500/20 border border-red-500/30 rounded-lg p-3">
        <div class="text-sm text-red-400 font-bold mb-1">Risk Alerts</div>
        <div class="text-xs text-gray-300">No active alerts</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const marginLevel = ref(250);
</script>

