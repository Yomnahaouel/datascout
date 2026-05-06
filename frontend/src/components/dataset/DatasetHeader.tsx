import { Link } from "react-router-dom";
import type { Dataset, Tag } from "../../types/dataset";
import QualityBadge from "../common/QualityBadge";
import TagBadge from "../common/TagBadge";

interface DatasetHeaderProps {
  dataset: Dataset;
  tags?: Tag[];
  onViewDashboard?: () => void;
  onDownload?: () => void;
  onDelete?: () => void;
  onDeleteLoading?: boolean;
}

export default function DatasetHeader({
  dataset,
  tags = [],
  onViewDashboard,
  onDownload,
  onDelete,
  onDeleteLoading = false,
}: DatasetHeaderProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const domainTags = tags.filter((t) => t.category === "domain");
  const piiTags = tags.filter((t) => t.category === "pii_type");

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      {/* Back link */}
      <Link
        to="/browse"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to Browse
      </Link>

      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-gray-900 truncate">
              {dataset.name}
            </h1>
            <QualityBadge score={dataset.quality_score} size="lg" />
          </div>

          {dataset.description && (
            <p className="text-gray-600 mb-4">{dataset.description}</p>
          )}

          {/* Tags */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-2 py-1 rounded text-xs font-medium uppercase bg-gray-100 text-gray-700">
              {dataset.file_format}
            </span>
            <span className="text-gray-300">|</span>
            <span className="text-sm text-gray-500">
              {formatFileSize(dataset.file_size)}
            </span>
            {domainTags.length > 0 && (
              <>
                <span className="text-gray-300">|</span>
                {domainTags.slice(0, 3).map((tag) => (
                  <TagBadge
                    key={tag.id}
                    value={tag.value}
                    category={tag.category}
                    confidence={tag.confidence}
                  />
                ))}
              </>
            )}
            {piiTags.length > 0 && (
              <>
                <span className="text-gray-300">|</span>
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Contains PII ({piiTags.length} types)
                </span>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {onViewDashboard && (
            <Link
              to={`/datasets/${dataset.id}/dashboard`}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              View Dashboard
            </Link>
          )}

          {onDownload && (
            <button
              onClick={onDownload}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download
            </button>
          )}

          {onDelete && (
            <button
              onClick={onDelete}
              disabled={onDeleteLoading}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {onDeleteLoading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Deleting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  Delete
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
