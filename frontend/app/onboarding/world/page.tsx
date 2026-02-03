import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Globe, Lock } from "lucide-react";

export default function OnboardingWorld() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-background animate-in fade-in duration-500">
            <div className="max-w-2xl text-center space-y-8 w-full">
                <h1 className="text-3xl font-bold tracking-tight">Select Environment</h1>
                <p className="text-muted-foreground">
                    Where should we initialize your session?
                </p>

                <div className="grid grid-cols-1 gap-4 pt-4 max-w-md mx-auto w-full">
                    <Link href="/world">
                        <Button variant="outline" size="lg" className="w-full justify-start h-16 text-lg gap-4">
                            <Globe className="h-6 w-6 text-primary" />
                            <span>Public Demo World</span>
                        </Button>
                    </Link>

                    <Button variant="outline" size="lg" className="w-full justify-start h-16 text-lg gap-4 opacity-50 cursor-not-allowed">
                        <Lock className="h-6 w-6 text-muted-foreground" />
                        <span>Private World (Premium)</span>
                    </Button>
                </div>
            </div>
        </div>
    );
}
