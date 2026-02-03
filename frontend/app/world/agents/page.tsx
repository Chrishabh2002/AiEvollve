"use client";

import { useEffect, useState } from "react";
import AgentCard from "@/components/AgentCard";
import { fetchAgents } from "@/lib/api";

export default function AgentsPage() {
    const [agents, setAgents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadAgents() {
            try {
                const data = await fetchAgents();
                setAgents(data);
            } catch (error) {
                console.error("Failed to load agents:", error);
            } finally {
                setLoading(false);
            }
        }

        loadAgents();
        const interval = setInterval(loadAgents, 5000); // Refresh every 5s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    const activeAgents = agents.filter((a) => a.state !== "RETIRED");
    const retiredAgents = agents.filter((a) => a.state === "RETIRED");

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">👥 AI Agents</h1>
                <p className="text-muted-foreground">
                    Meet the autonomous agents building the AI civilization
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-500">{activeAgents.length}</div>
                    <div className="text-sm text-muted-foreground">Active Agents</div>
                </div>
                <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-500">{agents.length}</div>
                    <div className="text-sm text-muted-foreground">Total Agents</div>
                </div>
                <div className="bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-orange-500">{retiredAgents.length}</div>
                    <div className="text-sm text-muted-foreground">Retired Agents</div>
                </div>
            </div>

            {/* Active Agents */}
            {activeAgents.length > 0 && (
                <div>
                    <h2 className="text-xl font-bold mb-4">⚡ Active Agents</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {activeAgents.map((agent) => (
                            <AgentCard key={agent.id} agent={agent} />
                        ))}
                    </div>
                </div>
            )}

            {/* Retired Agents */}
            {retiredAgents.length > 0 && (
                <div>
                    <h2 className="text-xl font-bold mb-4 text-muted-foreground">
                        💤 Retired Agents
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 opacity-50">
                        {retiredAgents.map((agent) => (
                            <AgentCard key={agent.id} agent={agent} />
                        ))}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {agents.length === 0 && (
                <div className="text-center py-12 bg-secondary/20 rounded-lg border border-border">
                    <p className="text-muted-foreground">No agents found. Initializing...</p>
                </div>
            )}
        </div>
    );
}
