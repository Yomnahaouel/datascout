import { useState } from "react";
import type { DataPreview } from "../../types/dataset";

interface DataPreviewTableProps {
  preview: DataPreview;
  onLoadMore?: () => void;
  loading?: boolean;
}

export default function DataPreviewTable({
  preview,
  onLoadMore,
  loading = false,
}: DataPreviewTableProps) {
  const [selectedColumn, setSelectedColumn] = useState<number | null>(null);

  const formatCell = (value: string | number | boolean | null) => {
    if (value === null || value === "") return <span className="text-gray-400">null</span>;
    if (typeof value === "boolean") return value ? "true" : "false";
    return String(value);
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Data Preview</h2>
          <p className="text-sm text-gray-500">
            Showing {preview.preview_rows.toLocaleString()} of{" "}
            {preview.total_rows.toLocaleString()} rows
          </p>
        </div>
        {onLoadMore && preview.preview_rows < preview.total_rows && (
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? "Loading..." : "Load More"}
          </button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 sticky top-0">
            <tr>
              <th className="px-3 py-2 text-center text-gray-400 font-normal w-12">
                #
              </th>
              {preview.columns.map((col, i) => (
                <th
                  key={i}
                  className={`px-3 py-2 text-left font-medium cursor-pointer hover:bg-gray-100 transition-colors whitespace-nowrap ${
                    selectedColumn === i ? "bg-blue-50 text-blue-700" : ""
                  }`}
                  onClick={() => setSelectedColumn(selectedColumn === i ? null : i)}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {preview.data.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                <td className="px-3 py-2 text-center text-gray-400 text-xs">
                  {rowIndex + 1}
                </td>
                {row.map((cell, colIndex) => (
                  <td
                    key={colIndex}
                    className={`px-3 py-2 whitespace-nowrap ${
                      selectedColumn === colIndex ? "bg-blue-50" : ""
                    }`}
                  >
                    <span className="max-w-[200px] truncate block" title={String(cell)}>
                      {formatCell(cell)}
                    </span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {preview.data.length === 0 && (
        <div className="p-8 text-center text-gray-500">No data available.</div>
      )}
    </div>
  );
}
