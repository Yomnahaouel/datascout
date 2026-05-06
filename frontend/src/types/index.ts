// ----- DataSource -----
export interface DataSource {
  id: number;
  name: string;
  source_type: string;
  connection_string: string | null;
  created_at: string | null;
}

export interface DataSourceCreate {
  name: string;
  source_type: string;
  connection_string?: string;
}

// ----- Job -----
export interface Job {
  id: number;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  source_id: number;
  created_at: string | null;
  finished_at: string | null;
}

export interface JobCreate {
  name: string;
  source_id: number;
}

// ----- Result -----
export interface Result {
  id: number;
  job_id: number;
  data: Record<string, unknown> | null;
  summary: string | null;
  created_at: string | null;
}

// ----- Dashboard Stats -----
export interface DashboardStats {
  totalSources: number;
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  totalResults: number;
  jobsByStatus: { name: string; value: number }[];
  jobTimeline: { date: string; count: number }[];
  sourceTypes: { name: string; value: number }[];
}
