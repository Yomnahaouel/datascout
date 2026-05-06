import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  
} from "recharts";

interface BoxPlotData {
  name: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  outliers?: number[];
}

interface BoxPlotChartProps {
  data: BoxPlotData[];
  title?: string;
}

export default function BoxPlotChart({ data, title }: BoxPlotChartProps) {
  // Transform data for visualization
  // Using a composed chart with bars to simulate box plots
  const chartData = data.map((d) => ({
    name: d.name,
    range: [d.q1, d.q3],
    median: d.median,
    whiskerLow: d.min,
    whiskerHigh: d.max,
    iqr: d.q3 - d.q1,
    q1: d.q1,
    q3: d.q3,
    min: d.min,
    max: d.max,
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      {title && (
        <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={250}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 20, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: "#E5E7EB" }}
          />
          <YAxis
            tick={{ fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: "#E5E7EB" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #E5E7EB",
              borderRadius: "8px",
              fontSize: "12px",
            }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0].payload;
              return (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                  <p className="font-semibold text-gray-900 mb-2">{d.name}</p>
                  <div className="text-xs space-y-1 text-gray-600">
                    <p>Max: {d.max?.toFixed(2)}</p>
                    <p>Q3: {d.q3?.toFixed(2)}</p>
                    <p className="font-medium text-gray-900">
                      Median: {d.median?.toFixed(2)}
                    </p>
                    <p>Q1: {d.q1?.toFixed(2)}</p>
                    <p>Min: {d.min?.toFixed(2)}</p>
                  </div>
                </div>
              );
            }}
          />
          {/* Box (IQR) */}
          <Bar
            dataKey="iqr"
            fill="#3B82F6"
            fillOpacity={0.3}
            stroke="#3B82F6"
            strokeWidth={2}
            radius={[4, 4, 4, 4]}
            maxBarSize={50}
          />
          {/* Median line */}
          <Line
            type="monotone"
            dataKey="median"
            stroke="#EF4444"
            strokeWidth={3}
            dot={{ fill: "#EF4444", r: 5 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="flex items-center justify-center gap-4 mt-2 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-blue-500 bg-opacity-30 border border-blue-500 rounded" />
          IQR (Q1-Q3)
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-red-500 rounded-full" />
          Median
        </span>
      </div>
    </div>
  );
}
