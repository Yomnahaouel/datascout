import type { TagCategory } from "../../types/dataset";

interface TagBadgeProps {
  value: string;
  category?: TagCategory;
  confidence?: number;
  onRemove?: () => void;
}

export default function TagBadge({
  value,
  category = "domain",
  confidence,
  onRemove,
}: TagBadgeProps) {
  const categoryStyles: Record<TagCategory, { bg: string; text: string; border: string }> = {
    domain: {
      bg: "bg-blue-50",
      text: "text-blue-700",
      border: "border-blue-200",
    },
    data_type: {
      bg: "bg-purple-50",
      text: "text-purple-700",
      border: "border-purple-200",
    },
    pii_type: {
      bg: "bg-red-50",
      text: "text-red-700",
      border: "border-red-200",
    },
    custom: {
      bg: "bg-gray-50",
      text: "text-gray-700",
      border: "border-gray-200",
    },
  };

  const style = categoryStyles[category];

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${style.bg} ${style.text} ${style.border}`}
    >
      {category === "pii_type" && (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
      )}
      <span>{value}</span>
      {confidence !== undefined && confidence < 1 && (
        <span className="opacity-60">({Math.round(confidence * 100)}%)</span>
      )}
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-1 hover:opacity-70 transition-opacity"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </span>
  );
}
