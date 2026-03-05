/** Axios API client with typed methods for all backend endpoints. */

import axios from "axios";
import type { ModelSummary, ModelDetail } from "@/types/models";
import type { ServedModel, ServeRequest } from "@/types/serve";
import type { APIKey, CreatedKey } from "@/types/keys";
import type { PaginatedResponse, DataResponse } from "@/types/api";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
    headers: { "Content-Type": "application/json" },
});

/** Set the API key for all subsequent requests. */
export function setApiKey(key: string) {
    api.defaults.headers.common["X-API-Key"] = key;
}

/** Get the currently set API key. */
export function getApiKey(): string | undefined {
    return api.defaults.headers.common["X-API-Key"] as string | undefined;
}

// --- Models ---

export async function getModels(
    category?: string,
    q?: string,
    page = 1,
    pageSize = 20
): Promise<PaginatedResponse<ModelSummary>> {
    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (category) params.category = category;
    if (q) params.q = q;
    const { data } = await api.get<PaginatedResponse<ModelSummary>>("/models", { params });
    return data;
}

export async function getModel(modelId: string): Promise<ModelDetail> {
    const { data } = await api.get<DataResponse<ModelDetail>>(`/models/${modelId}`);
    return data.data;
}

// --- Serve ---

export async function serveModel(req: ServeRequest): Promise<ServedModel> {
    const { data } = await api.post<DataResponse<ServedModel>>("/serve", req);
    return data.data;
}

export async function getServedModels(): Promise<ServedModel[]> {
    const { data } = await api.get<DataResponse<ServedModel[]>>("/serve");
    return data.data;
}

export async function getServedModel(id: string): Promise<ServedModel> {
    const { data } = await api.get<DataResponse<ServedModel>>(`/serve/${id}`);
    return data.data;
}

export async function stopModel(id: string): Promise<void> {
    await api.delete(`/serve/${id}`);
}

// --- Keys ---

export async function createKey(name: string): Promise<CreatedKey> {
    const { data } = await api.post<DataResponse<CreatedKey>>("/keys", { name });
    return data.data;
}

export async function getKeys(): Promise<APIKey[]> {
    const { data } = await api.get<DataResponse<APIKey[]>>("/keys");
    return data.data;
}

export async function revokeKey(id: string): Promise<void> {
    await api.delete(`/keys/${id}`);
}

// --- Health ---

export async function healthCheck(): Promise<{ status: string }> {
    const { data } = await api.get("/health");
    return data;
}
