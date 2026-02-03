export default function DecisionTimeline({ events }: { events: any[] }) {
    return (
        <div className="relative border-l border-muted ml-3 space-y-6">
            {events.map((event, i) => (
                <div key={i} className="relative ml-6">
                    <div className="absolute -left-[31px] mt-1.5 h-2.5 w-2.5 rounded-full border border-background bg-muted-foreground/30"></div>
                    <div className="flex flex-col gap-1">
                        <span className="text-xs font-mono text-muted-foreground">{event.timestamp}</span>
                        <p className="text-sm">
                            <span className="font-semibold text-foreground/90">{event.agent}</span> {event.action}
                        </p>
                        {event.detail && (
                            <p className="text-xs text-muted-foreground mt-0.5 bg-muted/30 p-2 rounded border border-border/50">
                                "{event.detail}"
                            </p>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
