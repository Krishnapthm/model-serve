import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useCurrentUser } from "@/hooks/useAuth";
import { getAuthToken } from "@/lib/api";

export function ProtectedRoute() {
  const token = getAuthToken();
  const location = useLocation();
  const { data: user, isLoading, isError } = useCurrentUser();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
        Authenticating...
      </div>
    );
  }

  if (isError || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
