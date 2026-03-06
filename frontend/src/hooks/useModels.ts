/** TanStack Query hook for configured model slots. */

import { useQuery } from "@tanstack/react-query";
import { getConfiguredModels } from "@/lib/api";

export function useConfiguredModels() {
    return useQuery({
        queryKey: ["models"],
        queryFn: getConfiguredModels,
        refetchInterval: 15_000, // Poll for health status
    });
}
