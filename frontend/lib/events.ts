export type EventType = "TICK" | "AGENT_MESSAGE" | "DECISION_CREATED" | "PLAN_UPDATE" | "EVOLUTION";

export interface TickEvent {
    type: "TICK";
    timestamp: number;
    payload: {
        tick: number;
    };
}

export interface AgentMessageEvent {
    type: "AGENT_MESSAGE";
    timestamp: number;
    payload: {
        agent: string;
        content: string;
        id: string;
    };
}

export interface DecisionEvent {
    type: "DECISION_CREATED";
    timestamp: number;
    payload: {
        id: string;
        topic: string;
        author: string;
    };
}

export interface PlanUpdateEvent {
    type: "PLAN_UPDATE";
    timestamp: number;
    payload: {
        count: number;
    };
}

export interface EvolutionEvent {
    type: "EVOLUTION";
    timestamp: number;
    payload: {
        id: string;
        reason: string;
        generation: number;
    };
}

export type WorldEvent = TickEvent | AgentMessageEvent | DecisionEvent | PlanUpdateEvent | EvolutionEvent;
