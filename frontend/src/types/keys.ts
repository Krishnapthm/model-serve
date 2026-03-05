/** Shared TypeScript types for API keys. */

export interface APIKey {
    id: string;
    name: string;
    key_prefix: string;
    created_at: string;
    last_used_at: string | null;
    is_active: boolean;
}

export interface CreateKeyRequest {
    name: string;
}

export interface CreatedKey {
    id: string;
    name: string;
    key: string;
    key_prefix: string;
    created_at: string;
}
