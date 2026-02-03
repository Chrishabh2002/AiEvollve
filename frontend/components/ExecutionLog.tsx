export default function ExecutionLog({ logs }: { logs: Array<{ timestamp: string, message: string }> }) {
    return (
        <div className="rounded-lg border bg-black/50 font-mono text-xs p-4 h-[300px] overflow-y-auto space-y-2">
            {logs.map((log, i) => (
                <div key={i} className="flex gap-3 text-muted-foreground hover:text-foreground transition-colors">
                    <span className="opacity-50 select-none flex-shrink-0">[{log.timestamp}]</span>
                    <span>{log.message}</span>
                </div>
            ))}
            <div className="text-primary animate-pulse">_</div>
        </div>
    );
}
