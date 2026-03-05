import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "@/components/app/layout";
import ModelsPage from "@/pages/models";
import ServedPage from "@/pages/served";
import KeysPage from "@/pages/keys";

export function App() {
    return (
        <Routes>
            <Route element={<Layout />}>
                <Route path="/" element={<Navigate to="/models" replace />} />
                <Route path="/models" element={<ModelsPage />} />
                <Route path="/served" element={<ServedPage />} />
                <Route path="/keys" element={<KeysPage />} />
            </Route>
        </Routes>
    );
}

export default App;