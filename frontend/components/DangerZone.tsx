import { Button } from "@/components/ui/button";
import { AlertTriangle, Trash2, Power } from "lucide-react";

export default function DangerZone() {
    return (
        <div className="rounded-xl border border-red-900/50 bg-red-950/10 p-6 space-y-6">
            <h3 className="text-lg font-semibold text-red-500 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" /> Danger Zone
            </h3>

            <div className="flex items-center justify-between p-4 rounded-lg border border-red-900/20 bg-background/50">
                <div>
                    <h4 className="font-medium text-foreground">Emergency Stop</h4>
                    <p className="text-sm text-muted-foreground">Immediately halts all agent execution threads.</p>
                </div>
                <Button variant="destructive">
                    <Power className="h-4 w-4 mr-2" />
                    HALT SYSTEM
                </Button>
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg border border-red-900/20 bg-background/50">
                <div>
                    <h4 className="font-medium text-foreground">Factory Reset</h4>
                    <p className="text-sm text-muted-foreground">Wipes all memory, agents, and decisions.</p>
                </div>
                <Button variant="outline" className="text-red-500 border-red-900/50 hover:bg-red-950/30">
                    <Trash2 className="h-4 w-4 mr-2" />
                    RESET WORLD
                </Button>
            </div>
        </div>
    );
}
