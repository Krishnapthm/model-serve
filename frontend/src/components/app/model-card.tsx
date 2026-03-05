/** Model card for model list items. */

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { IconRocket, IconDownload, IconHeart } from "@tabler/icons-react";
import type { ModelSummary } from "@/types/models";

const BADGE_COLORS: Record<string, string> = {
    blue: "bg-blue-500/15 text-blue-600 border-blue-500/30",
    purple: "bg-purple-500/15 text-purple-600 border-purple-500/30",
    pink: "bg-pink-500/15 text-pink-600 border-pink-500/30",
    orange: "bg-orange-500/15 text-orange-600 border-orange-500/30",
    green: "bg-emerald-500/15 text-emerald-600 border-emerald-500/30",
    cyan: "bg-cyan-500/15 text-cyan-600 border-cyan-500/30",
    gray: "bg-zinc-500/15 text-zinc-500 border-zinc-500/30",
};

function formatNumber(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
    return String(n);
}

interface ModelCardProps {
    model: ModelSummary;
    onServe: (modelId: string) => void;
    isServing?: boolean;
}

export function ModelCard({ model, onServe, isServing }: ModelCardProps) {
    return (
        <Card className="group hover:border-border transition-colors">
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 mb-1.5">
                            <Badge
                                variant="outline"
                                className={BADGE_COLORS[model.badge_color] ?? BADGE_COLORS.gray}
                            >
                                {model.label}
                            </Badge>
                        </div>
                        <h3 className="font-medium text-sm truncate" title={model.id}>
                            {model.id}
                        </h3>
                        {model.description && (
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                {model.description}
                            </p>
                        )}
                        <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                                <IconDownload size={13} /> {formatNumber(model.downloads)}
                            </span>
                            <span className="flex items-center gap-1">
                                <IconHeart size={13} /> {formatNumber(model.likes)}
                            </span>
                        </div>
                    </div>
                    <Button
                        size="sm"
                        onClick={() => onServe(model.id)}
                        disabled={isServing}
                        className="shrink-0"
                    >
                        <IconRocket size={15} className="mr-1" />
                        Serve
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
