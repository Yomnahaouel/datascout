// ----- Enums -----
export type DatasetStatus = "pending" | "processing" | "completed" | "failed";
export type FileFormat = "csv" | "tsv" | "json" | "parquet" | "excel";
export type TagCategory = "domain" | "data_type" | "pii_type" | "custom";

// ----- Dataset -----
export interface Dataset {
  id: number;
  name: string;
  description: string | null;
  source: string | null;
  file_path: string;
  file_format: FileFormat;
  file_size: number;
  row_count: number | null;
  column_count: number | null;
  quality_score: number | null;
  status: DatasetStatus;
  error_message: string | null;
  created_at: string;
  processed_at: string | null;
  tags?: Tag[];
}

export interface DatasetCreate {
  name?: string;
  description?: string;
  source?: string;
}

export interface DatasetDetail extends Dataset {
  column_profiles: ColumnProfile[];
  tags: Tag[];
  quality_score_detail: QualityScoreDetail | null;
  quality_details?: QualityScoreDetail | null; // Alias for quality_score_detail
  dashboard_config: DashboardConfig | null;
}

// ----- Column Profile -----
export interface ColumnProfile {
  id: number;
  dataset_id: number;
  column_name: string;
  column_index: number;
  raw_dtype: string;
  inferred_type: string;
  missing_count: number;
  missing_pct: number;
  unique_count: number;
  mean: number | null;
  median: number | null;
  std_dev: number | null;
  min_value: number | null;
  max_value: number | null;
  distribution: DistributionBin[] | null;
  outlier_count: number;
  sample_values: (string | number | boolean | null)[];
  is_pii: boolean;
  pii_detected?: boolean; // Alias for is_pii
  pii_type: string | null;
}

export interface DistributionBin {
  bin_start: number;
  bin_end: number;
  count: number;
}

// ----- Tag -----
export interface Tag {
  id: number;
  category: TagCategory;
  value: string;
  confidence: number;
  method: string;
  created_at: string;
}

// ----- Quality Score -----
export interface QualityScoreDetail {
  id: number;
  dataset_id: number;
  completeness: number;
  consistency: number;
  uniqueness: number;
  validity: number;
  timeliness: number;
  overall_score: number;
  grade: string;
  details: Record<string, unknown>;
  recommendations: string[];
  created_at: string;
}

// ----- Dashboard Config -----
export interface DashboardConfig {
  id?: number;
  dataset_id?: number;
  charts: ChartConfig[];
  kpis?: KPIConfig[];
  filters?: FilterConfig[];
  layout?: LayoutConfig;
  created_at?: string;
  generated_at?: string;
  summary?: Record<string, string | number | boolean>;
}

export interface ChartConfig {
  chart_type: "histogram" | "pie" | "bar" | "box" | "boxplot" | "scatter" | "heatmap" | "line" | "missing";
  title: string;
  x_axis?: string | null;
  y_axis?: string | null;
  column?: string;
  color_by?: string | null;
  size_by?: string | null;
  aggregation?: string | null;
  confidence?: number;
  reason?: string;
  config?: Record<string, unknown>;
  // Frontend rendering data
  data?: unknown[];
}

export interface KPIConfig {
  label: string;
  value: string | number;
  format: string;
  icon: string | null;
}

export interface FilterConfig {
  column: string;
  filter_type: string;
  options: string[] | null;
}

export interface LayoutConfig {
  columns: number;
  rows: number;
  chart_height: number;
}

// ----- Search -----
export interface SearchResult {
  dataset_id: number;
  name: string;
  description: string | null;
  relevance_score: number;
  matched_columns: string[];
  snippet: string | null;
}

// ----- Data Preview -----
export interface DataPreview {
  columns: string[];
  data: (string | number | boolean | null)[][];
  rows?: (string | number | boolean | null)[][]; // Alias for data
  total_rows: number;
  preview_rows: number;
}

// ----- List Response -----
export interface DatasetListResponse {
  items: Dataset[];
  total: number;
  skip?: number;
  limit?: number;
  page?: number;
  page_size?: number;
  pages?: number;
}

// ----- Stats -----
export interface GlobalStats {
  total_datasets: number;
  total_rows: number;
  avg_quality: number;
  domain_count: number;
}
