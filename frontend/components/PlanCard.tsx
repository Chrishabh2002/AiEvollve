import { Box, CheckCircle2, Circle, XCircle } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface Plan {
    id: string;
    goal: string;
    status: "ACTIVE" | "COMPLETED" | "FAILED";
    progress: number;
    updated: string;
}

export default function PlanCard({ plan }: { plan: Plan }) {
    const statusColors = {
        "ACTIVE": "text-blue-500 bg-blue-500/10 border-blue-500/20",
        "COMPLETED": "text-green-500 bg-green-500/10 border-green-500/20",
        "FAILED": "text-red-500 bg-red-500/10 border-red-500/20",
    };

    return (
        <Link href={`/world/plans/${plan.id}`}>
            <div className="group rounded-lg border bg-card p-5 shadow-sm transition-all hover:bg-muted/30 hover:shadow-md hover:border-primary/30">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center text-primary">
                            <Box className="h-5 w-5" />
                        </div>
                        <div>
                            <h3 className="font-semibold group-hover:text-primary transition-colors">{plan.goal}</h3>
                            <p className="text-xs text-muted-foreground font-mono">{plan.id}</p>
                        </div>
                    </div>
                    <div className={cn("text-[10px] font-mono uppercase px-2 py-1 rounded border font-bold", statusColors[plan.status])}>
                        {plan.status}
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Progress</span>
                        <span>{plan.progress}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                        <div
                            className={cn("h-full transition-all", plan.status === "FAILED" ? "bg-red-500" : "bg-primary")}
                            style={{ width: `${plan.progress}%` }}
                        ></div>
                    </div>
                    <p className="text-xs text-muted-foreground pt-1 text-right">Updated {plan.updated}</p>
                </div>
            </div>
        </Link>
    );
}
