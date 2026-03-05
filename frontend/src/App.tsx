import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "@/components/app/layout";
import { ProtectedRoute } from "@/components/app/protected-route";
import ModelsPage from "@/pages/models";
import ServedPage from "@/pages/served";
import KeysPage from "@/pages/keys";
import LoginPage from "@/pages/login";
import SignupPage from "@/pages/signup";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/served" element={<ServedPage />} />
          <Route path="/keys" element={<KeysPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
