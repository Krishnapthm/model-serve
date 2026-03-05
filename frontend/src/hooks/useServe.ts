/** TanStack Query hooks for model serving. */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getServedModels, serveModel, stopModel } from "@/lib/api";
import { toast } from "sonner";

export function useServedModels() {
    return useQuery({
        queryKey: ["served-models"],
        queryFn: getServedModels,
        staleTime: 30 * 1000, // 30s
        refetchInterval: (query) => {
            // Poll every 10s while any model is pending
            const data = query.state.data;
            if (data && data.some((m) => m.status === "pending")) {
                return 10_000;
            }
            return false;
        },
    });
}

export function useServeModel() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: serveModel,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["served-models"] });
            toast.success("Model serving started", {
                description: "Check the Served page for status.",
            });
        },
        onError: (err: Error) => {
            toast.error("Failed to serve model", { description: err.message });
        },
    });
}

export function useStopModel() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: stopModel,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["served-models"] });
            toast.success("Model stopped");
        },
        onError: (err: Error) => {
            toast.error("Failed to stop model", { description: err.message });
        },
    });
}
