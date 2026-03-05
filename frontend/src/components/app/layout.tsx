/** App layout with sidebar navigation. */

import { NavLink, Outlet } from "react-router-dom";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    IconBox,
    IconServer,
    IconKey,
} from "@tabler/icons-react";

const NAV_ITEMS = [
    { to: "/models", label: "Models", icon: IconBox },
    { to: "/served", label: "Served", icon: IconServer },
    { to: "/keys", label: "API Keys", icon: IconKey },
];

export function Layout() {
    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Sidebar */}
            <aside className="w-56 border-r border-border/50 flex flex-col bg-background/80 backdrop-blur-md">
                <div className="p-4 border-b border-border/50">
                    <h1 className="text-lg font-semibold tracking-tight">
                        ModelServe
                    </h1>
                    <p className="text-xs text-muted-foreground mt-0.5">
                        GPU Model Serving
                    </p>
                </div>
                <nav className="flex-1 p-2 space-y-1">
                    {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
                        <NavLink
                            key={to}
                            to={to}
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                                    ? "bg-accent text-accent-foreground"
                                    : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                                }`
                            }
                        >
                            <Icon size={18} stroke={1.5} />
                            {label}
                        </NavLink>
                    ))}
                </nav>
            </aside>

            {/* Main content */}
            <main className="flex-1 flex flex-col min-w-0">
                <ScrollArea className="flex-1">
                    <div className="p-6 max-w-6xl">
                        <Outlet />
                    </div>
                </ScrollArea>
            </main>
        </div>
    );
}
