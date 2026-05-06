interface ProgressStepsProps {
  currentStage: string;
  progress: number;
}

const STAGES = [
  { key: "Uploading", label: "Uploading", icon: "☁️" },
  { key: "Validating", label: "Validating", icon: "✓" },
  { key: "Profiling", label: "Profiling", icon: "📊" },
  { key: "Detecting PII", label: "Detecting PII", icon: "🔒" },
  { key: "Quality scoring", label: "Quality Scoring", icon: "⭐" },
  { key: "Indexing", label: "Indexing", icon: "🔍" },
  { key: "Dashboard", label: "Dashboard", icon: "📈" },
  { key: "Complete", label: "Complete", icon: "✅" },
];

export default function ProgressSteps({ currentStage, progress }: ProgressStepsProps) {
  const currentIndex = STAGES.findIndex((s) => s.key === currentStage);

  return (
    <div className="py-4">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{currentStage || "Starting..."}</span>
          <span>{progress}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {STAGES.map((stage, index) => {
          const isComplete = index < currentIndex;
          const isCurrent = index === currentIndex;
          // isPending would be: index > currentIndex

          return (
            <div
              key={stage.key}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                isCurrent
                  ? "bg-blue-50 border border-blue-200"
                  : isComplete
                    ? "bg-green-50"
                    : "bg-gray-50"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                  isComplete
                    ? "bg-green-500 text-white"
                    : isCurrent
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-gray-500"
                }`}
              >
                {isComplete ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : isCurrent ? (
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
                ) : (
                  <span>{stage.icon}</span>
                )}
              </div>
              <span
                className={`text-sm font-medium ${
                  isComplete
                    ? "text-green-700"
                    : isCurrent
                      ? "text-blue-700"
                      : "text-gray-500"
                }`}
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
