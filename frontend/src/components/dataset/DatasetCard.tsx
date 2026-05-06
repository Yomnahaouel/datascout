import { Link } from "react-router-dom";
import type { Dataset } from "../../types/dataset";
import QualityBadge from "../common/QualityBadge";

interface DatasetCardProps {
  dataset: Dataset;
}

export default function DatasetCard({ dataset }: DatasetCardProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const getFormatIcon = (format: string) => {
    const icons: Record<string, string> = {
      csv: "📊",
      tsv: "📊",
      json: "📋",
      parquet: "⚡",
      excel: "📗",
    };
    return icons[format] || "📄";
  };

  return (
    <Link
      to={`/datasets/${dataset.id}`}
      className="block bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-blue-300 transition-all group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{getFormatIcon(dataset.file_format)}</span>
            <h3 className="font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
              {dataset.name}
            </h3>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <span>{dataset.row_count?.toLocaleString() ?? "—"} rows</span>
            <span>•</span>
            <span>{dataset.column_count ?? "—"} cols</span>
            <span>•</span>
            <span>{formatFileSize(dataset.file_size)}</span>
          </div>
        </div>
        <QualityBadge score={dataset.quality_score} size="sm" />
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
        <span>{formatDate(dataset.created_at)}</span>
        {dataset.status === "processing" && (
          <span className="flex items-center gap-1 text-blue-500">
            <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Processing
          </span>
        )}
        {dataset.status === "failed" && (
          <span className="text-red-500">Failed</span>
        )}
      </div>
    </Link>
  );
}
