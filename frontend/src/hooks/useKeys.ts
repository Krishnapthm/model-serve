/** TanStack Query hooks for API keys. */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getKeys, createKey, revokeKey } from "@/lib/api";
import { toast } from "sonner";

export function useApiKeys() {
    return useQuery({
        queryKey: ["api-keys"],
        queryFn: getKeys,
        staleTime: 0, // Always fresh after mutations
    });
}

export function useCreateKey() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (name: string) => createKey(name),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
        },
        onError: (err: Error) => {
            toast.error("Failed to create key", { description: err.message });
        },
    });
}

export function useRevokeKey() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: revokeKey,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
            toast.success("API key revoked");
        },
        onError: (err: Error) => {
            toast.error("Failed to revoke key", { description: err.message });
        },
    });
}
