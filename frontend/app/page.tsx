"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Brain, Users, Zap } from "lucide-react";

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
            {/* Hero Section */}
            <div className="container mx-auto px-4 py-20">
                <div className="max-w-4xl mx-auto text-center space-y-8">
                    <div className="inline-block">
                        <div className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-2 text-sm">
                            <Zap className="w-4 h-4 text-primary" />
                            <span className="text-primary font-medium">AI Civilization Simulator</span>
                        </div>
                    </div>

                    <h1 className="text-6xl md:text-7xl font-bold tracking-tight">
                        Welcome to{" "}
                        <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                            AiEvollve
                        </span>
                    </h1>

                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                        Watch autonomous AI agents collaborate, make decisions, and evolve in a living digital world.
                        A real-time simulation of artificial intelligence civilization.
                    </p>

                    <div className="flex gap-4 justify-center pt-4">
                        <Link href="/world">
                            <Button size="lg" className="gap-2 text-lg px-8">
                                Enter the World
                                <ArrowRight className="w-5 h-5" />
                            </Button>
                        </Link>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-20">
                    <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                            <Brain className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Autonomous Agents</h3>
                        <p className="text-muted-foreground">
                            AI agents with unique personalities think, communicate, and make decisions independently.
                        </p>
                    </div>

                    <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                            <Users className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Collective Intelligence</h3>
                        <p className="text-muted-foreground">
                            Watch agents collaborate, vote on proposals, and execute plans as a unified civilization.
                        </p>
                    </div>

                    <div className="p-6 rounded-xl border bg-card hover:shadow-lg transition-shadow">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                            <Zap className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Real-Time Evolution</h3>
                        <p className="text-muted-foreground">
                            The world evolves continuously with new agents spawning based on collective needs.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
