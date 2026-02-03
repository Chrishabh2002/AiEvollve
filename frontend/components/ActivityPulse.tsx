export default function ActivityPulse() {
    return (
        <div className="flex items-center gap-1 h-8">
            <span className="text-xs font-mono text-muted-foreground mr-2 animate-pulse">SYSTEM HEARTBEAT</span>
            {[...Array(5)].map((_, i) => (
                <div
                    key={i}
                    className="w-1 bg-primary/40 rounded-full animate-pulse"
                    style={{
                        height: `${Math.random() * 60 + 20}%`,
                        animationDuration: `${Math.random() * 1000 + 500}ms`
                    }}
                ></div>
            ))}
            {[...Array(5)].map((_, i) => (
                <div
                    key={i + 5}
                    className="w-1 bg-primary/20 rounded-full animate-pulse"
                    style={{
                        height: `${Math.random() * 40 + 10}%`,
                        animationDuration: `${Math.random() * 1500 + 800}ms`
                    }}
                ></div>
            ))}
        </div>
    );
}
