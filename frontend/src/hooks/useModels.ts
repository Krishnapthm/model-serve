/** TanStack Query hooks for HuggingFace models. */

import { useQuery } from "@tanstack/react-query";
import { getModels, getModel } from "@/lib/api";

export function useModels(category?: string, q?: string, page = 1, pageSize = 20) {
    return useQuery({
        queryKey: ["models", category, q, page, pageSize],
        queryFn: () => getModels(category, q, page, pageSize),
        staleTime: 5 * 60 * 1000, // 5 min — HF model list doesn't change often
        gcTime: 30 * 60 * 1000,
    });
}

export function useModel(modelId: string) {
    return useQuery({
        queryKey: ["model", modelId],
        queryFn: () => getModel(modelId),
        staleTime: 5 * 60 * 1000,
        enabled: !!modelId,
    });
}
