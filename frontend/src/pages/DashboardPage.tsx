import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getDataset, getDatasetDashboard } from "../services/api";
import type { DatasetDetail, DashboardConfig, ChartConfig } from "../types/dataset";
import HistogramChart from "../components/charts/HistogramChart";
import PieChartComponent from "../components/charts/PieChartComponent";
import BoxPlotChart from "../components/charts/BoxPlotChart";
import HeatmapChart from "../components/charts/HeatmapChart";
import MissingValuesMap from "../components/charts/MissingValuesMap";
import LoadingSpinner from "../components/common/LoadingSpinner";
import {
  BarChart,
  Bar,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type NameValueDatum = { name: string; value: number; count?: number };
type TimeSeriesDatum = { date?: string; name?: string; count?: number; value?: number };

function normalizeNameValueData(data: unknown[]): NameValueDatum[] {
  return data
    .map((item) => {
      if (!item || typeof item !== "object") return null;
      const row = item as Record<string, unknown>;
      const name = String(row.name ?? row.label ?? row.date ?? row.column ?? "Unknown");
      const rawValue = row.value ?? row.count ?? 0;
      const value = typeof rawValue === "number" ? rawValue : Number(rawValue) || 0;
      return { name, value };
    })
    .filter((item): item is NameValueDatum => item !== null);
}

function renderKpiCards(chart: ChartConfig) {
  const rawData = chart.data ?? chart.config?.data;
  const cards = Array.isArray(rawData)
    ? rawData.map((item) => {
        const row = (item ?? {}) as Record<string, unknown>;
        return { label: String(row.label ?? row.name ?? "Metric"), value: row.value ?? "N/A" };
      })
    : Object.entries((rawData ?? {}) as Record<string, unknown>).map(([key, value]) => ({
        label: key.replace(/_/g, " "),
        value,
      }));

  return (
    <div className="h-full">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">{chart.title}</h3>
      <div className="grid grid-cols-2 gap-3">
        {cards.map((card) => (
          <div key={card.label} className="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3">
            <p className="text-xs font-medium uppercase tracking-wide text-blue-500">{card.label}</p>
            <p className="mt-1 text-2xl font-bold text-blue-900">{String(card.value)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function renderBarChart(data: NameValueDatum[], title: string) {
  return (
    <div className="h-full">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={60} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip />
          <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} maxBarSize={70} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function renderTimeSeries(data: TimeSeriesDatum[], title: string) {
  const chartData = data.map((item) => ({
    name: item.date ?? item.name ?? "Unknown",
    value: item.count ?? item.value ?? 0,
  }));

  return (
    <div className="h-full">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={60} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#2563EB" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Chart component renderer based on chart type
function renderChart(chart: ChartConfig) {
  const rawChartData = chart.data ?? chart.config?.data ?? [];
  const chartData = Array.isArray(rawChartData) ? rawChartData : [];

  switch (chart.chart_type) {
    case "kpi_cards":
      return renderKpiCards(chart);
    case "histogram":
      return (
        <HistogramChart
          data={chartData as { bin_start: number; bin_end: number; count: number }[]}
          title={chart.title}
        />
      );
    case "bar":
      return renderBarChart(normalizeNameValueData(chartData), chart.title);
    case "pie":
      return (
        <PieChartComponent
          data={normalizeNameValueData(chartData) as { name: string; value: number; color?: string }[]}
          title={chart.title}
        />
      );
    case "class_balance":
      return (
        <PieChartComponent
          data={normalizeNameValueData(chartData) as { name: string; value: number; color?: string }[]}
          title={chart.title}
        />
      );
    case "time_series":
    case "line":
      return renderTimeSeries(chartData as TimeSeriesDatum[], chart.title);
    case "box":
    case "boxplot":
      return (
        <BoxPlotChart
          data={chartData as { name: string; min: number; q1: number; median: number; q3: number; max: number }[]}
          title={chart.title}
        />
      );
    case "heatmap": {
      const heatData = chartData as { x: string; y: string; value: number }[];
      const xLabels = [...new Set(heatData.map((d) => d.x))];
      const yLabels = [...new Set(heatData.map((d) => d.y))];
      return (
        <HeatmapChart
          data={heatData}
          xLabels={xLabels}
          yLabels={yLabels}
          title={chart.title}
        />
      );
    }
    case "missing":
      return (
        <MissingValuesMap
          data={chartData as { column: string; missing_pct: number; missing_count: number }[]}
          title={chart.title}
        />
      );
    default:
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          Unsupported chart type: {chart.chart_type}
        </div>
      );
  }
}

export default function DashboardPage() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<DatasetDetail | null>(null);
  const [dashboard, setDashboard] = useState<DashboardConfig | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const numId = Number(id);
    queueMicrotask(() => setLoading(true));
    Promise.all([getDataset(numId), getDatasetDashboard(numId)])
      .then(([datasetData, dashboardData]) => {
        setDataset(datasetData);
        setDashboard(dashboardData);
      })
      .catch((err) => {
        console.error("Failed to load dashboard:", err);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!dataset || !dashboard) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Dashboard not available</h2>
        <p className="text-gray-500 mb-4">
          Unable to generate dashboard for this dataset.
        </p>
        <Link to={`/datasets/${id}`} className="text-blue-600 hover:underline">
          ← Back to dataset
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <nav className="flex items-center gap-2 text-sm">
            <Link to="/browse" className="text-gray-500 hover:text-gray-700">
              Datasets
            </Link>
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <Link to={`/datasets/${id}`} className="text-gray-500 hover:text-gray-700">
              {dataset.name}
            </Link>
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-gray-900 font-medium">Dashboard</span>
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {dataset.name} Dashboard
            </h1>
            <p className="text-gray-500 mt-1">
              Auto-generated visualizations based on column types
            </p>
          </div>
          <Link
            to={`/datasets/${id}`}
            className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Profile
          </Link>
        </div>

        {/* Dashboard info */}
        {dashboard.generated_at && (
          <div className="mb-6 px-4 py-3 bg-blue-50 border border-blue-100 rounded-lg">
            <p className="text-sm text-blue-700">
              <span className="font-medium">Dashboard generated:</span>{" "}
              {new Date(dashboard.generated_at).toLocaleString()}
            </p>
          </div>
        )}

        {/* Charts Grid */}
        {dashboard.charts.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <svg
              className="w-16 h-16 text-gray-300 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-1">
              No charts available
            </h3>
            <p className="text-gray-500">
              Unable to generate visualizations for this dataset's columns
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {dashboard.charts.map((chart, index) => (
              <div
                key={index}
                className="bg-white rounded-xl border border-gray-200 p-6 min-h-[350px]"
              >
                {renderChart(chart)}
              </div>
            ))}
          </div>
        )}

        {/* Summary Statistics */}
        {dashboard.summary && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Summary Statistics
            </h2>
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Metric
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Value
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {Object.entries(dashboard.summary).map(([key, value]) => (
                    <tr key={key} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-600 capitalize">
                        {key.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {typeof value === "number"
                          ? value.toLocaleString()
                          : String(value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
