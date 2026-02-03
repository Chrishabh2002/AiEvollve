import { GitBranch, GitCommit, GitMerge, UserPlus } from "lucide-react";
import { cn } from "@/lib/utils";

interface EvoEvent {
    id: string;
    timestamp: string;
    trigger: "DEADLOCK" | "FAILURE" | "LOAD" | "OPTIMIZATION";
    spawnedRole: string;
    reason: string;
    generation: number;
}

export default function EvolutionEvent({ event }: { event: EvoEvent }) {
    const triggerColors = {
        "DEADLOCK": "text-amber-500 bg-amber-500/10",
        "FAILURE": "text-red-400 bg-red-500/10",
        "LOAD": "text-blue-500 bg-blue-500/10",
        "OPTIMIZATION": "text-purple-500 bg-purple-500/10"
    };

    return (
        <div className="relative pl-8 pb-8 border-l border-muted last:border-0 last:pb-0 group">
            <div className={cn(
                "absolute -left-3 top-0 h-6 w-6 rounded-full border bg-background flex items-center justify-center transition-all group-hover:scale-110",
                triggerColors[event.trigger]
            )}>
                {event.trigger === "DEADLOCK" && <GitMerge className="w-3.5 h-3.5" />}
                {event.trigger === "FAILURE" && <GitBranch className="w-3.5 h-3.5" />}
                {event.trigger === "LOAD" && <UserPlus className="w-3.5 h-3.5" />}
                {event.trigger === "OPTIMIZATION" && <GitCommit className="w-3.5 h-3.5" />}
            </div>

            <div className="rounded-lg border bg-card/50 p-4 transition-all hover:bg-card">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">{event.timestamp}</span>
                        <span className={cn("text-[10px] font-bold px-1.5 py-0.5 rounded", triggerColors[event.trigger])}>
                            {event.trigger}
                        </span>
                    </div>
                    <span className="font-mono text-xs text-muted-foreground">Gen {event.generation}</span>
                </div>

                <h3 className="font-medium text-foreground text-sm">
                    Spawned Agent: <span className="font-bold text-primary">{event.spawnedRole}</span>
                </h3>
                <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
                    {event.reason}
                </p>
            </div>
        </div>
    );
}
