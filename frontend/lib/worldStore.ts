import { WorldEvent } from "./events";

// Simple in-memory store for global state cache
// Components can subscribe to changes here to avoid prop drilling or complex context

interface WorldState {
    tick: number;
    messages: any[]; // Using any for brevity in store, mapped to API schemas really
    decisions: any[];
    plans_count: number;
}

// Initial State
let currentState: WorldState = {
    tick: 0,
    messages: [],
    decisions: [],
    plans_count: 0
};

type StoreListener = (state: WorldState) => void;
const listeners: StoreListener[] = [];

export const worldStore = {
    getState: () => currentState,

    subscribe: (listener: StoreListener) => {
        listeners.push(listener);
        return () => {
            const index = listeners.indexOf(listener);
            if (index > -1) listeners.splice(index, 1);
        };
    },

    // This handles incoming WS events and updates state
    processEvent: (event: WorldEvent) => {
        let hasChanged = false;

        switch (event.type) {
            case "TICK":
                currentState.tick = event.payload.tick;
                hasChanged = true;
                break;
            case "AGENT_MESSAGE":
                // Prepend new message
                currentState.messages = [
                    {
                        id: event.payload.id,
                        agent_id: event.payload.agent,
                        content: event.payload.content,
                        timestamp: new Date().toISOString() // Local timestamp if server timestamp is numeric
                    },
                    ...currentState.messages
                ].slice(0, 50); // Keep last 50
                hasChanged = true;
                break;
            case "PLAN_UPDATE":
                currentState.plans_count = event.payload.count;
                hasChanged = true;
                break;
            case "DECISION_CREATED":
                // Just invalidating or adding simple notification could be enough
                // For now let's just log it or maybe add to a 'recent events' list
                // We'll leave it as a no-op update for global tick for now
                hasChanged = true;
                break;
        }

        if (hasChanged) {
            listeners.forEach(cb => cb(currentState));
        }
    }
};
