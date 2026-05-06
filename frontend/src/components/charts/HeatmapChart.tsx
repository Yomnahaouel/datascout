interface HeatmapChartProps {
  data: { x: string; y: string; value: number }[];
  xLabels: string[];
  yLabels: string[];
  title?: string;
  height?: number;
}

export default function HeatmapChart({
  data,
  xLabels,
  yLabels,
  title,
  height = 300,
}: HeatmapChartProps) {
  // Create a matrix from the data
  const matrix: Record<string, Record<string, number>> = {};
  data.forEach((d) => {
    if (!matrix[d.y]) matrix[d.y] = {};
    matrix[d.y][d.x] = d.value;
  });

  const getColor = (value: number) => {
    // Value should be between -1 and 1 for correlation
    if (value >= 0.7) return "bg-blue-600";
    if (value >= 0.4) return "bg-blue-400";
    if (value >= 0.1) return "bg-blue-200";
    if (value >= -0.1) return "bg-gray-100";
    if (value >= -0.4) return "bg-red-200";
    if (value >= -0.7) return "bg-red-400";
    return "bg-red-600";
  };

  const getTextColor = (value: number) => {
    if (Math.abs(value) >= 0.7) return "text-white";
    return "text-gray-700";
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      {title && <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>}
      <div className="overflow-x-auto" style={{ minHeight: height }}>
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="p-2"></th>
              {xLabels.map((label) => (
                <th
                  key={label}
                  className="p-2 text-gray-600 font-medium text-center truncate max-w-[80px]"
                  title={label}
                >
                  {label.length > 8 ? label.slice(0, 8) + "…" : label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {yLabels.map((yLabel) => (
              <tr key={yLabel}>
                <td
                  className="p-2 text-gray-600 font-medium text-right truncate max-w-[80px]"
                  title={yLabel}
                >
                  {yLabel.length > 8 ? yLabel.slice(0, 8) + "…" : yLabel}
                </td>
                {xLabels.map((xLabel) => {
                  const value = matrix[yLabel]?.[xLabel] ?? 0;
                  return (
                    <td key={xLabel} className="p-1">
                      <div
                        className={`w-10 h-10 flex items-center justify-center rounded ${getColor(value)} ${getTextColor(value)} font-medium`}
                        title={`${yLabel} × ${xLabel}: ${value.toFixed(2)}`}
                      >
                        {value.toFixed(1)}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Legend */}
      <div className="flex justify-center items-center gap-2 mt-4 text-xs text-gray-500">
        <span>-1</span>
        <div className="flex h-2">
          <div className="w-6 bg-red-600 rounded-l" />
          <div className="w-6 bg-red-400" />
          <div className="w-6 bg-red-200" />
          <div className="w-6 bg-gray-100" />
          <div className="w-6 bg-blue-200" />
          <div className="w-6 bg-blue-400" />
          <div className="w-6 bg-blue-600 rounded-r" />
        </div>
        <span>+1</span>
      </div>
    </div>
  );
}
