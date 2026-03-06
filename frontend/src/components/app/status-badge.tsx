/** Status badge for served model status. */

import { Badge } from "@/components/ui/badge";
import type { ModelStatus } from "@/types/serve";

const STATUS_CONFIG: Record<ModelStatus, { label: string; className: string }> =
  {
    running: {
      label: "Running",
      className: "bg-emerald-500/15 text-emerald-600 border-emerald-500/30",
    },
    loading: {
      label: "Loading",
      className:
        "bg-yellow-500/15 text-yellow-600 border-yellow-500/30 animate-pulse",
    },
  };

interface StatusBadgeProps {
  status: ModelStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
