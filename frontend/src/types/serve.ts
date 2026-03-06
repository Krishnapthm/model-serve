/** Shared TypeScript types for served models. */

export type ModelStatus = "running" | "loading";

export interface ServedModel {
  slot: number;
  model_id: string;
  display_name: string;
  endpoint_url: string;
  status: ModelStatus;
  env_snippet: string;
}
