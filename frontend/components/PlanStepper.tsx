import { Check, CircleDashed, Loader2, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Step {
    id: string;
    description: string;
    status: "DONE" | "RUNNING" | "PENDING" | "FAILED";
}

export default function PlanStepper({ steps }: { steps: Step[] }) {

    const getIcon = (status: string) => {
        switch (status) {
            case "DONE": return <Check className="w-4 h-4 text-white" />;
            case "RUNNING": return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
            case "FAILED": return <X className="w-4 h-4 text-white" />;
            default: return <div className="w-2 h-2 bg-muted-foreground rounded-full" />;
        }
    }

    const getBg = (status: string) => {
        switch (status) {
            case "DONE": return "bg-green-500 border-green-500";
            case "RUNNING": return "bg-blue-500/10 border-blue-500";
            case "FAILED": return "bg-red-500 border-red-500";
            default: return "bg-background border-muted-foreground/30";
        }
    }

    return (
        <div className="space-y-0">
            {steps.map((step, index) => (
                <div key={index} className="flex gap-4 group">
                    <div className="flex flex-col items-center">
                        <div className={cn("w-8 h-8 rounded-full border flex items-center justify-center transition-colors z-10", getBg(step.status))}>
                            {getIcon(step.status)}
                        </div>
                        {index < steps.length - 1 && (
                            <div className={cn(
                                "w-0.5 h-12 my-1 transition-colors",
                                step.status === "DONE" ? "bg-green-500/50" : "bg-muted"
                            )}></div>
                        )}
                    </div>
                    <div className="pt-1.5 pb-8">
                        <p className={cn("text-sm font-medium", step.status === "PENDING" && "text-muted-foreground")}>
                            {step.description}
                        </p>
                        <p className="text-xs font-mono text-muted-foreground mt-0.5">{step.id}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}
