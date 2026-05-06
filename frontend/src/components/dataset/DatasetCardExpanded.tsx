import { Link } from "react-router-dom";
import type { Dataset } from "../../types/dataset";
import QualityBadge from "../common/QualityBadge";
import TagBadge from "../common/TagBadge";

interface DatasetCardExpandedProps {
  dataset: Dataset;
  tags?: { value: string; category: "domain" | "data_type" | "pii_type" | "custom" }[];
}

export default function DatasetCardExpanded({ dataset, tags = [] }: DatasetCardExpandedProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-700";
      case "processing":
        return "bg-blue-100 text-blue-700";
      case "failed":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const getFormatColor = (format: string) => {
    const colors: Record<string, string> = {
      csv: "bg-emerald-100 text-emerald-700",
      tsv: "bg-emerald-100 text-emerald-700",
      json: "bg-amber-100 text-amber-700",
      parquet: "bg-purple-100 text-purple-700",
      excel: "bg-green-100 text-green-700",
    };
    return colors[format] || "bg-gray-100 text-gray-700";
  };

  // Mock tags if none provided
  const displayTags = tags.length > 0 ? tags : [
    { value: "Finance", category: "domain" as const },
  ];

  const hasPII = displayTags.some((t) => t.category === "pii_type");

  return (
    <Link
      to={`/datasets/${dataset.id}`}
      className="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-blue-300 transition-all group"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
            {dataset.name}
          </h3>
          {dataset.description && (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">
              {dataset.description}
            </p>
          )}
        </div>
        <QualityBadge score={dataset.quality_score} size="md" />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Rows</p>
          <p className="text-sm font-semibold text-gray-900">
            {dataset.row_count?.toLocaleString() ?? "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Columns</p>
          <p className="text-sm font-semibold text-gray-900">
            {dataset.column_count ?? "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Size</p>
          <p className="text-sm font-semibold text-gray-900">
            {formatFileSize(dataset.file_size)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Added</p>
          <p className="text-sm font-semibold text-gray-900">
            {formatDate(dataset.created_at)}
          </p>
        </div>
      </div>

      {/* Tags and badges */}
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`px-2 py-1 rounded text-xs font-medium uppercase ${getFormatColor(dataset.file_format)}`}
        >
          {dataset.file_format}
        </span>
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(dataset.status)}`}
        >
          {dataset.status}
        </span>
        {displayTags.slice(0, 3).map((tag, i) => (
          <TagBadge key={i} value={tag.value} category={tag.category} />
        ))}
        {hasPII && (
          <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700 flex items-center gap-1">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            PII
          </span>
        )}
      </div>
    </Link>
  );
}
