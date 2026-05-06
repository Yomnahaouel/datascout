import { useEffect, useState, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { getDataset, getDatasetProfile, getDatasetPreview, deleteDataset } from "../services/api";
import type { DatasetDetail, ColumnProfile, DataPreview } from "../types/dataset";
import DatasetHeader from "../components/dataset/DatasetHeader";
import KPICard from "../components/common/KPICard";
import QualityBreakdown from "../components/dataset/QualityBreakdown";
import ColumnProfileTable from "../components/dataset/ColumnProfileTable";
import DataPreviewTable from "../components/dataset/DataPreviewTable";
import LoadingSpinner from "../components/common/LoadingSpinner";

export default function DatasetProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState<DatasetDetail | null>(null);
  const [columns, setColumns] = useState<ColumnProfile[]>([]);
  const [preview, setPreview] = useState<DataPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [activeTab, setActiveTab] = useState<"columns" | "preview" | "quality">("columns");

  useEffect(() => {
    if (!id) return;
    const numId = Number(id);
    queueMicrotask(() => setLoading(true));
    Promise.all([
      getDataset(numId),
      getDatasetProfile(numId),
      getDatasetPreview(numId),
    ])
      .then(([datasetData, profileData, previewData]) => {
        setDataset(datasetData);
        setColumns(profileData); // getDatasetProfile returns ColumnProfile[] directly
        setPreview(previewData);
      })
      .catch((err) => {
        console.error("Failed to load dataset:", err);
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = useCallback(async () => {
    if (!id || !dataset || !window.confirm(`Delete dataset "${dataset.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteDataset(dataset.id);
      navigate("/browse");
    } catch (err) {
      console.error("Delete failed:", err);
      setDeleting(false);
    }
  }, [id, dataset, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Dataset not found</h2>
        <p className="text-gray-500 mb-4">The dataset you're looking for doesn't exist.</p>
        <Link to="/browse" className="text-blue-600 hover:underline">
          ← Back to browse
        </Link>
      </div>
    );
  }

  const piiCount = columns.filter((c) => c.is_pii).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <nav className="flex items-center gap-2 text-sm">
            <Link to="/browse" className="text-gray-500 hover:text-gray-700">
              Datasets
            </Link>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-gray-900 font-medium">{dataset.name}</span>
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <DatasetHeader
          dataset={dataset}
          onViewDashboard={() => {}}
          onDelete={handleDelete}
          onDeleteLoading={deleting}
        />

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <KPICard
            label="Total Rows"
            value={dataset.row_count ?? "N/A"}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            }
          />
          <KPICard
            label="Columns"
            value={dataset.column_count ?? columns.length}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
            }
          />
          <KPICard
            label="Quality Score"
            value={dataset.quality_score !== null ? `${dataset.quality_score}%` : "N/A"}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <KPICard
            label="PII Fields"
            value={piiCount}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          />
        </div>

        {/* Tabs */}
        <div className="mt-8">
          <div className="border-b border-gray-200">
            <nav className="flex gap-8">
              <button
                onClick={() => setActiveTab("columns")}
                className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "columns"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Column Profile
              </button>
              <button
                onClick={() => setActiveTab("preview")}
                className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "preview"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Data Preview
              </button>
              <button
                onClick={() => setActiveTab("quality")}
                className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "quality"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Quality Details
              </button>
            </nav>
          </div>

          <div className="mt-6">
            {activeTab === "columns" && (
              <ColumnProfileTable profiles={columns} />
            )}

            {activeTab === "preview" && preview && (
              <DataPreviewTable preview={preview} />
            )}

            {activeTab === "quality" && dataset.quality_score_detail && (
              <QualityBreakdown quality={dataset.quality_score_detail} />
            )}
          </div>
        </div>

        {/* Dashboard Link */}
        <div className="mt-8 p-6 bg-white rounded-xl border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">Auto-Generated Dashboard</h3>
              <p className="text-sm text-gray-500 mt-1">
                View automatically generated visualizations based on column types
              </p>
            </div>
            <Link
              to={`/datasets/${id}/dashboard`}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              View Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
