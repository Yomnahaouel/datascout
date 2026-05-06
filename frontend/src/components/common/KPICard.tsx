interface KPICardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    label: string;
  };
  color?: "blue" | "green" | "yellow" | "red" | "purple";
}

export default function KPICard({
  label,
  value,
  icon,
  trend,
  color = "blue",
}: KPICardProps) {
  const colorClasses = {
    blue: "bg-blue-500/10 text-blue-600 dark:text-blue-300",
    green: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-300",
    yellow: "bg-amber-500/10 text-amber-600 dark:text-amber-300",
    red: "bg-red-500/10 text-red-600 dark:text-red-300",
    purple: "bg-violet-500/10 text-violet-600 dark:text-violet-300",
  };

  const trendColors = {
    positive: "text-emerald-600 dark:text-emerald-300",
    negative: "text-red-600 dark:text-red-300",
    neutral: "text-slate-500 dark:text-slate-400",
  };

  const getTrendType = (val: number) => {
    if (val > 0) return "positive";
    if (val < 0) return "negative";
    return "neutral";
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-950/5 transition-all hover:-translate-y-0.5 hover:shadow-xl dark:border-white/10 dark:bg-white/[0.055] sm:p-6">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="mb-1 truncate text-sm font-semibold text-slate-500 dark:text-slate-400">{label}</p>
          <p className="truncate text-2xl font-black tracking-tight text-slate-950 dark:text-white sm:text-3xl">
            {typeof value === "number" ? value.toLocaleString() : value}
          </p>
          {trend && (
            <p className={`mt-2 text-sm ${trendColors[getTrendType(trend.value)]}`}>
              {trend.value > 0 ? "↑" : trend.value < 0 ? "↓" : "→"}{" "}
              {Math.abs(trend.value)}% {trend.label}
            </p>
          )}
        </div>
        {icon && <div className={`rounded-2xl p-3 ${colorClasses[color]}`}>{icon}</div>}
      </div>
    </div>
  );
}
