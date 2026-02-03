"use client";

import { useEffect, useState } from "react";
import { Activity, ShieldCheck, Zap, AlertTriangle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function WorldHealth() {
    const [metrics, setMetrics] = useState({
        stability: 98.2,
        chaos: "LOW",
        decision_success: 94,
        decision_count: 12,
        load_balance: "Optimal",
        tick: 0
    });

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/world/health`);
                if (res.ok) {
                    const data = await res.json();
                    setMetrics({
                        stability: 100 - (data.agent_count * 0.5), // Dummy calc based on real data
                        chaos: data.status === 'RUNNING' ? "LOW" : "PAUSED",
                        decision_success: data.decision_count > 0 ? 100 : 0,
                        decision_count: data.decision_count,
                        load_balance: data.agent_count > 10 ? "High Load" : "Optimal",
                        tick: data.tick
                    });
                }
            } catch (e) {
                console.error("Failed to fetch health metrics", e);
            }
        };

        fetchHealth();
        const interval = setInterval(fetchHealth, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border bg-card p-6 flex flex-col justify-between">
                <div className="flex items-center justify-between text-muted-foreground mb-4">
                    <span className="text-sm font-medium">Stability Score</span>
                    <ShieldCheck className="h-4 w-4 text-green-500" />
                </div>
                <div className="text-3xl font-bold">{metrics.stability.toFixed(1)}%</div>
                <div className="text-xs text-green-500 mt-1">Tick: {metrics.tick}</div>
            </div>

            <div className="rounded-xl border bg-card p-6 flex flex-col justify-between">
                <div className="flex items-center justify-between text-muted-foreground mb-4">
                    <span className="text-sm font-medium">Chaos Level</span>
                    <Activity className={`h-4 w-4 ${metrics.chaos === 'LOW' ? 'text-blue-500' : 'text-amber-500'}`} />
                </div>
                <div className={`text-3xl font-bold ${metrics.chaos === 'LOW' ? 'text-blue-500' : 'text-amber-500'}`}>
                    {metrics.chaos}
                </div>
                <div className="text-xs text-muted-foreground mt-1">Variance nominal</div>
            </div>

            <div className="rounded-xl border bg-card p-6 flex flex-col justify-between">
                <div className="flex items-center justify-between text-muted-foreground mb-4">
                    <span className="text-sm font-medium">Decisions</span>
                    <Zap className="h-4 w-4 text-amber-500" />
                </div>
                <div className="text-3xl font-bold">{metrics.decision_success}%</div>
                <div className="text-xs text-muted-foreground mt-1">{metrics.decision_count} total decisions</div>
            </div>

            <div className="rounded-xl border bg-card p-6 flex flex-col justify-between">
                <div className="flex items-center justify-between text-muted-foreground mb-4">
                    <span className="text-sm font-medium">Load Balance</span>
                    <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="text-3xl font-bold">{metrics.load_balance}</div>
                <div className="text-xs text-muted-foreground mt-1">System Status</div>
            </div>
        </div>
    );
}
