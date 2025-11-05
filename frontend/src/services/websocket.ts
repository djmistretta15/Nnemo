/**
 * WebSocket client for real-time updates
 */

type MessageHandler = (message: any) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(userId: string, token: string) {
    const wsUrl = `ws://localhost:8000/ws/${userId}?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;

      // Subscribe to default topics
      this.send({ type: 'subscribe', topic: 'market' });
      this.send({ type: 'subscribe', topic: 'contracts' });
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(userId, token);
    };
  }

  private attemptReconnect(userId: string, token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

      setTimeout(() => {
        this.connect(userId, token);
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private handleMessage(message: any) {
    const { type } = message;
    const handlers = this.handlers.get(type);

    if (handlers) {
      handlers.forEach(handler => handler(message));
    }

    // Also trigger 'all' handlers
    const allHandlers = this.handlers.get('all');
    if (allHandlers) {
      allHandlers.forEach(handler => handler(message));
    }
  }

  subscribe(topic: string) {
    this.send({ type: 'subscribe', topic });
  }

  unsubscribe(topic: string) {
    this.send({ type: 'unsubscribe', topic });
  }

  ping() {
    this.send({ type: 'ping', timestamp: Date.now() });
  }
}

export const wsClient = new WebSocketClient();
export default wsClient;
