/** Shared TypeScript types for user authentication. */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
  is_active: boolean;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthSession {
  access_token: string;
  token_type: "bearer";
  user: User;
}
