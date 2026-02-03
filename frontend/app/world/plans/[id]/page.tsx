"use client";

import PlanStepper from "@/components/PlanStepper";
import ExecutionLog from "@/components/ExecutionLog";
import { ArrowLeft, Box, PlayCircle, PauseCircle } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const MOCK_PLAN_DETAIL = {
    id: "P-9021",
    goal: "Optimize Database Indices",
    status: "ACTIVE",
    progress: 45,
    steps: [
        { id: "S-1", description: "Analyze slow query logs", status: "DONE" },
        { id: "S-2", description: "Identify missing indices", status: "DONE" },
        { id: "S-3", description: "Generate migration script", status: "RUNNING" },
        { id: "S-4", description: "Execute migration (dry-run)", status: "PENDING" },
        { id: "S-5", description: "Apply changes", status: "PENDING" }
    ],
    logs: [
        { timestamp: "10:30:05", message: "Plan started by Executor-1" },
        { timestamp: "10:30:06", message: "Step S-1: Analyzing logs for last 24h..." },
        { timestamp: "10:30:15", message: "Step S-1: DONE. Found 3 slow query patterns." },
        { timestamp: "10:30:16", message: "Step S-2: Matching patterns to schema..." },
        { timestamp: "10:30:20", message: "Step S-2: DONE. Candidate indices identified: users_idx_email, logs_idx_ts." },
        { timestamp: "10:30:21", message: "Step S-3: Generating SQL..." }
    ]
};

export default function PlanDetailPage({ params }: { params: { id: string } }) {
    // @ts-ignore
    const plan = MOCK_PLAN_DETAIL;

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/world/plans">
                        <Button variant="ghost" size="icon">
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                    </Link>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-bold tracking-tight">{plan.goal}</h1>
                            <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 border border-blue-500/20 text-xs font-bold uppercase flex items-center gap-1">
                                <PlayCircle className="w-3 h-3" /> Active
                            </span>
                        </div>
                        <p className="text-muted-foreground font-mono text-sm mt-1">{plan.id}</p>
                    </div>
                </div>

                <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                        <PauseCircle className="w-4 h-4 mr-2" /> Pause
                    </Button>
                    <Button variant="destructive" size="sm">
                        Abort
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Left Column: Steps */}
                <div className="rounded-xl border bg-card p-8">
                    <h3 className="font-semibold mb-6 flex items-center gap-2">
                        <Box className="w-4 h-4 text-primary" /> Execution Steps
                    </h3>
                    {/* @ts-ignore */}
                    <PlanStepper steps={plan.steps} />
                </div>

                {/* Right Column: Logs */}
                <div className="space-y-6">
                    <div className="rounded-xl border bg-card p-6 h-full flex flex-col">
                        <h3 className="font-semibold mb-4">Live Execution Log</h3>
                        <div className="flex-1">
                            <ExecutionLog logs={plan.logs} />
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
