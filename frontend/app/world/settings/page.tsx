"use client";

import { useState, useEffect } from "react";
import WorldHealth from "@/components/WorldHealth";
import ControlToggle from "@/components/ControlToggle";
import ControlSlider from "@/components/ControlSlider";
import DangerZone from "@/components/DangerZone";
import { Sliders } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function ControlPage() {
    const [systemActive, setSystemActive] = useState(true);
    const [autoEvolution, setAutoEvolution] = useState(true);
    const [tickRate, setTickRate] = useState(1.2);
    const [maxAgents, setMaxAgents] = useState(12);
    const [strictMode, setStrictMode] = useState(false);
    const [sandboxed, setSandboxed] = useState(true);
    const [loading, setLoading] = useState(false);

    // Load current settings
    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/world/control/settings`);
            const data = await response.json();
            setSystemActive(data.is_running ?? true);
            setMaxAgents(data.max_agents ?? 12);
            setTickRate(data.tick_rate || 1.2);
            setAutoEvolution(data.auto_evolution ?? true);
            setStrictMode(data.strict_mode ?? false);
            setSandboxed(data.sandboxed ?? true);
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    };

    const handleSystemToggle = async (value: boolean) => {
        setLoading(true);
        try {
            const endpoint = value ? '/api/world/control/resume' : '/api/world/control/pause';
            const response = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
            if (response.ok) {
                setSystemActive(value);
            }
        } catch (error) {
            console.error('Failed to toggle system:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAutoEvolution = async (value: boolean) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/api/world/control/set-auto-evolution`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value })
            });
            if (response.ok) setAutoEvolution(value);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleTickRateChange = async (value: number) => {
        setTickRate(value); // Optimistic update
        try {
            const response = await fetch(`${API_BASE}/api/world/control/set-tick`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tick_rate: value })
            });
            if (!response.ok) console.error("Failed to set tick rate");
        } catch (e) {
            console.error(e);
        }
    };

    const handleMaxAgentsChange = async (value: number) => {
        setMaxAgents(value); // Optimistic update
        try {
            const response = await fetch(`${API_BASE}/api/world/control/set-max-agents`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ max_agents: value })
            });
            if (!response.ok) console.error("Failed to set max agents");
        } catch (e) {
            console.error(e);
        }
    };

    const handleStrictMode = async (value: boolean) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/api/world/control/set-strict-mode`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value })
            });
            if (response.ok) setStrictMode(value);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleSandboxed = async (value: boolean) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/api/world/control/set-sandboxed`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value })
            });
            if (response.ok) setSandboxed(value);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center gap-3">
                <Sliders className="h-8 w-8 text-primary" />
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">System Control</h2>
                    <p className="text-muted-foreground">Orchestrate world parameters</p>
                </div>
            </div>

            <WorldHealth />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Controls Column */}
                <div className="space-y-6">
                    <div className="rounded-xl border bg-card p-6 space-y-6">
                        <h3 className="font-semibold">Sim Parameters</h3>

                        <ControlToggle
                            label="System Active"
                            description="Master switch for the entire kernel loop."
                            checked={systemActive}
                            onChange={handleSystemToggle}
                        />

                        <div className="h-px bg-border" />

                        <ControlToggle
                            label="Auto-Evolution"
                            description="Allow system to spawn new agents autonomously."
                            checked={autoEvolution}
                            onChange={handleAutoEvolution}
                        />

                        <div className="h-px bg-border" />

                        <ControlSlider
                            label="Tick Rate"
                            value={tickRate}
                            min={0.1}
                            max={5.0}
                            unit=" Hz"
                            onChange={handleTickRateChange}
                        />

                        <ControlSlider
                            label="Max Agents"
                            value={maxAgents}
                            min={2}
                            max={50}
                            onChange={handleMaxAgentsChange}
                        />
                    </div>

                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-4">Governance Overrides</h3>
                        <div className="space-y-4">
                            <ControlToggle
                                label="Strict Mode"
                                description="Require super-majority (75%) for all legislative decisions."
                                checked={strictMode}
                                onChange={handleStrictMode}
                            />
                            <ControlToggle
                                label="Sandboxed Execution"
                                description="Prevent agents from accessing external networks."
                                checked={sandboxed}
                                onChange={handleSandboxed}
                            />
                        </div>
                    </div>
                </div>

                {/* Danger Column */}
                <div className="space-y-6">
                    <DangerZone />

                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-2">Debug Tools</h3>
                        <p className="text-sm text-muted-foreground mb-4">Advanced debugging and monitoring</p>
                        <div className="space-y-2">
                            <button
                                onClick={() => window.open(`${API_BASE}/docs`, '_blank')}
                                className="w-full px-4 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded-lg transition-colors"
                            >
                                Open API Documentation
                            </button>
                            <button
                                onClick={loadSettings}
                                className="w-full px-4 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded-lg transition-colors"
                            >
                                Refresh Settings
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {loading && (
                <div className="fixed bottom-4 right-4 bg-card border rounded-lg p-4 shadow-lg">
                    <p className="text-sm">Updating settings...</p>
                </div>
            )}
        </div>
    );
}
