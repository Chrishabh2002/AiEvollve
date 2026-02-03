"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Home,
    Users,
    MessageSquare,
    FileText,
    Target,
    Settings,
    TrendingUp
} from "lucide-react";

export default function Sidebar() {
    const pathname = usePathname();

    const navItems = [
        { href: "/world", icon: Home, label: "Dashboard" },
        { href: "/world/agents", icon: Users, label: "Agents" },
        { href: "/world/feed", icon: MessageSquare, label: "Feed" },
        { href: "/world/decisions", icon: Target, label: "Decisions" },
        { href: "/world/plans", icon: FileText, label: "Plans" },
        { href: "/world/evolution", icon: TrendingUp, label: "Evolution" },
        { href: "/world/settings", icon: Settings, label: "Settings" },
    ];

    const isActive = (href: string) => {
        if (href === "/world") {
            return pathname === "/world";
        }
        return pathname?.startsWith(href);
    };

    return (
        <aside className="w-64 bg-secondary/20 border-r border-border flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-border">
                <Link href="/world" className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-lg">🌍</span>
                    </div>
                    <span className="font-bold text-xl">AiEvollve</span>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${active
                                    ? "bg-primary text-primary-foreground shadow-md"
                                    : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                                }`}
                        >
                            <Icon className="w-5 h-5" />
                            <span className="font-medium">{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-border">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span>System Running</span>
                </div>
            </div>
        </aside>
    );
}
