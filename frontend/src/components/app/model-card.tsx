/** Model card for configured model slots. */

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/app/status-badge";
import { IconCopy, IconCheck } from "@tabler/icons-react";
import { toast } from "sonner";
import type { ServedModel } from "@/types/serve";

interface ModelCardProps {
  model: ServedModel;
}

export function ModelCard({ model }: ModelCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopySnippet = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(model.env_snippet);
    setCopied(true);
    toast.success("Copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="group hover:border-border transition-colors">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1 space-y-1.5">
            <div className="flex items-center gap-2">
              <h3
                className="font-medium text-sm truncate"
                title={model.display_name}
              >
                {model.display_name}
              </h3>
              <StatusBadge status={model.status} />
            </div>
            <p
              className="text-xs text-muted-foreground font-mono truncate"
              title={model.model_id}
            >
              {model.model_id}
            </p>
            <p className="text-xs text-muted-foreground font-mono">
              {model.endpoint_url}
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={handleCopySnippet}
            className="shrink-0"
          >
            {copied ? (
              <IconCheck size={15} className="mr-1" />
            ) : (
              <IconCopy size={15} className="mr-1" />
            )}
            {copied ? "Copied" : "Copy env"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
