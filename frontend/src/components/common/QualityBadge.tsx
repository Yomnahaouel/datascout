interface QualityBadgeProps {
  score: number | null;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export default function QualityBadge({
  score,
  size = "md",
  showLabel = true,
}: QualityBadgeProps) {
  if (score === null) {
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
        N/A
      </span>
    );
  }

  const getColor = (s: number) => {
    if (s >= 80) return { bg: "bg-green-100", text: "text-green-700", ring: "ring-green-500" };
    if (s >= 60) return { bg: "bg-yellow-100", text: "text-yellow-700", ring: "ring-yellow-500" };
    return { bg: "bg-red-100", text: "text-red-700", ring: "ring-red-500" };
  };

  const getGrade = (s: number) => {
    if (s >= 90) return "A";
    if (s >= 80) return "B";
    if (s >= 70) return "C";
    if (s >= 60) return "D";
    return "F";
  };

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-sm",
    lg: "px-3 py-1.5 text-base",
  };

  const colors = getColor(score);

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium ${colors.bg} ${colors.text} ${sizeClasses[size]}`}
    >
      <span className="font-bold">{Math.round(score)}</span>
      {showLabel && <span className="opacity-75">({getGrade(score)})</span>}
    </span>
  );
}
