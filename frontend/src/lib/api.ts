/** Axios API client with typed methods for all backend endpoints. */

import axios from "axios";
import type { ModelSummary, ModelDetail } from "@/types/models";
import type { ServedModel, ServeRequest } from "@/types/serve";
import type { APIKey, CreatedKey } from "@/types/keys";
import type {
  AuthSession,
  LoginRequest,
  SignupRequest,
  User,
} from "@/types/auth";
import type { PaginatedResponse, DataResponse } from "@/types/api";

function resolveApiBaseUrl() {
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  if (envBaseUrl) {
    return envBaseUrl;
  }

  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
  }

  return "http://localhost:8000/api/v1";
}

const api = axios.create({
  baseURL: resolveApiBaseUrl(),
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error?.response?.data?.detail;
    const message =
      typeof detail === "string" ? detail : error.message || "Request failed";
    return Promise.reject(new Error(message));
  },
);

/** Set or clear bearer auth token for all subsequent requests. */
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

/** Get the currently set bearer auth token (without Bearer prefix). */
export function getAuthToken(): string | undefined {
  const header = api.defaults.headers.common.Authorization as
    | string
    | undefined;
  if (!header) return undefined;
  return header.startsWith("Bearer ") ? header.slice(7) : header;
}

// --- Auth ---

export async function signup(payload: SignupRequest): Promise<AuthSession> {
  const { data } = await api.post<DataResponse<AuthSession>>(
    "/auth/signup",
    payload,
  );
  return data.data;
}

export async function login(payload: LoginRequest): Promise<AuthSession> {
  const { data } = await api.post<DataResponse<AuthSession>>(
    "/auth/login",
    payload,
  );
  return data.data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<DataResponse<User>>("/auth/me");
  return data.data;
}

// --- Models ---

export async function getModels(
  category?: string,
  q?: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<ModelSummary>> {
  const params: Record<string, string | number> = { page, page_size: pageSize };
  if (category) params.category = category;
  if (q) params.q = q;
  const { data } = await api.get<PaginatedResponse<ModelSummary>>("/models", {
    params,
  });
  return data;
}

export async function getModel(modelId: string): Promise<ModelDetail> {
  const { data } = await api.get<DataResponse<ModelDetail>>(
    `/models/${modelId}`,
  );
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
