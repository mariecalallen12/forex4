import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import websocketService from '../services/websocket';

export const useWebSocketStore = defineStore('websocket', () => {
  const connected = ref(false);
  const reconnectAttempts = ref(0);
  const error = ref(null);

  const isConnected = computed(() => connected.value);

  function connect(url) {
    websocketService.connect(url);
    
    websocketService.on('connected', () => {
      connected.value = true;
      error.value = null;
      reconnectAttempts.value = 0;
    });

    websocketService.on('disconnected', () => {
      connected.value = false;
    });

    websocketService.on('reconnected', (data) => {
      connected.value = true;
      reconnectAttempts.value = data.attempts || 0;
    });

    websocketService.on('error', (err) => {
      error.value = err;
      connected.value = false;
    });
  }

  function disconnect() {
    websocketService.disconnect();
    connected.value = false;
  }

  function subscribe(instrument, callback) {
    websocketService.subscribe(instrument, callback);
  }

  function unsubscribe(instrument, callback) {
    websocketService.unsubscribe(instrument, callback);
  }

  return {
    connected,
    reconnectAttempts,
    error,
    isConnected,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
  };
});

