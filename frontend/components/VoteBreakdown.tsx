"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Ban, Lightbulb } from "lucide-react";

interface Vote {
    agent: string;
    decision: "YES" | "NO" | "BLOCK";
    weight: number;
    reasoning?: string;
    suggestions?: string[];
}

export default function VoteBreakdown({ votes }: { votes: Vote[] }) {
    const [expandedVotes, setExpandedVotes] = useState<Set<number>>(new Set());

    const toggleVote = (index: number) => {
        const newExpanded = new Set(expandedVotes);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedVotes(newExpanded);
    };

    const yesVotes = votes.filter(v => v.decision === "YES");
    const noVotes = votes.filter(v => v.decision === "NO");
    const blockVotes = votes.filter(v => v.decision === "BLOCK");

    const totalWeight = votes.reduce((sum, v) => sum + v.weight, 0);
    const yesWeight = yesVotes.reduce((sum, v) => sum + v.weight, 0);

    const widthPercent = totalWeight > 0 ? (yesWeight / totalWeight) * 100 : 0;

    const getVoteIcon = (decision: string) => {
        switch (decision) {
            case "YES":
                return <ThumbsUp className="w-4 h-4 text-green-500" />;
            case "NO":
                return <ThumbsDown className="w-4 h-4 text-orange-500" />;
            case "BLOCK":
                return <Ban className="w-4 h-4 text-red-500" />;
            default:
                return null;
        }
    };

    const getVoteColor = (decision: string) => {
        switch (decision) {
            case "YES":
                return "border-green-500/30 bg-green-500/5 hover:bg-green-500/10";
            case "NO":
                return "border-orange-500/30 bg-orange-500/5 hover:bg-orange-500/10";
            case "BLOCK":
                return "border-red-500/30 bg-red-500/5 hover:bg-red-500/10";
            default:
                return "border-border/30 bg-secondary/5";
        }
    };

    return (
        <div className="space-y-6">
            {/* Vote Summary Bar */}
            <div className="bg-secondary/20 rounded-lg p-4 border border-border/50">
                <div className="flex justify-between items-center mb-3 text-sm font-medium">
                    <div className="flex items-center gap-2">
                        <ThumbsUp className="w-4 h-4 text-green-500" />
                        <span className="text-green-500">YES ({yesVotes.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <ThumbsDown className="w-4 h-4 text-orange-500" />
                        <span className="text-orange-500">NO ({noVotes.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Ban className="w-4 h-4 text-red-500" />
                        <span className="text-red-500">BLOCK ({blockVotes.length})</span>
                    </div>
                </div>

                {/* Animated Progress Bar */}
                <div className="h-4 w-full bg-gradient-to-r from-red-500/20 to-red-500/20 rounded-full overflow-hidden flex relative">
                    <div
                        className="h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-1000 ease-out shadow-lg shadow-green-500/50"
                        style={{ width: `${widthPercent}%` }}
                    >
                        <div className="h-full w-full bg-gradient-to-t from-white/20 to-transparent"></div>
                    </div>
                </div>

                <div className="mt-2 text-center text-xs text-muted-foreground">
                    {widthPercent.toFixed(1)}% Support
                </div>
            </div>

            {/* Individual Votes with Detailed Reasoning */}
            <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                    Individual Votes & Reasoning
                </h3>

                {votes.map((vote, i) => {
                    const isExpanded = expandedVotes.has(i);
                    const hasDetails = vote.reasoning || (vote.suggestions && vote.suggestions.length > 0);

                    return (
                        <div
                            key={i}
                            className={`border rounded-lg transition-all duration-300 ${getVoteColor(vote.decision)} ${isExpanded ? "shadow-lg" : "shadow-sm"
                                }`}
                        >
                            {/* Vote Header */}
                            <div
                                className={`flex items-center justify-between p-4 ${hasDetails ? "cursor-pointer" : ""
                                    }`}
                                onClick={() => hasDetails && toggleVote(i)}
                            >
                                <div className="flex items-center gap-3 flex-1">
                                    {getVoteIcon(vote.decision)}
                                    <span className="font-mono text-sm font-medium">{vote.agent}</span>
                                </div>

                                <div className="flex items-center gap-4">
                                    {/* Weight Indicator */}
                                    <div className="flex items-center gap-2">
                                        <div className="w-20 h-2 bg-secondary rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-blue-400 to-purple-500 transition-all duration-500"
                                                style={{ width: `${vote.weight * 10}%` }}
                                            ></div>
                                        </div>
                                        <span className="text-xs text-muted-foreground w-8">
                                            {vote.weight.toFixed(1)}
                                        </span>
                                    </div>

                                    {/* Decision Badge */}
                                    <span
                                        className={`font-bold text-sm px-3 py-1 rounded-full ${vote.decision === "YES"
                                                ? "bg-green-500/20 text-green-500"
                                                : vote.decision === "BLOCK"
                                                    ? "bg-red-500/20 text-red-500"
                                                    : "bg-orange-500/20 text-orange-500"
                                            }`}
                                    >
                                        {vote.decision}
                                    </span>

                                    {/* Expand Icon */}
                                    {hasDetails && (
                                        <div className="ml-2">
                                            {isExpanded ? (
                                                <ChevronUp className="w-4 h-4 text-muted-foreground" />
                                            ) : (
                                                <ChevronDown className="w-4 h-4 text-muted-foreground" />
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Expanded Details */}
                            {isExpanded && hasDetails && (
                                <div className="px-4 pb-4 space-y-3 border-t border-border/30 pt-3 animate-in slide-in-from-top-2 duration-300">
                                    {/* Reasoning */}
                                    {vote.reasoning && (
                                        <div className="space-y-2">
                                            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                                                <span>💭</span>
                                                <span>Reasoning</span>
                                            </div>
                                            <p className="text-sm leading-relaxed pl-5 text-foreground/90 italic">
                                                "{vote.reasoning}"
                                            </p>
                                        </div>
                                    )}

                                    {/* Suggestions */}
                                    {vote.suggestions && vote.suggestions.length > 0 && (
                                        <div className="space-y-2">
                                            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                                                <Lightbulb className="w-3 h-3" />
                                                <span>Suggestions</span>
                                            </div>
                                            <ul className="space-y-1.5 pl-5">
                                                {vote.suggestions.map((suggestion, idx) => (
                                                    <li
                                                        key={idx}
                                                        className="text-sm text-foreground/80 flex items-start gap-2"
                                                    >
                                                        <span className="text-blue-400 mt-0.5">•</span>
                                                        <span>{suggestion}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Summary Section */}
            {votes.length > 0 && (
                <div className="bg-secondary/10 rounded-lg p-4 border border-border/30">
                    <h4 className="text-sm font-semibold mb-2">📊 Consensus Summary</h4>
                    <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                            <div className="text-2xl font-bold text-green-500">{yesVotes.length}</div>
                            <div className="text-xs text-muted-foreground">Support</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-orange-500">{noVotes.length}</div>
                            <div className="text-xs text-muted-foreground">Concerns</div>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-red-500">{blockVotes.length}</div>
                            <div className="text-xs text-muted-foreground">Blocked</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
