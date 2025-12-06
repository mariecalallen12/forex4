import { defineStore } from 'pinia';
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { tradingApi } from '../services/api/trading';
import { useWebSocketStore } from './websocket';

export const useTradingStore = defineStore('trading', () => {
  const orders = ref([]);
  const openPositions = ref([]); // Removed mock data - will be fetched from API
  const orderHistory = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const statistics = ref(null);

  const totalPnl = computed(() => {
    return openPositions.value.reduce((sum, pos) => sum + (pos.unrealizedPnl || pos.pnl || 0), 0);
  });

  async function placeOrder(orderData) {
    isLoading.value = true;
    error.value = null;
    
    try {
      // Map frontend format to backend format
      const backendOrderData = {
        symbol: orderData.symbol,
        side: orderData.side,
        type: orderData.type || 'market',
        quantity: orderData.quantity,
        price: orderData.price,
        stop_price: orderData.stopPrice,
        leverage: orderData.leverage || 1,
        stop_loss: orderData.stopLoss,
        take_profit: orderData.takeProfit,
        margin: orderData.margin
      };
      
      const response = await tradingApi.placeOrder(backendOrderData);
      
      // Refresh orders and positions after placing order
      await fetchOrders();
      if (response.status === 'filled' || response.status === 'FILLED') {
        await fetchPositions();
      }
      
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to place order';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function closePosition(positionId) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.closePosition(positionId);
      openPositions.value = openPositions.value.filter(pos => pos.id !== positionId);
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to close position';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function cancelOrder(orderId) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.cancelOrder(orderId);
      // Refresh orders after cancellation
      await fetchOrders();
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to cancel order';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchOrders(filters = {}) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.getOrders(filters);
      // Handle nested response structure
      if (response.orders) {
        orders.value = response.orders.map(order => ({
          id: order.id,
          symbol: order.symbol,
          side: order.side,
          type: order.type,
          quantity: order.quantity,
          price: order.price,
          status: order.status,
          executed_quantity: order.executed_quantity || 0,
          executed_price: order.executed_price || 0,
          filled_amount: order.filled_amount || 0,
          fee: order.fee || 0,
          create_time: order.create_time,
          update_time: order.update_time
        }));
      } else if (Array.isArray(response)) {
        orders.value = response;
      }
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch orders';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchPositions(symbol = null) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.getPositions(symbol);
      // Handle nested response structure
      if (response.positions) {
        openPositions.value = response.positions.map(pos => ({
          id: pos.id,
          symbol: pos.symbol,
          side: pos.side,
          quantity: pos.quantity,
          entryPrice: pos.entry_price,
          currentPrice: pos.current_price,
          unrealizedPnl: pos.unrealized_pnl || 0,
          realizedPnl: pos.realized_pnl || 0,
          leverage: pos.leverage || 1,
          margin: pos.margin || 0,
          status: pos.status,
          createTime: pos.create_time
        }));
      } else if (Array.isArray(response)) {
        openPositions.value = response;
      }
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch positions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchOrderHistory(filters = {}) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.getOrderHistory(filters);
      // Handle nested response structure
      if (response.orders) {
        orderHistory.value = response.orders;
      } else if (Array.isArray(response)) {
        orderHistory.value = response;
      }
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch order history';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchStatistics() {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.getStatistics();
      statistics.value = response;
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch statistics';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchRiskAssessment() {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await tradingApi.getRiskAssessment();
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to fetch risk assessment';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // WebSocket integration for real-time updates
  const wsStore = useWebSocketStore();
  
  function setupWebSocketListeners() {
    // Listen for order updates
    wsStore.subscribe('orders', (message) => {
      if (message.type === 'order_update' && message.data) {
        const orderData = message.data;
        const orderId = orderData.id || orderData.order_id;
        const index = orders.value.findIndex(o => String(o.id) === String(orderId));
        if (index !== -1) {
          orders.value[index] = { ...orders.value[index], ...orderData };
        } else {
          orders.value.push(orderData);
        }
      }
    });

    // Listen for position updates
    wsStore.subscribe('positions', (message) => {
      if (message.type === 'position_update' && message.data) {
        const positionData = message.data;
        const positionId = positionData.id || positionData.position_id;
        const index = openPositions.value.findIndex(p => String(p.id) === String(positionId));
        if (index !== -1) {
          openPositions.value[index] = { ...openPositions.value[index], ...positionData };
        } else if (!positionData.is_closed && positionData.status !== 'closed') {
          openPositions.value.push(positionData);
        }
      }
    });

    // Listen for price updates
    wsStore.subscribe('prices', (message) => {
      if (message.type === 'price_update' && message.data) {
        const { symbol, price } = message.data;
        // Update current price in positions
        openPositions.value.forEach(pos => {
          if (pos.symbol === symbol) {
            pos.currentPrice = price;
            // Recalculate PnL
            if (pos.side === 'long' || pos.side === 'buy') {
              pos.unrealizedPnl = (price - pos.entryPrice) * pos.quantity;
            } else {
              pos.unrealizedPnl = (pos.entryPrice - price) * pos.quantity;
            }
          }
        });
      }
    });
  }

  // Setup WebSocket on store initialization
  if (typeof window !== 'undefined') {
    setupWebSocketListeners();
  }

  return {
    orders,
    openPositions,
    orderHistory,
    statistics,
    isLoading,
    error,
    totalPnl,
    placeOrder,
    closePosition,
    cancelOrder,
    fetchOrders,
    fetchPositions,
    fetchOrderHistory,
    fetchStatistics,
    fetchRiskAssessment,
    setupWebSocketListeners,
  };
});

