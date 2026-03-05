/** Shared TypeScript types for HuggingFace models. */

export interface ModelSummary {
  id: string;
  name: string;
  pipeline_tag: string | null;
  description: string | null;
  downloads: number;
  likes: number;
  label: string;
  badge_color: string;
}

export interface ModelDetail extends ModelSummary {
  model_card_url: string;
  library_name: string | null;
  tags: string[];
}

export type ModelCategory =
  | "text-generation"
  | "feature-extraction"
  | "text-to-image"
  | "text-to-video"
  | "automatic-speech-recognition"
  | "image-to-text";

export const CATEGORY_LABELS: Record<string, string> = {
  "text-generation": "LLM",
  "feature-extraction": "Text Embedding",
  "text-to-image": "Image Generation",
  "text-to-video": "Video Generation",
  "automatic-speech-recognition": "Speech-to-Text",
  "image-to-text": "Vision-Language",
};
