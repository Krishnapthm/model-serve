/** Models page — browse HuggingFace models with category tabs and search. */

import { useState, useMemo } from "react";
import { useModels } from "@/hooks/useModels";
import { useServeModel } from "@/hooks/useServe";
import { ModelCard } from "@/components/app/model-card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { CATEGORY_LABELS } from "@/types/models";
import { IconSearch } from "@tabler/icons-react";

const CATEGORIES = [
    { value: undefined, label: "All" },
    ...Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label })),
];

export default function ModelsPage() {
    const [category, setCategory] = useState<string | undefined>(undefined);
    const [search, setSearch] = useState("");
    const [debouncedSearch, setDebouncedSearch] = useState("");

    // Debounce search input
    const debounceTimer = useMemo(() => {
        return (value: string) => {
            const timeout = setTimeout(() => setDebouncedSearch(value), 250);
            return () => clearTimeout(timeout);
        };
    }, []);

    const handleSearchChange = (value: string) => {
        setSearch(value);
        debounceTimer(value);
    };

    const { data, isLoading } = useModels(category, debouncedSearch || undefined);
    const serveMutation = useServeModel();

    // Client-side search filter on cached data
    const filteredModels = useMemo(() => {
        if (!data?.data) return [];
        if (!search) return data.data;
        const q = search.toLowerCase();
        return data.data.filter(
            (m) =>
                m.id.toLowerCase().includes(q) ||
                m.description?.toLowerCase().includes(q)
        );
    }, [data?.data, search]);

    return (
        <div className="space-y-4">
            <div>
                <h2 className="text-2xl font-semibold tracking-tight">Models</h2>
                <p className="text-sm text-muted-foreground mt-1">
                    Browse HuggingFace models and serve them with one click
                </p>
            </div>

            {/* Search */}
            <div className="relative max-w-md">
                <IconSearch
                    size={16}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                />
                <Input
                    placeholder="Search models..."
                    value={search}
                    onChange={(e) => handleSearchChange(e.target.value)}
                    className="pl-9"
                />
            </div>

            {/* Category tabs */}
            <div className="flex gap-1.5 flex-wrap">
                {CATEGORIES.map((cat) => (
                    <button
                        key={cat.label}
                        onClick={() => setCategory(cat.value)}
                        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${category === cat.value
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted text-muted-foreground hover:bg-accent hover:text-foreground"
                            }`}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>

            {/* Model list */}
            {isLoading ? (
                <div className="grid gap-3">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <Skeleton key={i} className="h-24 w-full rounded-lg" />
                    ))}
                </div>
            ) : (
                <ScrollArea className="h-[calc(100vh-280px)]">
                    <div className="grid gap-3 pr-3">
                        {filteredModels.length === 0 ? (
                            <p className="text-sm text-muted-foreground py-8 text-center">
                                No models found. Try a different search or category.
                            </p>
                        ) : (
                            filteredModels.map((model) => (
                                <ModelCard
                                    key={model.id}
                                    model={model}
                                    onServe={(id) => serveMutation.mutate({ model_id: id })}
                                    isServing={serveMutation.isPending}
                                />
                            ))
                        )}
                    </div>
                </ScrollArea>
            )}

            {/* Pagination info */}
            {data?.meta && (
                <p className="text-xs text-muted-foreground">
                    Showing {filteredModels.length} of {data.meta.total} models
                </p>
            )}
        </div>
    );
}
