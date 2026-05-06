import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/common/Navbar";
import SearchPage from "./pages/SearchPage";
import BrowsePage from "./pages/BrowsePage";
import DatasetProfilePage from "./pages/DatasetProfilePage";
import DashboardPage from "./pages/DashboardPage";
import UploadModal from "./components/upload/UploadModal";
import { UiProvider } from "./contexts/UiProvider";

export default function App() {
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  return (
    <UiProvider>
      <div className="min-h-screen overflow-x-hidden bg-slate-50 text-slate-950 transition-colors dark:bg-[#060914] dark:text-slate-100">
        <Navbar onUploadClick={() => setUploadModalOpen(true)} />

        <main className="pt-16">
          <Routes>
            <Route index element={<SearchPage />} />
            <Route path="browse" element={<BrowsePage />} />
            <Route path="datasets/:id" element={<DatasetProfilePage />} />
            <Route path="datasets/:id/dashboard" element={<DashboardPage />} />
          </Routes>
        </main>

        <UploadModal
          isOpen={uploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
        />
      </div>
    </UiProvider>
  );
}
