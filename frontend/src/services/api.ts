import type {
  Dataset,
  DatasetDetail,
  DatasetListResponse,
  ColumnProfile,
  QualityScoreDetail,
  DashboardConfig,
  DataPreview,
  SearchResult,
  GlobalStats,
  Tag,
} from "../types/dataset";

const API_BASE = "/api/v1";

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || response.statusText);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// ----- Datasets -----

export interface ListDatasetsParams {
  skip?: number;
  limit?: number;
  status?: string;
  format?: string;
  search_name?: string;
  sort_by?: string;
  sort_desc?: boolean;
}

export async function listDatasets(
  params: ListDatasetsParams = {}
): Promise<DatasetListResponse> {
  const searchParams = new URLSearchParams();
  if (params.skip !== undefined) searchParams.set("skip", String(params.skip));
  if (params.limit !== undefined) searchParams.set("limit", String(params.limit));
  if (params.status) searchParams.set("status", params.status);
  if (params.format) searchParams.set("format", params.format);
  if (params.search_name) searchParams.set("search_name", params.search_name);
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.sort_desc !== undefined) searchParams.set("sort_desc", String(params.sort_desc));

  const query = searchParams.toString();
  return request<DatasetListResponse>(`/datasets${query ? `?${query}` : ""}`);
}

export async function getDataset(id: number): Promise<DatasetDetail> {
  return request<DatasetDetail>(`/datasets/${id}`);
}

export async function deleteDataset(id: number): Promise<void> {
  return request<void>(`/datasets/${id}`, { method: "DELETE" });
}

export async function reprocessDataset(id: number): Promise<Dataset> {
  return request<Dataset>(`/datasets/${id}/reprocess`, { method: "POST" });
}

// ----- Upload -----

export interface UploadProgress {
  stage: string;
  progress: number;
}

export async function uploadDataset(
  file: File,
  options: { name?: string; description?: string; source?: string } = {},
  onProgress?: (progress: UploadProgress) => void
): Promise<Dataset> {
  const formData = new FormData();
  formData.append("file", file);
  if (options.name) formData.append("name", options.name);
  if (options.description) formData.append("description", options.description);
  if (options.source) formData.append("source", options.source);

  const url = `${API_BASE}/datasets/upload`;

  // Simulate progress stages
  const stages = [
    { stage: "Uploading", progress: 10 },
    { stage: "Validating", progress: 25 },
    { stage: "Profiling", progress: 40 },
    { stage: "Detecting PII", progress: 55 },
    { stage: "Quality scoring", progress: 70 },
    { stage: "Indexing", progress: 85 },
    { stage: "Dashboard", progress: 95 },
  ];

  let stageIndex = 0;
  const progressInterval = setInterval(() => {
    if (onProgress && stageIndex < stages.length) {
      onProgress(stages[stageIndex]);
      stageIndex++;
    }
  }, 500);

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    clearInterval(progressInterval);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Upload failed" }));
      throw new ApiError(response.status, error.detail || response.statusText);
    }

    onProgress?.({ stage: "Complete", progress: 100 });
    return response.json();
  } catch (err) {
    clearInterval(progressInterval);
    throw err;
  }
}

// ----- Profile -----

export async function getDatasetProfile(id: number): Promise<ColumnProfile[]> {
  return request<ColumnProfile[]>(`/datasets/${id}/profile`);
}

// ----- Quality -----

export async function getDatasetQuality(id: number): Promise<QualityScoreDetail | null> {
  return request<QualityScoreDetail | null>(`/datasets/${id}/quality`);
}

// ----- Dashboard -----

export async function getDatasetDashboard(id: number): Promise<DashboardConfig | null> {
  return request<DashboardConfig | null>(`/datasets/${id}/dashboard`);
}

// ----- Preview -----

export async function getDatasetPreview(
  id: number,
  rows: number = 100,
  offset: number = 0
): Promise<DataPreview> {
  return request<DataPreview>(`/datasets/${id}/preview?rows=${rows}&offset=${offset}`);
}

// ----- Tags -----

export async function getDatasetTags(id: number): Promise<Tag[]> {
  return request<Tag[]>(`/datasets/${id}/tags`);
}

// ----- Search -----

export async function searchDatasets(
  query: string,
  limit: number = 10
): Promise<SearchResult[]> {
  return request<SearchResult[]>(`/datasets/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

// ----- Stats -----

export async function getGlobalStats(): Promise<GlobalStats> {
  // Use dedicated stats endpoint
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) {
    // Fallback to computing from datasets list
    const datasets = await listDatasets({ limit: 100 });
    const total_rows = datasets.items.reduce((sum, d) => sum + (d.row_count || 0), 0);
    const validQuality = datasets.items.filter((d) => d.quality_score !== null);
    const avg_quality = validQuality.length > 0
      ? validQuality.reduce((sum, d) => sum + (d.quality_score || 0), 0) / validQuality.length
      : 0;
    return {
      total_datasets: datasets.total,
      total_rows,
      avg_quality: Math.round(avg_quality * 10) / 10,
      domain_count: 0,
    };
  }
  return response.json();
}

export { ApiError };
