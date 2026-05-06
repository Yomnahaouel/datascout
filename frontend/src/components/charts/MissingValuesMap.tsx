import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface MissingValuesMapProps {
  data: { column: string; missing_pct: number; missing_count: number }[];
  title?: string;
  height?: number;
}

export default function MissingValuesMap({
  data,
  title = "Missing Values by Column",
  height = 300,
}: MissingValuesMapProps) {
  const sortedData = [...data].sort((a, b) => b.missing_pct - a.missing_pct);

  const getColor = (pct: number) => {
    if (pct >= 50) return "#EF4444"; // Red
    if (pct >= 20) return "#F59E0B"; // Yellow
    if (pct >= 5) return "#3B82F6"; // Blue
    return "#10B981"; // Green
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      {title && <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 80, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            tickFormatter={(v) => `${v}%`}
          />
          <YAxis
            type="category"
            dataKey="column"
            tick={{ fontSize: 11 }}
            width={70}
            tickFormatter={(v) => (v.length > 10 ? v.slice(0, 10) + "…" : v)}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #E5E7EB",
              borderRadius: "8px",
              fontSize: 12,
            }}
            formatter={(value, _name, props: { payload?: { missing_count?: number } }) => [
              `${Number(value).toFixed(1)}% (${props?.payload?.missing_count?.toLocaleString() ?? 0} values)`,
              "Missing",
            ]}
          />
          <Bar dataKey="missing_pct" radius={[0, 4, 4, 0]}>
            {sortedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.missing_pct)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {/* Legend */}
      <div className="flex justify-center gap-4 mt-4 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-green-500" />
          {"<5%"}
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-blue-500" />
          5-20%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-yellow-500" />
          20-50%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-red-500" />
          {">50%"}
        </span>
      </div>
    </div>
  );
}
