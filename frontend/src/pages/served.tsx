/** Served models page — list running models, status, env snippets, stop. */

import { useServedModels, useStopModel } from "@/hooks/useServe";
import { StatusBadge } from "@/components/app/status-badge";
import { EnvSnippet } from "@/components/app/env-snippet";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { IconPlayerStop, IconServer } from "@tabler/icons-react";

export default function ServedPage() {
    const { data: models, isLoading } = useServedModels();
    const stopMutation = useStopModel();

    if (isLoading) {
        return (
            <div className="space-y-4">
                <div>
                    <h2 className="text-2xl font-semibold tracking-tight">Served Models</h2>
                    <p className="text-sm text-muted-foreground mt-1">Running model instances</p>
                </div>
                <div className="grid gap-3">
                    {Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-40 w-full rounded-lg" />
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
                                <IconServer size={40} className="mx-auto text-muted-foreground mb-3" />
                                <p className="text-sm text-muted-foreground">
                                    No models served yet. Go to Models to serve one.
                                </p>
                            </CardContent>
                        </Card>
                    ) : (
                        models.map((model) => (
                            <Card key={model.id}>
                                <CardHeader className="pb-3">
                                    <div className="flex items-center justify-between">
                                        <div className="space-y-1">
                                            <CardTitle className="text-base">{model.display_name}</CardTitle>
                                            <p className="text-xs text-muted-foreground font-mono">{model.model_id}</p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <StatusBadge status={model.status} />
                                            {(model.status === "running" || model.status === "pending") && (
                                                <AlertDialog>
                                                    <AlertDialogTrigger asChild>
                                                        <Button size="sm" variant="outline" className="text-destructive">
                                                            <IconPlayerStop size={14} className="mr-1" />
                                                            Stop
                                                        </Button>
                                                    </AlertDialogTrigger>
                                                    <AlertDialogContent className="backdrop-blur-md bg-background/80 border border-border/50">
                                                        <AlertDialogHeader>
                                                            <AlertDialogTitle>Stop {model.display_name}?</AlertDialogTitle>
                                                            <AlertDialogDescription>
                                                                This will stop the model and remove its container. Any clients using
                                                                this endpoint will lose access.
                                                            </AlertDialogDescription>
                                                        </AlertDialogHeader>
                                                        <AlertDialogFooter>
                                                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                            <AlertDialogAction
                                                                onClick={() => stopMutation.mutate(model.id)}
                                                                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                                            >
                                                                Stop Model
                                                            </AlertDialogAction>
                                                        </AlertDialogFooter>
                                                    </AlertDialogContent>
                                                </AlertDialog>
                                            )}
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    {model.env_snippet && model.status === "running" && (
                                        <EnvSnippet
                                            apiKey={model.env_snippet.OPENAI_API_KEY}
                                            baseUrl={model.env_snippet.OPENAI_BASE_URL}
                                        />
                                    )}
                                    <div className="flex gap-4 mt-3 text-xs text-muted-foreground">
                                        <span>GPU: {model.gpu_type.toUpperCase()}</span>
                                        <span>Started: {new Date(model.started_at).toLocaleString()}</span>
                                        {model.stopped_at && (
                                            <span>Stopped: {new Date(model.stopped_at).toLocaleString()}</span>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            </ScrollArea>
        </div>
    );
}
