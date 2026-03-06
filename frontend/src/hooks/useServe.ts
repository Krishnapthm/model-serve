/** TanStack Query hooks for served models. */

import { useQuery } from "@tanstack/react-query";
import { getServedModels } from "@/lib/api";

export function useServedModels() {
    return useQuery({
        queryKey: ["served-models"],
        queryFn: getServedModels,
        staleTime: 30 * 1000, // 30s
        refetchInterval: (query) => {
            // Poll every 10s while any model is loading
            const data = query.state.data;
            if (data && data.some((m) => m.status === "loading")) {
                return 10_000;
            }
            return false;
        },
    });
}
