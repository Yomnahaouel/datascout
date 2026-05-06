import type { QualityScoreDetail } from "../../types/dataset";

interface QualityBreakdownProps {
  quality: QualityScoreDetail;
}

export default function QualityBreakdown({ quality }: QualityBreakdownProps) {
  const dimensions = [
    {
      name: "Completeness",
      value: quality.completeness,
      description: "Percentage of non-null values",
      color: "bg-blue-500",
    },
    {
      name: "Consistency",
      value: quality.consistency,
      description: "Data format uniformity",
      color: "bg-green-500",
    },
    {
      name: "Uniqueness",
      value: quality.uniqueness,
      description: "Duplicate detection score",
      color: "bg-purple-500",
    },
    {
      name: "Validity",
      value: quality.validity,
      description: "Values within expected ranges",
      color: "bg-yellow-500",
    },
    {
      name: "Timeliness",
      value: quality.timeliness,
      description: "Date freshness score",
      color: "bg-red-500",
    },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Quality Breakdown</h2>
        <div className="flex items-center gap-2">
          <span className={`text-3xl font-bold ${getScoreColor(quality.overall_score)}`}>
            {Math.round(quality.overall_score)}
          </span>
          <span className="text-gray-400">/100</span>
          <span
            className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
              quality.grade === "A"
                ? "bg-green-100 text-green-700"
                : quality.grade === "B"
                  ? "bg-blue-100 text-blue-700"
                  : quality.grade === "C"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-red-100 text-red-700"
            }`}
          >
            Grade {quality.grade}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {dimensions.map((dim) => (
          <div key={dim.name}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">{dim.name}</span>
                <span className="text-xs text-gray-400">{dim.description}</span>
              </div>
              <span className={`text-sm font-semibold ${getScoreColor(dim.value)}`}>
                {Math.round(dim.value)}%
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full ${dim.color} rounded-full transition-all duration-500`}
                style={{ width: `${dim.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Recommendations */}
      {quality.recommendations && quality.recommendations.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Recommendations</h3>
          <ul className="space-y-2">
            {quality.recommendations.map((rec, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-gray-600"
              >
                <svg
                  className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clipRule="evenodd"
                  />
                </svg>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
