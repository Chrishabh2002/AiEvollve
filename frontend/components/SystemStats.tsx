import { Activity, Brain, Box, Network } from "lucide-react";

const stats = [
    { label: "Total Agents", value: "12", icon: UsersIcon, color: "text-blue-500" },
    { label: "Active Decisions", value: "3", icon: ScaleIcon, color: "text-amber-500" },
    { label: "Sim Status", value: "98%", icon: Activity, color: "text-green-500" },
    { label: "Cycle Rate", value: "1.2 Hz", icon: Brain, color: "text-purple-500" },
];

import { Users as UsersIcon, Scale as ScaleIcon } from "lucide-react";

export default function SystemStats() {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat, index) => (
                <div
                    key={index}
                    className="rounded-xl border bg-card text-card-foreground p-6 shadow-sm transition-all hover:bg-accent/10"
                >
                    <div className="flex items-center justify-between space-y-0 pb-2">
                        <h3 className="text-sm font-medium text-muted-foreground">{stat.label}</h3>
                        <stat.icon className={`h-4 w-4 ${stat.color}`} />
                    </div>
                    <div className="text-2xl font-bold">{stat.value}</div>
                </div>
            ))}
        </div>
    );
}
