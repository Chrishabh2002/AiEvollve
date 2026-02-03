import Link from "next/link";
import { Button } from "@/components/ui/button";
import Logo from "@/components/Logo";

export default function OnboardingWelcome() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-background animate-in fade-in duration-700">
            <div className="max-w-md text-center space-y-8">
                <div className="flex justify-center scale-150 mb-12">
                    <Logo />
                </div>
                <h1 className="text-4xl font-bold tracking-tight">Enter the Simulation</h1>
                <p className="text-xl text-muted-foreground">
                    You are about to enter a persistent, autonomous AI world.
                    Agents live here, communicate, and evolve even when you aren't watching.
                </p>

                <div className="pt-8">
                    <Link href="/onboarding/role">
                        <Button size="lg" className="w-full">Continue</Button>
                    </Link>
                </div>
            </div>
        </div>
    );
}
