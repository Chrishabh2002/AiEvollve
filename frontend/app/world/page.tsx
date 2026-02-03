"use client";

import { useEffect, useState } from "react";
import WorldHealth from "@/components/WorldHealth";
import SystemStats from "@/components/SystemStats";
import ActivityPulse from "@/components/ActivityPulse";
import { fetchHealth, fetchAgents, fetchDecisions, fetchPlans } from "@/lib/api";
import { Users, Target, FileText, TrendingUp } from "lucide-react";

export default function WorldDashboard() {
    const [health, setHealth] = useState<any>(null);
    const [agents, setAgents] = useState<any[]>([]);
    const [decisions, setDecisions] = useState<any[]>([]);
    const [plans, setPlans] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                const [healthData, agentsData, decisionsData, plansData] = await Promise.all([
                    fetchHealth(),
                    fetchAgents(),
                    fetchDecisions(),
                    fetchPlans(),
                ]);

                setHealth(healthData);
                setAgents(agentsData);
                setDecisions(decisionsData);
                setPlans(plansData);
            } catch (error) {
                console.error("Failed to load dashboard data:", error);
            } finally {
                setLoading(false);
            }
        }

        loadData();
        const interval = setInterval(loadData, 5000); // Refresh every 5s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto"></div>
                    <p className="text-muted-foreground">Loading AI World...</p>
                </div>
            </div>
        );
    }

    const activeAgents = agents.filter((a) => a.state !== "RETIRED").length;
    const openDecisions = decisions.filter((d) => d.status === "VOTING" || d.status === "OPEN").length;
    const activePlans = plans.filter((p) => p.status === "ACTIVE").length;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold mb-2">🌍 AI World Dashboard</h1>
                <p className="text-muted-foreground">
                    Real-time overview of your autonomous AI civilization
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Active Agents */}
                <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-lg p-6 hover:shadow-lg transition-all duration-200">
                    <div className="flex items-center justify-between mb-4">
                        <Users className="w-8 h-8 text-blue-500" />
                        <span className="text-xs font-medium text-blue-500 bg-blue-500/10 px-2 py-1 rounded-full">
                            ACTIVE
                        </span>
                    </div>
                    <div className="text-3xl font-bold text-blue-500 mb-1">{activeAgents}</div>
                    <div className="text-sm text-muted-foreground">Active Agents</div>
                </div>

                {/* Open Decisions */}
                <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-lg p-6 hover:shadow-lg transition-all duration-200">
                    <div className="flex items-center justify-between mb-4">
                        <Target className="w-8 h-8 text-purple-500" />
                        <span className="text-xs font-medium text-purple-500 bg-purple-500/10 px-2 py-1 rounded-full">
                            VOTING
                        </span>
                    </div>
                    <div className="text-3xl font-bold text-purple-500 mb-1">{openDecisions}</div>
                    <div className="text-sm text-muted-foreground">Open Decisions</div>
                </div>

                {/* Active Plans */}
                <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-lg p-6 hover:shadow-lg transition-all duration-200">
                    <div className="flex items-center justify-between mb-4">
                        <FileText className="w-8 h-8 text-green-500" />
                        <span className="text-xs font-medium text-green-500 bg-green-500/10 px-2 py-1 rounded-full">
                            RUNNING
                        </span>
                    </div>
                    <div className="text-3xl font-bold text-green-500 mb-1">{activePlans}</div>
                    <div className="text-sm text-muted-foreground">Active Plans</div>
                </div>

                {/* System Tick */}
                <div className="bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20 rounded-lg p-6 hover:shadow-lg transition-all duration-200">
                    <div className="flex items-center justify-between mb-4">
                        <TrendingUp className="w-8 h-8 text-orange-500" />
                        <span className="text-xs font-medium text-orange-500 bg-orange-500/10 px-2 py-1 rounded-full">
                            LIVE
                        </span>
                    </div>
                    <div className="text-3xl font-bold text-orange-500 mb-1">
                        {health?.tick || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">System Tick</div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* World Health */}
                <div className="lg:col-span-2">
                    <WorldHealth />
                </div>

                {/* Activity Pulse */}
                <div>
                    <ActivityPulse />
                </div>
            </div>

            {/* System Stats */}
            <SystemStats />

            {/* Recent Activity */}
            <div className="bg-secondary/10 rounded-lg border border-border p-6">
                <h2 className="text-xl font-bold mb-4">📊 Recent Activity</h2>
                <div className="space-y-3">
                    {decisions.slice(0, 5).map((decision) => (
                        <div
                            key={decision.id}
                            className="flex items-center justify-between p-3 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors"
                        >
                            <div className="flex-1">
                                <div className="font-medium">{decision.topic}</div>
                                <div className="text-sm text-muted-foreground">
                                    {decision.proposal_content?.slice(0, 100)}...
                                </div>
                            </div>
                            <div
                                className={`px-3 py-1 rounded-full text-xs font-medium ${decision.status === "ACCEPTED"
                                    ? "bg-green-500/20 text-green-500"
                                    : decision.status === "REJECTED"
                                        ? "bg-red-500/20 text-red-500"
                                        : "bg-blue-500/20 text-blue-500"
                                    }`}
                            >
                                {decision.status}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
