interface PIIFilterProps {
  value: "all" | "has_pii" | "no_pii";
  onChange: (value: "all" | "has_pii" | "no_pii") => void;
}

const OPTIONS = [
  { value: "all", label: "All datasets" },
  { value: "has_pii", label: "Contains PII" },
  { value: "no_pii", label: "No PII" },
] as const;

export default function PIIFilter({ value, onChange }: PIIFilterProps) {
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-3">PII Detection</h3>
      <div className="space-y-2">
        {OPTIONS.map((option) => (
          <label
            key={option.value}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="radio"
              name="pii-filter"
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600 group-hover:text-gray-900">
              {option.label}
            </span>
            {option.value === "has_pii" && (
              <svg
                className="w-4 h-4 text-red-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </label>
        ))}
      </div>
    </div>
  );
}
