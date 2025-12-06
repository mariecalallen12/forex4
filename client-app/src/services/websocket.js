class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.subscribers = new Map();
    this.eventListeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000; // 30 seconds max
    this.messageQueue = [];
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
    this.heartbeatIntervalMs = 30000; // 30 seconds
    this.heartbeatTimeoutMs = 10000; // 10 seconds timeout
    this.isManualDisconnect = false;
    this.reconnectTimer = null;
  }

  connect(url = import.meta.env.VITE_WS_URL || window.location.origin) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.isManualDisconnect = false;
    
    // Convert http/https to ws/wss
    let wsUrl = url;
    if (wsUrl.startsWith('http://')) {
      wsUrl = wsUrl.replace('http://', 'ws://');
    } else if (wsUrl.startsWith('https://')) {
      wsUrl = wsUrl.replace('https://', 'wss://');
    }
    
    // Add token to query params
    const token = localStorage.getItem('auth_token');
    const separator = wsUrl.includes('?') ? '&' : '?';
    wsUrl = `${wsUrl}/ws${separator}token=${encodeURIComponent(token || '')}`;
    
    // Add channels to subscribe
    wsUrl += '&channels=orders,positions,prices';
    
    try {
      this.socket = new WebSocket(wsUrl);
      this.setupEventHandlers();
      this.startHeartbeat();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.emit('error', { type: 'connection_error', error });
      this.scheduleReconnect();
    }
  }

  setupEventHandlers() {
    this.socket.onopen = () => {
      this.connected = true;
      this.reconnectAttempts = 0;
      console.log('WebSocket connected');
      this.emit('connected', { status: 'connected' });
      
      // Process queued messages
      this.processMessageQueue();
    };

    this.socket.onclose = (event) => {
      this.connected = false;
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.stopHeartbeat();
      this.emit('disconnected', { status: 'disconnected', code: event.code, reason: event.reason });
      
      // Auto-reconnect if not manual disconnect and not normal closure
      if (!this.isManualDisconnect && event.code !== 1000) {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', { type: 'socket_error', error });
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle different message types
        if (message.type === 'connected') {
          console.log('WebSocket handshake complete');
        } else if (message.type === 'pong') {
          // Clear heartbeat timeout on pong
          if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
          }
        } else if (message.type === 'ping') {
          // Respond to ping
          this.send({ type: 'pong' });
        } else if (message.type === 'order_update') {
          this.handleOrderUpdate(message);
        } else if (message.type === 'position_update') {
          this.handlePositionUpdate(message);
        } else if (message.type === 'price_update') {
          this.handlePriceUpdate(message);
        } else if (message.channel === 'orders') {
          this.handleOrderUpdate(message);
        } else if (message.channel === 'positions') {
          this.handlePositionUpdate(message);
        } else if (message.channel === 'prices') {
          this.handlePriceUpdate(message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      this.messageQueue.push({ data, timestamp: Date.now() });
    }
  }

  handleOrderUpdate(message) {
    const callbacks = this.subscribers.get('orders');
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  handlePositionUpdate(message) {
    const callbacks = this.subscribers.get('positions');
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  handleAccountUpdate(data) {
    const callbacks = this.subscribers.get('account');
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handleNewsUpdate(data) {
    const callbacks = this.subscribers.get('news');
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handleIndicatorsUpdate(data) {
    const callbacks = this.subscribers.get('indicators');
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  disconnect() {
    this.isManualDisconnect = true;
    this.stopHeartbeat();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      this.socket.close(1000, 'Manual disconnect');
      this.socket = null;
      this.connected = false;
    }
    
    this.messageQueue = [];
    this.reconnectAttempts = 0;
  }

  subscribe(channel, callback) {
    const key = channel;
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, new Set());
    }

    this.subscribers.get(key).add(callback);
    
    // Send subscribe message if connected
    if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.send({
        type: 'subscribe',
        channels: [channel]
      });
    }
  }

  unsubscribe(channel, callback) {
    const key = channel;
    if (this.subscribers.has(key)) {
      this.subscribers.get(key).delete(callback);
      
      if (this.subscribers.get(key).size === 0) {
        this.subscribers.delete(key);
      }
    }
  }

  handleMarketData(data) {
    const callbacks = this.subscribers.get(data.instrument);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  handlePriceUpdate(message) {
    // Handle price updates for 'prices' channel
    const priceCallbacks = this.subscribers.get('prices');
    if (priceCallbacks) {
      priceCallbacks.forEach(callback => callback(message));
    }
    
    // Also handle by symbol if data contains symbol
    if (message.data && message.data.symbol) {
      const symbolCallbacks = this.subscribers.get(message.data.symbol);
      if (symbolCallbacks) {
        symbolCallbacks.forEach(callback => callback(message));
      }
    }
  }

  emit(event, data) {
    // For compatibility, map emit to send
    this.send({ type: event, ...data });
  }

  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).delete(callback);
    }
  }

  // Heartbeat mechanism
  startHeartbeat() {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
        
        // Set timeout for pong response
        this.heartbeatTimeout = setTimeout(() => {
          console.warn('WebSocket heartbeat timeout, reconnecting...');
          if (this.socket) {
            this.socket.close();
          }
          this.scheduleReconnect();
        }, this.heartbeatTimeoutMs);
      }
    }, this.heartbeatIntervalMs);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  // Exponential backoff reconnection
  scheduleReconnect() {
    if (this.isManualDisconnect || this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );

    console.log(`Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      // Recreate connection
      const url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
      this.connect(url);
      
      if (this.reconnectAttempts > 0) {
        this.emit('reconnected', { attempts: this.reconnectAttempts });
      }
    }, delay);
  }

  // Process queued messages
  processMessageQueue() {
    if (this.messageQueue.length === 0) {
      return;
    }

    console.log(`Processing ${this.messageQueue.length} queued messages`);
    
    const messages = [...this.messageQueue];
    this.messageQueue = [];
    
    messages.forEach(({ data }) => {
      if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send(data);
      } else {
        // Re-queue if still not connected
        this.messageQueue.push({ data, timestamp: Date.now() });
      }
    });
  }
}

export default new WebSocketService();
