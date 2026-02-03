"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchDecisions } from "@/lib/api";
import { Target, ThumbsUp, ThumbsDown, Shield, Clock, CheckCircle, XCircle } from "lucide-react";

interface Decision {
    id: string;
    topic: string;
    proposal_content: string;
    proposer_id: string;
    proposer_name: string;
    status: string;
    created_at: string;
    resolved_at?: string;
    votes?: any[];
}

export default function DecisionsPage() {
    const [decisions, setDecisions] = useState<Decision[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>("ALL");

    useEffect(() => {
        async function loadDecisions() {
            try {
                const data = await fetchDecisions();
                setDecisions(data);
            } catch (error) {
                console.error("Failed to load decisions:", error);
            } finally {
                setLoading(false);
            }
        }

        loadDecisions();
        const interval = setInterval(loadDecisions, 3000); // Refresh every 3s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    const filteredDecisions = filter === "ALL"
        ? decisions
        : decisions.filter(d => d.status === filter);

    const votingCount = decisions.filter(d => d.status === "VOTING" || d.status === "OPEN").length;
    const acceptedCount = decisions.filter(d => d.status === "ACCEPTED").length;
    const rejectedCount = decisions.filter(d => d.status === "REJECTED").length;

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "ACCEPTED": return <CheckCircle className="w-5 h-5 text-green-500" />;
            case "REJECTED": return <XCircle className="w-5 h-5 text-red-500" />;
            case "VOTING":
            case "OPEN": return <Clock className="w-5 h-5 text-blue-500" />;
            default: return <Target className="w-5 h-5 text-gray-500" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "ACCEPTED": return "bg-green-500/20 text-green-500 border-green-500/30";
            case "REJECTED": return "bg-red-500/20 text-red-500 border-red-500/30";
            case "VOTING":
            case "OPEN": return "bg-blue-500/20 text-blue-500 border-blue-500/30";
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

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">🎯 Decisions</h1>
                <p className="text-muted-foreground">
                    Collective decision-making by the AI civilization
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-500">{decisions.length}</div>
                    <div className="text-sm text-muted-foreground">Total Decisions</div>
                </div>
                <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-500">{votingCount}</div>
                    <div className="text-sm text-muted-foreground">Open for Voting</div>
                </div>
                <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-500">{acceptedCount}</div>
                    <div className="text-sm text-muted-foreground">Accepted</div>
                </div>
                <div className="bg-gradient-to-br from-red-500/10 to-red-500/5 border border-red-500/20 rounded-lg p-4">
                    <div className="text-2xl font-bold text-red-500">{rejectedCount}</div>
                    <div className="text-sm text-muted-foreground">Rejected</div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
                {["ALL", "VOTING", "OPEN", "ACCEPTED", "REJECTED"].map((status) => (
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

            {/* Decisions List */}
            <div className="space-y-4">
                {filteredDecisions.length === 0 ? (
                    <div className="text-center py-12 bg-secondary/20 rounded-lg border border-border">
                        <p className="text-muted-foreground">
                            No decisions found for this filter.
                        </p>
                    </div>
                ) : (
                    filteredDecisions.map((decision) => (
                        <Link
                            key={decision.id}
                            href={`/world/decisions/${decision.id}`}
                            className="block bg-secondary/10 rounded-lg border border-border p-6 hover:bg-secondary/20 hover:shadow-lg transition-all duration-200"
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        {getStatusIcon(decision.status)}
                                        <h3 className="text-xl font-bold">{decision.topic}</h3>
                                    </div>
                                    <div className="text-sm text-muted-foreground">
                                        Proposed by <span className="font-medium text-foreground">{decision.proposer_name}</span>
                                        {" · "}
                                        {formatDate(decision.created_at)}
                                    </div>
                                </div>
                                <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(decision.status)}`}>
                                    {decision.status}
                                </div>
                            </div>

                            {/* Proposal Content */}
                            <p className="text-foreground/90 mb-4 line-clamp-3">
                                {decision.proposal_content}
                            </p>

                            {/* Vote Summary */}
                            {decision.votes && decision.votes.length > 0 && (
                                <div className="flex items-center gap-4 text-sm">
                                    <div className="flex items-center gap-2 text-green-500">
                                        <ThumbsUp className="w-4 h-4" />
                                        <span>{decision.votes.filter((v: any) => v.decision === "YES").length}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-red-500">
                                        <ThumbsDown className="w-4 h-4" />
                                        <span>{decision.votes.filter((v: any) => v.decision === "NO").length}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-orange-500">
                                        <Shield className="w-4 h-4" />
                                        <span>{decision.votes.filter((v: any) => v.decision === "BLOCK").length}</span>
                                    </div>
                                    <div className="text-muted-foreground ml-auto">
                                        {decision.votes.length} votes
                                    </div>
                                </div>
                            )}
                        </Link>
                    ))
                )}
            </div>
        </div>
    );
}
