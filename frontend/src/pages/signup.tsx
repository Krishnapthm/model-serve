import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { SignupForm } from "@/components/signup-form";
import { useCurrentUser, useSignup } from "@/hooks/useAuth";
import type { SignupRequest } from "@/types/auth";

export default function SignupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname ?? "/models";

  const { data: user } = useCurrentUser();
  const signupMutation = useSignup();

  if (user) {
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (payload: SignupRequest) => {
    await signupMutation.mutateAsync(payload);
    navigate(redirectTo, { replace: true });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <SignupForm
        className="w-full max-w-md"
        onSubmit={handleSubmit}
        isLoading={signupMutation.isPending}
        errorMessage={signupMutation.error?.message}
      />
    </div>
  );
}
