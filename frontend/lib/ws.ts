import { WorldEvent } from "./events";

type MessageCallback = (event: WorldEvent) => void;

class WSManager {
    private socket: WebSocket | null = null;
    private url: string;
    private listeners: MessageCallback[] = [];
    private reconnectTimeout: NodeJS.Timeout | null = null;
    private isConnected = false;

    constructor(url: string = "ws://localhost:8000/ws/world") {
        this.url = url;
    }

    public connect() {
        if (this.socket || this.isConnected) return;

        console.log(`📡 Connecting to World Stream: ${this.url}`);
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => {
            console.log("✅ World Stream Connected");
            this.isConnected = true;
            if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
        };

        this.socket.onmessage = (msg) => {
            try {
                const event: WorldEvent = JSON.parse(msg.data);
                this.notify(event);
            } catch (e) {
                console.error("❌ Failed to parse WS message", e);
            }
        };

        this.socket.onclose = () => {
            console.log("⚠️ World Stream Disconnected. Reconnecting in 3s...");
            this.isConnected = false;
            this.socket = null;
            this.reconnectTimeout = setTimeout(() => this.connect(), 3000);
        };

        this.socket.onerror = (err) => {
            // Silently handle WS errors - they're usually connection issues
            // that will be resolved by auto-reconnect
            if (this.isConnected) {
                console.warn("⚠️ WS connection issue, will auto-reconnect");
            }
            // Don't log error details to avoid console spam
        };
    }

    public addListener(cb: MessageCallback) {
        this.listeners.push(cb);
        return () => {
            this.listeners = this.listeners.filter(l => l !== cb);
        };
    }

    private notify(event: WorldEvent) {
        this.listeners.forEach(cb => cb(event));
    }
}

// Global Singleton
export const wsManager = new WSManager();
