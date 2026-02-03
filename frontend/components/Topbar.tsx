"use client";

import React from "react"; // Added React import

import { Bell, Search, User } from "lucide-react";

export default function Topbar() {
    const [time, setTime] = React.useState<Date | null>(null);

    React.useEffect(() => {
        setTime(new Date());
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <header className="h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center justify-between px-6">
            {/* Search */}
            <div className="flex-1 max-w-md">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search neural logs, decisions, or agents..."
                        className="w-full pl-10 pr-4 py-2 bg-secondary/50 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-4">
                {/* System Status */}
                {/* System Status & Time */}
                <div className="flex flex-col items-end mr-4">
                    <div className="text-xs font-mono text-muted-foreground">
                        {time ? time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "--:--"}
                    </div>
                    <div className="text-[10px] text-muted-foreground/60">
                        {time ? time.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }) : "---"}
                    </div>
                </div>

                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-green-500">System Nominal</span>
                </div>

                {/* Notifications */}
                <button className="relative p-2 hover:bg-secondary/50 rounded-lg transition-colors">
                    <Bell className="w-5 h-5 text-muted-foreground" />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                {/* User Profile */}
                <button className="flex items-center gap-2 p-2 hover:bg-secondary/50 rounded-lg transition-colors">
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                    </div>
                    <div className="hidden md:block text-left">
                        <div className="text-sm font-medium">Chrishabh</div>
                        <div className="text-xs text-muted-foreground">CEO & Founder</div>
                    </div>
                </button>
            </div>
        </header>
    );
}
