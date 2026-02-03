import EvolutionEvent from "./EvolutionEvent";

interface EvoEvent {
    id: string;
    timestamp: string;
    trigger: "DEADLOCK" | "FAILURE" | "LOAD" | "OPTIMIZATION";
    spawnedRole: string;
    reason: string;
    generation: number;
}

export default function EvolutionTimeline({ events }: { events: EvoEvent[] }) {
    return (
        <div className="py-2">
            {events.map(event => (
                <EvolutionEvent key={event.id} event={event} />
            ))}

            {/* Origin Point */}
            <div className="relative pl-8 pt-4">
                <div className="absolute -left-2 top-4 h-4 w-4 rounded-full bg-primary/20 border-2 border-primary animate-pulse"></div>
                <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">System Genesis</p>
            </div>
        </div>
    );
}
