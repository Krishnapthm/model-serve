/** Status badge for served model status. */

import { Badge } from "@/components/ui/badge";
import type { ModelStatus } from "@/types/serve";

const STATUS_CONFIG: Record<ModelStatus, { label: string; className: string }> = {
    pending: {
        label: "Pending",
        className: "bg-yellow-500/15 text-yellow-600 border-yellow-500/30 animate-pulse",
    },
    running: {
        label: "Running",
        className: "bg-emerald-500/15 text-emerald-600 border-emerald-500/30",
    },
    stopped: {
        label: "Stopped",
        className: "bg-zinc-500/15 text-zinc-500 border-zinc-500/30",
    },
    error: {
        label: "Error",
        className: "bg-red-500/15 text-red-600 border-red-500/30",
    },
};

interface StatusBadgeProps {
    status: ModelStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
    const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.stopped;
    return (
        <Badge variant="outline" className={config.className}>
            {config.label}
        </Badge>
    );
}
