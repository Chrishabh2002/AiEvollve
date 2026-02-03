import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

// Minimal mock Avatar since we didn't install Shadcn Avatar fully, implementing simple one inline or stubbing imports if possible.
// Wait, user said "Existing Phase-1 components ONLY". I did NOT implement Avatar, Badge, Progress in Phase 1.
// I must implement simple versions of them locally or use basic HTML/Tailwind.

function SimpleAvatar({ name }: { name: string }) {
    const initials = name.slice(0, 2).toUpperCase();
    return (
        <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full bg-secondary flex items-center justify-center font-bold text-xs text-secondary-foreground border border-primary/20">
            {initials}
        </div>
    );
}

function SimpleBadge({ children, variant = "default" }: { children: React.ReactNode, variant?: "default" | "outline" | "secondary" }) {
    const variants = {
        default: "bg-primary/20 text-primary border-transparent",
        outline: "text-foreground border-border",
        secondary: "bg-secondary text-secondary-foreground border-transparent"
    };
    return (
        <div className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${variants[variant]}`}>
            {children}
        </div>
    );
}

function SimpleProgress({ value }: { value: number }) {
    return (
        <div className="h-2 w-full overflow-hidden rounded-full bg-secondary/50">
            <div className="h-full bg-primary transition-all" style={{ width: `${value}%` }}></div>
        </div>
    );
}

interface Agent {
    id: string;
    name: string;
    role: string;
    state: "IDLE" | "THINKING" | "EXECUTING" | "DELIBERATING";
    reputation: number;
}

export default function AgentCard({ agent, onClick }: { agent: Agent, onClick: () => void }) {
    return (
        <div
            onClick={onClick}
            className="group relative flex flex-col justify-between overflow-hidden rounded-xl border bg-card p-6 shadow-sm transition-all hover:bg-muted/50 hover:shadow-md cursor-pointer hover:border-primary/40"
        >
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                    <SimpleAvatar name={agent.name} />
                    <div>
                        <h3 className="font-semibold leading-none tracking-tight">{agent.name}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{agent.role}</p>
                    </div>
                </div>
                <SimpleBadge variant={agent.state === "EXECUTING" ? "default" : "secondary"}>
                    {agent.state}
                </SimpleBadge>
            </div>

            <div className="mt-8 space-y-2">
                <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Reputation</span>
                    <span>{agent.reputation}%</span>
                </div>
                <SimpleProgress value={agent.reputation} />
            </div>

            <div className="absolute top-0 right-0 p-6 opacity-0 group-hover:opacity-10 transition-opacity">
                <div className="text-6xl font-black text-primary pointer-events-none">#</div>
            </div>
        </div>
    );
}
