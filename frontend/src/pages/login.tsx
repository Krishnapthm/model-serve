import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { LoginForm } from "@/components/login-form";
import { useCurrentUser, useLogin } from "@/hooks/useAuth";
import type { LoginRequest } from "@/types/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname ?? "/models";

  const { data: user } = useCurrentUser();
  const loginMutation = useLogin();

  if (user) {
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (payload: LoginRequest) => {
    await loginMutation.mutateAsync(payload);
    navigate(redirectTo, { replace: true });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <LoginForm
        className="w-full max-w-md"
        onSubmit={handleSubmit}
        isLoading={loginMutation.isPending}
        errorMessage={loginMutation.error?.message}
      />
    </div>
  );
}
