import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Eye, Shield } from "lucide-react";

export default function OnboardingRole() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-background animate-in fade-in duration-500">
            <div className="max-w-2xl text-center space-y-8 w-full">
                <h1 className="text-3xl font-bold tracking-tight">Choose Your Role</h1>
                <p className="text-muted-foreground">
                    How do you wish to interact with the ecosystem?
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                    {/* Observer Card */}
                    <Link href="/onboarding/world" className="group relative rounded-xl border bg-card p-6 hover:bg-accent/50 transition-all hover:border-primary/50 text-left">
                        <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                            <Eye className="h-6 w-6" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Observer</h3>
                        <p className="text-muted-foreground text-sm">
                            Watch agents evolve without direct interference. Access pure analytics and logs.
                        </p>
                    </Link>

                    {/* Guide Card */}
                    <Link href="/onboarding/world" className="group relative rounded-xl border bg-card p-6 hover:bg-accent/50 transition-all hover:border-primary/50 text-left">
                        <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-secondary/80 text-secondary-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                            <Shield className="h-6 w-6" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Guide</h3>
                        <p className="text-muted-foreground text-sm">
                            Influence decisions and set boundaries. Act as a governance layer.
                        </p>
                    </Link>
                </div>
            </div>
        </div>
    );
}
