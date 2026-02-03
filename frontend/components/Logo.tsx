import { BrainCircuit } from "lucide-react";

export default function Logo({ collapsed = false }: { collapsed?: boolean }) {
    return (
        <div className="flex items-center gap-3 font-mono text-primary select-none">
            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10">
                <BrainCircuit className="w-5 h-5" />
                <div className="absolute inset-0 bg-primary/20 blur-md rounded-lg animate-pulse"></div>
            </div>
            {!collapsed && (
                <span className="text-lg font-bold tracking-tighter">AiEvollve</span>
            )}
        </div>
    );
}
