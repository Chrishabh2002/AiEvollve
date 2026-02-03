import { BadgeCheck, Ban, Clock, Timer } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface Decision {
    id: string;
    topic: string;
    status: "OPEN" | "VOTING" | "CLOSED";
    result: "ACCEPTED" | "REJECTED" | "PENDING";
    confidence: number;
    timestamp: string;
    author: string;
}

export default function DecisionCard({ decision }: { decision: Decision }) {
    const statusColors = {
        "OPEN": "text-blue-500 bg-blue-500/10 border-blue-500/20",
        "VOTING": "text-amber-500 bg-amber-500/10 border-amber-500/20",
        "CLOSED": "text-muted-foreground bg-muted/50 border-border",
    };

    const resultColors = {
        "ACCEPTED": "text-green-500 border-green-500/20 bg-green-500/10",
        "REJECTED": "text-red-500 border-red-500/20 bg-red-500/10",
        "PENDING": "text-muted-foreground border-border"
    };

    return (
        <Link href={`/world/decisions/${decision.id}`}>
            <div className="group relative rounded-lg border bg-card p-5 shadow-sm transition-all hover:bg-muted/30 hover:shadow-md hover:border-primary/30">
                <div className="flex items-start justify-between">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2 mb-2">
                            <span className={cn("text-[10px] font-mono uppercase px-1.5 py-0.5 rounded border", statusColors[decision.status])}>
                                {decision.status}
                            </span>
                            <span className="text-xs text-muted-foreground font-mono">{decision.id}</span>
                        </div>
                        <h3 className="font-semibold text-lg leading-tight group-hover:text-primary transition-colors">
                            {decision.topic}
                        </h3>
                        <p className="text-sm text-muted-foreground">Proposed by {decision.author} • {decision.timestamp}</p>
                    </div>

                    <div className="flex flex-col items-end gap-2 text-right">
                        {decision.result !== "PENDING" && (
                            <div className={cn("flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-bold", resultColors[decision.result])}>
                                {decision.result === "ACCEPTED" ? <BadgeCheck className="w-3.5 h-3.5" /> : <Ban className="w-3.5 h-3.5" />}
                                {decision.result}
                            </div>
                        )}
                        {decision.result === "PENDING" && (
                            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border bg-muted text-muted-foreground text-xs font-medium">
                                <Timer className="w-3.5 h-3.5" /> Voting
                            </div>
                        )}

                        {decision.status === "CLOSED" && (
                            <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                                conf: {(decision.confidence * 100).toFixed(0)}%
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </Link>
    );
}
