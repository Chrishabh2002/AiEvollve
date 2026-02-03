"use client";

import { useEffect, useState, use } from "react";
import DecisionTimeline from "@/components/DecisionTimeline";
import VoteBreakdown from "@/components/VoteBreakdown";
import { BadgeCheck, ArrowLeft, Ban, Timer } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const API_ROOT = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function fetchDecisionDetail(id: string) {
    const res = await fetch(`${API_ROOT}/api/world/decisions/${id}`, { cache: 'no-store' });
    if (!res.ok) throw new Error("Failed to fetch decision");
    return res.json();
}

export default function DecisionDetailPage({ params }: { params: Promise<{ id: string }> }) {
    // Unwrap the params Promise using React.use()
    const { id } = use(params);

    const [decision, setDecision] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const data = await fetchDecisionDetail(id);
                setDecision(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        load();
        const interval = setInterval(load, 2000); // Live polling
        return () => clearInterval(interval);
    }, [id]);

    if (loading) return <div className="p-10 text-center animate-pulse">Loading decision data...</div>;
    if (!decision) return <div className="p-10 text-center text-red-500">Decision not found</div>;

    // Transform API data for components if needed
    // Our API returns "votes_summary" instead of raw votes list sometimes,
    // let's check what the API returns. The view_file of decisions.py showed we return votes_summary.
    // We should probably update the API to return the raw votes list for the breakdown to work!

    // For now, let's look at the "detail" endpoint in decisions.py.
    // It returns votes_summary object. It does NOT return the individual votes list.
    // WE NEED TO UPDATE THE BACKEND TO RETURN VOTES LIST.

    // Assuming backend will be updated:
    // decision.votes = [{agent: "Name", decision: "YES", weight: 1.0}, ...]

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">

            <div className="flex items-center gap-4">
                <Link href="/world/decisions">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                </Link>
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold tracking-tight">{decision.topic}</h1>

                        {decision.result === "ACCEPTED" && (
                            <span className="px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 border border-green-500/20 text-xs font-bold uppercase flex items-center gap-1">
                                <BadgeCheck className="w-3 h-3" /> Accepted
                            </span>
                        )}
                        {decision.result === "REJECTED" && (
                            <span className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 border border-red-500/20 text-xs font-bold uppercase flex items-center gap-1">
                                <Ban className="w-3 h-3" /> Rejected
                            </span>
                        )}
                        {!decision.result && (
                            <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500 border border-amber-500/20 text-xs font-bold uppercase flex items-center gap-1">
                                <Timer className="w-3 h-3" /> Voting in Progress
                            </span>
                        )}
                    </div>
                    <p className="text-muted-foreground font-mono text-sm mt-1">{decision.id} • {decision.created_at}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Left Column: Context & Timeline */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-4">Proposal</h3>
                        <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                            {decision.proposal_content || "No detailed content provided."}
                        </p>
                    </div>

                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-6">Decision Timeline</h3>
                        {/* decision.timeline might be missing from API, handle gracefully */}
                        {decision.timeline ? (
                            <DecisionTimeline events={decision.timeline} />
                        ) : (
                            <p className="text-muted-foreground text-sm">Timeline data not available.</p>
                        )}
                    </div>
                </div>

                {/* Right Column: Votes with Reasoning */}
                <div className="space-y-6">
                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-4 flex items-center justify-between">
                            <span>Vote Breakdown</span>
                            <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-1 rounded-full">
                                {decision.votes?.length || 0} Votes
                            </span>
                        </h3>

                        {/* Summary Bar */}
                        <div className="flex w-full h-2 bg-secondary rounded-full overflow-hidden mb-6">
                            <div className="bg-green-500 h-full transition-all duration-500" style={{ width: `${(decision.votes_summary?.yes / (decision.votes.length || 1)) * 100}%` }} />
                            <div className="bg-red-500 h-full transition-all duration-500" style={{ width: `${(decision.votes_summary?.no / (decision.votes.length || 1)) * 100}%` }} />
                        </div>

                        {decision.votes && decision.votes.length > 0 ? (
                            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                                {decision.votes.map((vote: any, idx: number) => (
                                    <div key={idx} className="p-3 rounded-lg border bg-secondary/5 text-sm hover:bg-secondary/10 transition-colors">
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                <div className={`w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-[10px] text-white font-bold`}>
                                                    {vote.agent[0]}
                                                </div>
                                                <span className="font-semibold text-foreground/90">{vote.agent}</span>
                                            </div>
                                            <span className={cn(
                                                "px-2 py-0.5 rounded text-[10px] font-bold border",
                                                vote.decision === "YES" ? "bg-green-500/10 text-green-500 border-green-500/20" :
                                                    vote.decision === "NO" ? "bg-red-500/10 text-red-500 border-red-500/20" :
                                                        "bg-amber-500/10 text-amber-500 border-amber-500/20"
                                            )}>
                                                {vote.decision}
                                            </span>
                                        </div>

                                        {/* Reasoning Display */}
                                        {vote.reasoning && (
                                            <div className="pl-8 text-muted-foreground/80 italic text-xs border-l-2 border-border ml-1 mt-1">
                                                "{vote.reasoning}"
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground text-sm">
                                No detailed votes recorded yet.
                            </div>
                        )}

                        {/* Result Logic */}
                        {decision.result && (
                            <div className="mt-6 pt-6 border-t">
                                <h4 className="text-xs font-bold uppercase text-muted-foreground mb-2">Final Verdict</h4>
                                <div className={cn(
                                    "p-3 rounded-lg text-center font-bold border",
                                    decision.result === "ACCEPTED" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-red-500/10 text-red-500 border-red-500/20"
                                )}>
                                    {decision.result}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
