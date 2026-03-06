/** Models page — display configured model slots with status. */

import { useConfiguredModels } from "@/hooks/useModels";
import { ModelCard } from "@/components/app/model-card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";

export default function ModelsPage() {
    const { data: models, isLoading } = useConfiguredModels();

    return (
        <div className="space-y-4">
            <div>
                <h2 className="text-2xl font-semibold tracking-tight">Models</h2>
                <p className="text-sm text-muted-foreground mt-1">
                    Configured model slots managed by Docker Compose
                </p>
            </div>

            {isLoading ? (
                <div className="grid gap-3">
                    {Array.from({ length: 4 }).map((_, i) => (
                        <Skeleton key={i} className="h-24 w-full rounded-lg" />
                    ))}
                </div>
            ) : (
                <ScrollArea className="h-[calc(100vh-200px)]">
                    <div className="grid gap-3 pr-3">
                        {!models || models.length === 0 ? (
                            <p className="text-sm text-muted-foreground py-8 text-center">
                                No model slots configured. Configure models via environment variables.
                            </p>
                        ) : (
                            models.map((model) => (
                                <ModelCard key={model.slot} model={model} />
                            ))
                        )}
                    </div>
                </ScrollArea>
            )}
        </div>
    );
}
