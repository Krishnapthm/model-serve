/** Served models page — list running models with status and script dialog. */

import { useState } from "react";
import { useServedModels } from "@/hooks/useServe";
import { StatusBadge } from "@/components/app/status-badge";
import { ServeScriptDialog } from "@/components/app/serve-script-dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { IconServer } from "@tabler/icons-react";
import type { ServedModel } from "@/types/serve";

export default function ServedPage() {
  const { data: models, isLoading } = useServedModels();
  const [selectedModel, setSelectedModel] = useState<ServedModel | null>(null);
  const [scriptDialogOpen, setScriptDialogOpen] = useState(false);

  const openScriptDialog = (model: ServedModel) => {
    setSelectedModel(model);
    setScriptDialogOpen(true);
  };

  const handleScriptDialogOpenChange = (open: boolean) => {
    setScriptDialogOpen(open);
    if (!open) {
      setSelectedModel(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">
            Served Models
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Running model instances
          </p>
        </div>
        <div className="grid gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Served Models</h2>
        <p className="text-sm text-muted-foreground mt-1">
          {models && models.length > 0
            ? `${models.filter((m) => m.status === "running").length} running`
            : "No models served yet"}
        </p>
      </div>

      <ScrollArea className="h-[calc(100vh-200px)]">
        <div className="grid gap-4 pr-3">
          {!models || models.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="py-12 text-center">
                <IconServer
                  size={40}
                  className="mx-auto text-muted-foreground mb-3"
                />
                <p className="text-sm text-muted-foreground">
                  No models served yet. Configure models via environment
                  variables.
                </p>
              </CardContent>
            </Card>
          ) : (
            models.map((model) => (
              <Card
                key={model.slot}
                role="button"
                tabIndex={0}
                onClick={() => openScriptDialog(model)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    openScriptDialog(model);
                  }
                }}
                className="cursor-pointer hover:border-border transition-colors"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-base">
                        {model.display_name}
                      </CardTitle>
                      <p className="text-xs text-muted-foreground font-mono">
                        {model.model_id}
                      </p>
                    </div>
                    <StatusBadge status={model.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground font-mono">
                    {model.endpoint_url}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Click to view a copy-paste Python example script.
                  </p>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      <ServeScriptDialog
        model={selectedModel}
        open={scriptDialogOpen}
        onOpenChange={handleScriptDialogOpenChange}
      />
    </div>
  );
}
