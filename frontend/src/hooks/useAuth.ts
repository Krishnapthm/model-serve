/** TanStack Query hooks for dashboard authentication. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { getAuthToken, getMe, login, setAuthToken, signup } from "@/lib/api";
import type { LoginRequest, SignupRequest } from "@/types/auth";

const AUTH_STORAGE_KEY = "modelserve.auth.token";
const AUTH_QUERY_KEY = ["auth", "me"] as const;

function persistAuthToken(token: string) {
  localStorage.setItem(AUTH_STORAGE_KEY, token);
  setAuthToken(token);
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_STORAGE_KEY);
  setAuthToken(null);
}

export function initializeAuthFromStorage() {
  const token = localStorage.getItem(AUTH_STORAGE_KEY);
  if (token) {
    setAuthToken(token);
  }
}

export function useCurrentUser() {
  const token = getAuthToken();
  return useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: getMe,
    enabled: Boolean(token),
    retry: false,
    staleTime: 60 * 1000,
  });
}

export function useSignup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SignupRequest) => signup(payload),
    onSuccess: (session) => {
      persistAuthToken(session.access_token);
      queryClient.setQueryData(AUTH_QUERY_KEY, session.user);
      toast.success("Account created");
    },
    onError: (err: Error) => {
      toast.error("Signup failed", { description: err.message });
    },
  });
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: LoginRequest) => login(payload),
    onSuccess: (session) => {
      persistAuthToken(session.access_token);
      queryClient.setQueryData(AUTH_QUERY_KEY, session.user);
      toast.success("Logged in");
    },
    onError: (err: Error) => {
      toast.error("Login failed", { description: err.message });
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return () => {
    clearAuthSession();
    queryClient.clear();
  };
}
