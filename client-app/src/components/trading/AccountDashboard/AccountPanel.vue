<template>
  <div class="space-y-4">
    <!-- Account Balance Card -->
    <BalanceCard />
    
    <!-- Open Positions -->
    <PositionsList />
    
    <!-- Quick Actions -->
    <QuickActions />
  </div>
</template>

<script setup>
import BalanceCard from './BalanceCard.vue';
import PositionsList from './PositionsList.vue';
import QuickActions from './QuickActions.vue';
</script>

