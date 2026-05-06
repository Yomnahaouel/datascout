"""
Profiler Engine - Statistical analysis of datasets per PROJECT_SPECIFICATION.md
Uses pandas, scipy (Shapiro, skewness), and IsolationForest for outlier detection.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

# Regex patterns for inferred_type (spec)
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)


@dataclass
class ColumnProfile:
    """Profile statistics for a single column (spec-aligned)."""
    name: str
    dtype: str
    count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float

    # Numeric stats (optional)
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    median: float | None = None
    q1: float | None = None
    q3: float | None = None
    skewness: float | None = None
    kurtosis: float | None = None

    # Spec: inferred semantic type
    inferred_type: str = "text"
    # Spec: distribution label (normal, right_skewed, left_skewed, uniform)
    distribution: str | None = None
    # Spec: 5 random non-null sample values
    sample_values: list[Any] = field(default_factory=list)

    # Categorical stats (optional)
    top_values: list[dict[str, Any]] = field(default_factory=list)

    # Outlier info (IsolationForest contamination=0.05)
    outlier_count: int = 0
    outlier_indices: list[int] = field(default_factory=list)


@dataclass
class DatasetProfile:
    """Complete profile of a dataset."""
    row_count: int
    column_count: int
    memory_usage_mb: float
    duplicate_row_count: int
    columns: list[ColumnProfile]
    correlations: dict[str, dict[str, float]] | None = None
    outlier_summary: dict[str, int] = field(default_factory=dict)


class ProfilerEngine:
    """
    Auto-profiler per spec: column types, statistics, distribution (Shapiro + skewness),
    outlier count (IsolationForest contamination=0.05), sample values.
    """

    def __init__(
        self,
        outlier_contamination: float = 0.05,
        correlation_threshold: float = 0.5,
        top_n_values: int = 10,
    ):
        self.outlier_contamination = outlier_contamination
        self.correlation_threshold = correlation_threshold
        self.top_n_values = top_n_values
        self._isolation_forest: IsolationForest | None = None

    async def profile(self, data: pd.DataFrame) -> DatasetProfile:
        """Generate a comprehensive profile of the dataset (spec)."""
        logger.info(f"Profiling dataset with shape {data.shape}")

        row_count = len(data)
        column_count = len(data.columns)
        memory_usage_mb = data.memory_usage(deep=True).sum() / (1024 * 1024)
        duplicate_row_count = int(data.duplicated().sum())

        columns = []
        for col in data.columns:
            col_profile = await self._profile_column(data[col])
            columns.append(col_profile)

        # Outlier detection (updates column profiles)
        outlier_summary = await self._detect_outliers(data, columns)

        # Correlation analysis for numeric columns
        correlations = await self._compute_correlations(data)

        return DatasetProfile(
            row_count=row_count,
            column_count=column_count,
            memory_usage_mb=round(memory_usage_mb, 3),
            duplicate_row_count=duplicate_row_count,
            columns=columns,
            correlations=correlations,
            outlier_summary=outlier_summary,
        )

    def _infer_semantic_type(self, series: pd.Series, name: str) -> str:
        """Infer semantic type per spec heuristics."""
        name_lower = name.lower()
        dtype = str(series.dtype).lower()

        # Email: column name or values match email regex
        if "email" in name_lower:
            return "email"
        sample_str = series.dropna().astype(str).head(100)
        if len(sample_str) > 0 and sum(1 for v in sample_str if EMAIL_RE.match(v)) / len(sample_str) >= 0.5:
            return "email"

        # Person name: column contains "name" and dtype object
        if ("name" in name_lower or "first" in name_lower or "last" in name_lower) and series.dtype == object:
            return "person_name"

        # Phone: column name or values match phone regex
        if "phone" in name_lower or "tel" in name_lower:
            return "phone"
        if len(sample_str) > 0 and sum(1 for v in sample_str if PHONE_RE.search(v)) / len(sample_str) >= 0.5:
            return "phone"

        # Date: column name or datetime dtype
        if "date" in name_lower or "time" in name_lower or "timestamp" in name_lower:
            return "date"
        if "datetime" in dtype or pd.api.types.is_datetime64_any_dtype(series):
            return "date"

        # Identifier: column name contains "id" or "ID"
        if "id" in name_lower or "ID" in name:
            return "identifier"

        # Monetary: float/int, all positive, 2 decimal places
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if len(clean) > 0 and (clean >= 0).all():
                as_str = clean.astype(str)
                if sum(1 for v in as_str if "." in v and len(v.split(".")[-1]) >= 2) / len(as_str) >= 0.5:
                    return "monetary"
            return "numeric"

        # Binary: bool or unique count == 2
        if pd.api.types.is_bool_dtype(series):
            return "binary"
        if series.nunique() == 2:
            return "binary"

        # Categorical: object and unique count < 20
        if (pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series)) and series.nunique() < 20:
            return "categorical"

        # Numeric (int/float)
        if "int" in dtype or "float" in dtype:
            return "numeric"

        return "text"

    def _distribution_label(self, series: pd.Series) -> str | None:
        """Per spec: Shapiro for normality; skewness for skewed; else uniform."""
        clean = series.dropna()
        if len(clean) < 30:
            return None
        try:
            _, p_shapiro = stats.shapiro(clean)
            if p_shapiro > 0.05:
                return "normal"
            skew = float(stats.skew(clean))
            if skew > 1:
                return "right_skewed"
            if skew < -1:
                return "left_skewed"
            return "uniform"
        except Exception:
            return None

    async def _profile_column(self, series: pd.Series) -> ColumnProfile:
        """Profile a single column (spec: raw_dtype, inferred_type, missing, unique, numeric stats, distribution, outlier_count, sample_values)."""
        name = series.name
        dtype = str(series.dtype)
        count = len(series)
        null_count = int(series.isna().sum())
        null_percentage = round(null_count / count * 100, 2) if count > 0 else 0.0
        unique_count = series.nunique()
        unique_percentage = round(unique_count / count * 100, 2) if count > 0 else 0.0

        inferred_type = self._infer_semantic_type(series, str(name))
        non_null = series.dropna()
        sample_values = list(non_null.sample(n=min(5, len(non_null)), random_state=42).tolist()) if len(non_null) > 0 else []
        # Ensure JSON-serializable
        sample_values = [v if isinstance(v, (int, float, bool, str, type(None))) else str(v) for v in sample_values]

        distribution = None
        if pd.api.types.is_numeric_dtype(series):
            distribution = self._distribution_label(series)

        profile = ColumnProfile(
            name=str(name),
            dtype=dtype,
            count=count,
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
            inferred_type=inferred_type,
            distribution=distribution,
            sample_values=sample_values,
        )

        if pd.api.types.is_numeric_dtype(series):
            if len(non_null) > 0:
                profile.mean = round(float(non_null.mean()), 4)
                profile.std = round(float(non_null.std()), 4) if len(non_null) > 1 else 0.0
                profile.min = round(float(non_null.min()), 4)
                profile.max = round(float(non_null.max()), 4)
                profile.median = round(float(non_null.median()), 4)
                profile.q1 = round(float(non_null.quantile(0.25)), 4)
                profile.q3 = round(float(non_null.quantile(0.75)), 4)
                if len(non_null) >= 3:
                    profile.skewness = round(float(stats.skew(non_null)), 4)
                    profile.kurtosis = round(float(stats.kurtosis(non_null)), 4)

        if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
            value_counts = series.value_counts().head(self.top_n_values)
            profile.top_values = [
                {"value": str(val), "count": int(cnt), "percentage": round(cnt / count * 100, 2)}
                for val, cnt in value_counts.items()
            ]

        return profile

    async def _compute_correlations(
        self, data: pd.DataFrame
    ) -> dict[str, dict[str, float]] | None:
        """Compute correlation matrix for numeric columns."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return None
        corr_matrix = data[numeric_cols].corr()
        correlations: dict[str, dict[str, float]] = {}
        for col1 in corr_matrix.columns:
            col_corrs = {}
            for col2 in corr_matrix.columns:
                if col1 != col2:
                    val = corr_matrix.loc[col1, col2]
                    if abs(val) >= self.correlation_threshold:
                        col_corrs[str(col2)] = round(float(val), 4)
            if col_corrs:
                correlations[str(col1)] = col_corrs
        return correlations if correlations else None

    async def _detect_outliers(
        self, data: pd.DataFrame, columns: list[ColumnProfile]
    ) -> dict[str, int]:
        """IsolationForest with contamination=0.05; count predictions == -1."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return {}

        outlier_summary: dict[str, int] = {}
        for col in numeric_cols:
            series = data[col].dropna()
            if len(series) < 10:
                continue
            X = series.values.reshape(-1, 1)
            model = IsolationForest(
                contamination=self.outlier_contamination,
                random_state=42,
                n_jobs=-1,
            )
            predictions = model.fit_predict(X)
            outlier_mask = predictions == -1
            outlier_count = int(outlier_mask.sum())
            outlier_indices = series.index[outlier_mask].tolist()[:100]

            for cp in columns:
                if cp.name == col:
                    cp.outlier_count = outlier_count
                    cp.outlier_indices = outlier_indices
                    break
            if outlier_count > 0:
                outlier_summary[col] = outlier_count

        return outlier_summary

    async def detect_distribution(self, series: pd.Series) -> dict[str, Any]:
        """Detect distribution type (optional helper)."""
        clean_data = series.dropna().values
        if len(clean_data) < 30:
            return {"distribution": "unknown", "reason": "insufficient_data"}
        label = self._distribution_label(series)
        return {"distribution": label or "unknown", "reason": "shapiro_skewness"}

    async def get_histogram_data(
        self, series: pd.Series, bins: int = 30
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Generate histogram data for visualization (pipeline expects this format)."""
        clean_data = series.dropna()
        if len(clean_data) == 0:
            return {"bins": [], "counts": [], "edges": []}

        counts, edges = np.histogram(clean_data, bins=bins)
        return {
            "bins": [
                {"bin_start": round(float(edges[i]), 4), "bin_end": round(float(edges[i + 1]), 4), "count": int(c)}
                for i, c in enumerate(counts)
            ],
            "counts": [int(c) for c in counts],
            "edges": [round(float(e), 4) for e in edges],
        }
