import type { Dataset } from "../../types/dataset";
import QualityBadge from "../common/QualityBadge";

interface SuccessSummaryProps {
  dataset: Dataset;
  onViewDataset: () => void;
}

export default function SuccessSummary({ dataset, onViewDataset }: SuccessSummaryProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="text-center py-4">
      {/* Success icon */}
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg
          className="w-8 h-8 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>

      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Dataset Uploaded Successfully!
      </h3>
      <p className="text-gray-600 mb-6">
        Your dataset has been processed and is ready to explore.
      </p>

      {/* Stats */}
      <div className="bg-gray-50 rounded-xl p-4 mb-6">
        <h4 className="font-medium text-gray-900 mb-4">{dataset.name}</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="text-left">
            <span className="text-gray-500">Rows</span>
            <p className="font-semibold text-gray-900">
              {dataset.row_count?.toLocaleString() ?? "Processing..."}
            </p>
          </div>
          <div className="text-left">
            <span className="text-gray-500">Columns</span>
            <p className="font-semibold text-gray-900">
              {dataset.column_count ?? "Processing..."}
            </p>
          </div>
          <div className="text-left">
            <span className="text-gray-500">Size</span>
            <p className="font-semibold text-gray-900">
              {formatFileSize(dataset.file_size)}
            </p>
          </div>
          <div className="text-left">
            <span className="text-gray-500">Quality</span>
            <div className="mt-1">
              {dataset.quality_score !== null ? (
                <QualityBadge score={dataset.quality_score} size="sm" />
              ) : (
                <span className="text-gray-400">Processing...</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Status */}
      {dataset.status === "processing" && (
        <div className="flex items-center justify-center gap-2 text-blue-600 mb-4">
          <svg
            className="w-4 h-4 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
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
          <span className="text-sm">Processing in background...</span>
        </div>
      )}

      {/* Quick actions */}
      <div className="flex flex-col gap-2">
        <button
          onClick={onViewDataset}
          className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          View Dataset Profile
        </button>
        <button
          onClick={() => window.location.href = `/datasets/${dataset.id}/dashboard`}
          className="w-full py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
        >
          View Dashboard
        </button>
      </div>
    </div>
  );
}
