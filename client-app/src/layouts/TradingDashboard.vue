<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
    <!-- Header Navigation -->
    <TradingHeader />
    
    <!-- Main Trading Dashboard Layout -->
    <div class="container mx-auto px-2 sm:px-4 py-2 sm:py-4">
      <div class="grid grid-cols-12 gap-2 sm:gap-4">
        <!-- Column 1: Market Watch (20%) -->
        <div class="col-span-12 lg:col-span-2 order-1 space-y-2 sm:space-y-4">
          <MarketWatchPanel />
          <!-- Additional Panels in Column 1 -->
          <RiskPanel />
        </div>
        
        <!-- Column 2: TradingView Chart (35%) -->
        <div class="col-span-12 lg:col-span-5 order-2 space-y-2 sm:space-y-4">
          <TradingViewChart />
          <!-- Analytics Panel below chart -->
          <AnalyticsPanel />
        </div>
        
        <!-- Column 3: Order Panel (25%) -->
        <div class="col-span-12 lg:col-span-3 order-3 space-y-2 sm:space-y-4">
          <OrderPanel />
          <!-- AI Trading Panel below order panel -->
          <AITradingPanel />
        </div>
        
        <!-- Column 4: Account Dashboard (20%) -->
        <div class="col-span-12 lg:col-span-2 order-4 space-y-2 sm:space-y-4">
          <AccountDashboard />
          <!-- Compliance Panel below account -->
          <CompliancePanel />
        </div>
      </div>
      
      <!-- Additional Panels Row -->
      <div class="grid grid-cols-12 gap-2 sm:gap-4 mt-2 sm:mt-4">
        <!-- Order History -->
        <div class="col-span-12 lg:col-span-4">
          <OrderHistoryPanel />
        </div>
        
        <!-- Trade History -->
        <div class="col-span-12 lg:col-span-4">
          <TradeHistoryPanel />
        </div>
        
        <!-- Order Book -->
        <div class="col-span-12 lg:col-span-4">
          <OrderBookPanel />
        </div>
      </div>
      
      <!-- Social Feed Section -->
      <div class="mt-2 sm:mt-4">
        <SocialFeedPanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import TradingHeader from '../components/layout/TradingHeader.vue';
import MarketWatchPanel from '../components/trading/MarketWatch/MarketWatchPanel.vue';
import TradingViewChart from '../components/trading/Chart/TradingViewChart.vue';
import OrderPanel from '../components/trading/OrderPanel/OrderPanel.vue';
import AccountDashboard from '../components/trading/AccountDashboard/AccountPanel.vue';
import SocialFeedPanel from '../components/trading/SocialFeed/SocialFeedPanel.vue';
import RiskPanel from '../components/trading/RiskManagement/RiskPanel.vue';
import AnalyticsPanel from '../components/trading/Analytics/AnalyticsPanel.vue';
import CompliancePanel from '../components/trading/Compliance/CompliancePanel.vue';
import AITradingPanel from '../components/trading/AITrading/AITradingPanel.vue';
import OrderHistoryPanel from '../components/trading/OrderHistory/OrderHistoryPanel.vue';
import TradeHistoryPanel from '../components/trading/TradeHistory/TradeHistoryPanel.vue';
import OrderBookPanel from '../components/trading/OrderBook/OrderBookPanel.vue';
import { useTradingStore } from '../stores/trading';
import { useWebSocketStore } from '../stores/websocket';

const tradingStore = useTradingStore();
const wsStore = useWebSocketStore();

onMounted(async () => {
  // Fetch initial data
  try {
    await Promise.all([
      tradingStore.fetchPositions(),
      tradingStore.fetchOrders(),
      tradingStore.fetchOrderHistory()
    ]);
  } catch (error) {
    console.error('Error fetching trading data:', error);
  }

  // Connect WebSocket if not already connected
  if (!wsStore.connected) {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    wsStore.connect(wsUrl);
  }
});
</script>

