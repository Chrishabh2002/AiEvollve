"use client";

import { useEffect, useState } from "react";
import EvolutionTimeline from "@/components/EvolutionTimeline";
import { formatDistanceToNow } from 'date-fns';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function EvolutionPage() {
    const [events, setEvents] = useState([]);
    const [generation, setGeneration] = useState(0);

    useEffect(() => {
        fetchEvolutionEvents();
    }, []);

    const fetchEvolutionEvents = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/world/evolution`);
            if (res.ok) {
                const data = await res.json();

                // Map API data to component format
                const mappedEvents = data.map((e: any) => ({
                    id: e.id,
                    timestamp: e.timestamp ? formatDistanceToNow(new Date(e.timestamp), { addSuffix: true }) : "Unknown",
                    trigger: e.trigger,
                    spawnedRole: e.spawned_agent_role,
                    reason: e.reason,
                    generation: e.generation
                }));

                setEvents(mappedEvents);
                setGeneration(mappedEvents.length > 0 ? mappedEvents[0].generation : 0);
            }
        } catch (e) {
            console.error("Failed to fetch evolution events", e);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">System Evolution</h2>
                <p className="text-muted-foreground">Self-adaptation log and ancestry</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2">
                    <div className="rounded-xl border bg-card p-6 min-h-[500px]">
                        <h3 className="font-semibold mb-6">Evolutionary Timeline</h3>
                        {/* @ts-ignore */}
                        {events.length > 0 ? (
                            <EvolutionTimeline events={events} />
                        ) : (
                            <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                                <p>No evolution events recorded yet.</p>
                                <p className="text-xs mt-2">System is stable.</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-2">Generation</h3>
                        <div className="text-4xl font-bold text-primary">Gen-{generation}</div>
                        <p className="text-sm text-muted-foreground mt-2">
                            System has self-evolved {generation} times since inception.
                        </p>
                    </div>

                    <div className="rounded-xl border bg-card p-6">
                        <h3 className="font-semibold mb-4">Dominant Traits</h3>
                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                                <span>Robustness</span>
                                <div className="h-2 w-24 bg-secondary rounded-full overflow-hidden">
                                    <div className="h-full bg-green-500 w-[80%]"></div>
                                </div>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span>Innovation</span>
                                <div className="h-2 w-24 bg-secondary rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-500 w-[60%]"></div>
                                </div>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span>Speed</span>
                                <div className="h-2 w-24 bg-secondary rounded-full overflow-hidden">
                                    <div className="h-full bg-amber-500 w-[90%]"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
