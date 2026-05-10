"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


# ─────────────────────────────────────────────────────────────────────────────
# Enums (mirroring SQLAlchemy models)
# ─────────────────────────────────────────────────────────────────────────────

class DatasetStatus(str):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileFormat(str):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "excel"
    TSV = "tsv"


# ─────────────────────────────────────────────────────────────────────────────
# Column Profile Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ColumnProfileBase(BaseModel):
    column_name: str
    column_index: int
    raw_dtype: str
    inferred_type: str | None = None
    missing_count: int = 0
    missing_pct: float = 0.0
    unique_count: int | None = None
    mean: float | None = None
    median: float | None = None
    std_dev: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    distribution: dict[str, Any] | None = None
    outlier_count: int = 0
    sample_values: list[Any] | None = None
    is_pii: bool = False
    pii_type: str | None = None


class ColumnProfileResponse(ColumnProfileBase):
    id: int
    dataset_id: int

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tag Schemas
# ─────────────────────────────────────────────────────────────────────────────

class TagBase(BaseModel):
    tag_category: str
    tag_value: str
    confidence: float = 1.0
    method: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    dataset_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Quality Score Schemas
# ─────────────────────────────────────────────────────────────────────────────

class QualityScoreBase(BaseModel):
    completeness: float = Field(..., ge=0.0, le=1.0)
    consistency: float = Field(..., ge=0.0, le=1.0)
    uniqueness: float = Field(..., ge=0.0, le=1.0)
    validity: float = Field(..., ge=0.0, le=1.0)
    timeliness: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    grade: str


class QualityScoreResponse(QualityScoreBase):
    id: int
    dataset_id: int
    details: dict[str, Any] | None = None
    recommendations: list[str] | None = None
    scored_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Config Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ChartConfig(BaseModel):
    chart_type: str
    title: str
    x_axis: str | None = None
    y_axis: str | None = None
    color_by: str | None = None
    size_by: str | None = None
    aggregation: str | None = None
    confidence: float = 0.0
    reason: str = ""
    config: dict[str, Any] = Field(default_factory=dict)


class KPIConfig(BaseModel):
    name: str
    value: float | int | str
    format: str = "number"
    icon: str | None = None


class DashboardConfigBase(BaseModel):
    charts: list[ChartConfig]
    kpis: list[KPIConfig] | None = None
    filters: list[str] | None = None
    layout: dict[str, Any] | None = None


class DashboardConfigResponse(DashboardConfigBase):
    id: int
    dataset_id: int
    generated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Dataset Schemas
# ─────────────────────────────────────────────────────────────────────────────

class DatasetBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None


class DatasetSummary(DatasetBase):
    """Lightweight dataset response for list views."""
    id: int
    file_format: str
    file_size_bytes: int
    row_count: int | None = None
    column_count: int | None = None
    uploaded_at: datetime | None = None
    quality_score: float | None = None
    status: str
    domain: str | None = None
    domains: list[str] = []
    tags: list[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DatasetResponse(DatasetSummary):
    """Full dataset response with relationships."""
    file_path: str
    processed_at: datetime | None = None
    error_message: str | None = None
    tags: list[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DatasetDetail(DatasetResponse):
    """Detailed dataset response with all nested data."""
    column_profiles: list[ColumnProfileResponse] = []
    quality_scores: list[QualityScoreResponse] = []
    dashboard_configs: list[DashboardConfigResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Upload Response
# ─────────────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    dataset_id: int
    status: str
    message: str


# ─────────────────────────────────────────────────────────────────────────────
# Search Schemas
# ─────────────────────────────────────────────────────────────────────────────

class SearchResultItem(BaseModel):
    dataset_id: int
    dataset_name: str
    score: float
    highlight: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetSearchResult(BaseModel):
    """Single dataset search result (for GET /datasets/search)."""
    dataset_id: int
    name: str
    description: str | None = None
    relevance_score: float
    matched_columns: list[str] = Field(default_factory=list)
    snippet: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total_results: int
    search_time_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Data Preview Schemas
# ─────────────────────────────────────────────────────────────────────────────

class DataPreviewResponse(BaseModel):
    dataset_id: int
    columns: list[str]
    data: list[list[Any]]
    rows: list[list[Any]] | None = None
    total_rows: int
    preview_rows: int


# ─────────────────────────────────────────────────────────────────────────────
# List/Filter Schemas
# ─────────────────────────────────────────────────────────────────────────────

class DatasetListResponse(BaseModel):
    items: list[DatasetSummary]
    total: int
    page: int
    page_size: int
    pages: int


class DatasetFilter(BaseModel):
    status: str | None = None
    file_format: str | None = None
    min_quality_score: float | None = None
    has_pii: bool | None = None
    tag_category: str | None = None
    tag_value: str | None = None
