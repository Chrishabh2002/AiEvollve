"use client";

import { useEffect, useState } from "react";
import { wsManager } from "@/lib/ws";
import { worldStore } from "@/lib/worldStore";

export function useWorldStream() {
    // We can expose specific parts of state here if we want
    // But primarily this hook ensures connection is alive

    useEffect(() => {
        // 1. Connect WS
        wsManager.connect();

        // 2. Bind WS to Store
        const cleanupListener = wsManager.addListener((event) => {
            worldStore.processEvent(event);
        });

        return () => {
            cleanupListener();
        };
    }, []);
}
