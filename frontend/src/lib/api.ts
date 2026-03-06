/** Axios API client with typed methods for all backend endpoints. */

import axios from "axios";
import type { ServedModel } from "@/types/serve";
import type { APIKey, CreatedKey } from "@/types/keys";
import type {
  AuthSession,
  LoginRequest,
  SignupRequest,
  User,
} from "@/types/auth";
import type { DataResponse } from "@/types/api";

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

/** Get all configured model slots with health status (public). */
export async function getConfiguredModels(): Promise<ServedModel[]> {
  const { data } = await api.get<DataResponse<ServedModel[]>>("/models");
  return data.data;
}

/** Get a single model slot (public). */
export async function getConfiguredModel(slot: number): Promise<ServedModel> {
  const { data } = await api.get<DataResponse<ServedModel>>(
    `/models/${slot}`,
  );
  return data.data;
}

// --- Serve ---

/** Get served models (authenticated). */
export async function getServedModels(): Promise<ServedModel[]> {
  const { data } = await api.get<DataResponse<ServedModel[]>>("/serve");
  return data.data;
}

/** Get a single served model slot (authenticated). */
export async function getServedModel(slot: number): Promise<ServedModel> {
  const { data } = await api.get<DataResponse<ServedModel>>(`/serve/${slot}`);
  return data.data;
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
