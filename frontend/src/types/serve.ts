/** Shared TypeScript types for served models. */

export type ModelStatus = "pending" | "running" | "stopped" | "error";

export interface ServedModel {
    id: string;
    model_id: string;
    display_name: string;
    pipeline_tag: string | null;
    status: ModelStatus;
    endpoint_url: string | null;
    gpu_type: string;
    started_at: string;
    stopped_at: string | null;
    env_snippet?: {
        OPENAI_API_KEY: string;
        OPENAI_BASE_URL: string;
    };
}

export interface ServeRequest {
    model_id: string;
    gpu_type?: string;  // omit to let the server use its configured VLLM_GPU_TYPE
}
