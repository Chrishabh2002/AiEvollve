"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchPlans } from "@/lib/api";
import { FileText, Play, CheckCircle, XCircle, Clock, Pause } from "lucide-react";

interface Plan {
    id: string;
    title: string;
    description: string;
    decision_id?: string;
    status: string;
    created_at: string;
    completed_at?: string;
    steps?: any[];
    current_step?: number;
}

export default function PlansPage() {
    const [plans, setPlans] = useState<Plan[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>("ALL");

    useEffect(() => {
        async function loadPlans() {
            try {
                const data = await fetchPlans();
                setPlans(data);
            } catch (error) {
                console.error("Failed to load plans:", error);
            } finally {
                setLoading(false);
            }
        }

        loadPlans();
        const interval = setInterval(loadPlans, 3000); // Refresh every 3s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    const filteredPlans = filter === "ALL"
        ? plans
        : plans.filter(p => p.status === filter);

    const activeCount = plans.filter(p => p.status === "ACTIVE").length;
    const completedCount = plans.filter(p => p.status === "COMPLETED").length;
    const failedCount = plans.filter(p => p.status === "FAILED").length;

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "ACTIVE": return <Play className="w-5 h-5 text-blue-500" />;
            case "COMPLETED": return <CheckCircle className="w-5 h-5 text-green-500" />;
            case "FAILED": return <XCircle className="w-5 h-5 text-red-500" />;
            case "PAUSED": return <Pause className="w-5 h-5 text-orange-500" />;
            default: return <Clock className="w-5 h-5 text-gray-500" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "ACTIVE": return "bg-blue-500/20 text-blue-500 border-blue-500/30";
            case "COMPLETED": return "bg-green-500/20 text-green-500 border-green-500/30";
            case "FAILED": return "bg-red-500/20 text-red-500 border-red-500/30";
            case "PAUSED": return "bg-orange-500/20 text-orange-500 border-orange-500/30";
            default: return "bg-gray-500/20 text-gray-500 border-gray-500/30";
        }
    };

    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch {
            return "Unknown";
        }
    };

    const getProgress = (plan: Plan) => {
        if (!plan.steps || plan.steps.length === 0) return 0;
        const current = plan.current_step || 0;
        return Math.round((current / plan.steps.length) * 100);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">📄 Execution Plans</h1>
                <p className="text-muted-foreground">
                    Real-world actions being executed by agents
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-500">{plans.length}</div>
                    <div className="text-sm text-muted-foreground">Total Plans</div>
                </div>
                <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-500">{activeCount}</div>
                    <div className="text-sm text-muted-foreground">Active</div>
                </div>
                <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-500">{completedCount}</div>
                    <div className="text-sm text-muted-foreground">Completed</div>
                </div>
                <div className="bg-gradient-to-br from-red-500/10 to-red-500/5 border border-red-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-red-500">{failedCount}</div>
                    <div className="text-sm text-muted-foreground">Failed</div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
                {["ALL", "ACTIVE", "COMPLETED", "FAILED", "PAUSED"].map((status) => (
                    <button
                        key={status}
                        onClick={() => setFilter(status)}
                        className={`px-4 py-2 rounded-lg font-medium transition-all ${filter === status
                                ? "bg-primary text-primary-foreground shadow-md"
                                : "bg-secondary/50 text-muted-foreground hover:bg-secondary"
                            }`}
                    >
                        {status}
                    </button>
                ))}
            </div>

            {/* Plans List */}
            <div className="space-y-4">
                {filteredPlans.length === 0 ? (
                    <div className="text-center py-12 bg-secondary/20 rounded-lg border border-border">
                        <p className="text-muted-foreground">
                            No plans found for this filter.
                        </p>
                    </div>
                ) : (
                    filteredPlans.map((plan) => {
                        const progress = getProgress(plan);

                        return (
                            <Link
                                key={plan.id}
                                href={`/world/plans/${plan.id}`}
                                className="block bg-secondary/10 rounded-lg border border-border p-6 hover:bg-secondary/20 hover:shadow-lg transition-all duration-200"
                            >
                                {/* Header */}
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            {getStatusIcon(plan.status)}
                                            <h3 className="text-xl font-bold">{plan.title}</h3>
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            Created {formatDate(plan.created_at)}
                                        </div>
                                    </div>
                                    <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(plan.status)}`}>
                                        {plan.status}
                                    </div>
                                </div>

                                {/* Description */}
                                <p className="text-foreground/90 mb-4 line-clamp-2">
                                    {plan.description}
                                </p>

                                {/* Progress Bar */}
                                {plan.steps && plan.steps.length > 0 && (
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-muted-foreground">
                                                Step {plan.current_step || 0} of {plan.steps.length}
                                            </span>
                                            <span className="font-medium">{progress}%</span>
                                        </div>
                                        <div className="w-full bg-secondary/50 rounded-full h-2">
                                            <div
                                                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                                                style={{ width: `${progress}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </Link>
                        );
                    })
                )}
            </div>
        </div>
    );
}
