"""
Dashboard Engine - Auto-generated dashboard config per PROJECT_SPECIFICATION.md
Reads column characteristics from DataFrame; produces chart configs with data for frontend.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ChartType(str, Enum):
    """Spec chart types (values match frontend renderChart)."""
    KPI_CARDS = "kpi_cards"
    HISTOGRAM = "histogram"
    BOX_PLOT = "boxplot"
    BAR_CHART = "bar"
    PIE_CHART = "pie"
    CLASS_BALANCE = "class_balance"
    TIME_SERIES = "time_series"
    HEATMAP = "heatmap"
    MISSING_VALUES_MAP = "missing"


@dataclass
class ChartRecommendation:
    """Chart config with data for frontend."""
    chart_type: ChartType | str
    title: str
    x_axis: str | None = None
    y_axis: str | None = None
    color_by: str | None = None
    size_by: str | None = None
    aggregation: str | None = None
    confidence: float = 0.0
    reason: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    # Frontend reads chart.data or chart.config.data
    data: list[Any] | dict[str, Any] | None = None


@dataclass
class DashboardLayout:
    """Complete dashboard config (spec)."""
    title: str
    charts: list[ChartRecommendation]
    kpis: list[dict[str, Any]]
    filters: list[str]
    layout_config: dict[str, Any] = field(default_factory=dict)


def _infer_type(col: str, series: pd.Series) -> str:
    """Infer column type for chart selection."""
    name = col.lower()
    dtype = str(series.dtype).lower()
    n = series.nunique()

    if pd.api.types.is_datetime64_any_dtype(series) or "date" in name or "time" in name:
        return "date"
    if pd.api.types.is_bool_dtype(series) or n == 2:
        return "binary"
    if pd.api.types.is_numeric_dtype(series):
        if "amount" in name or "price" in name or "cost" in name:
            return "monetary"
        return "numeric"
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
        if n < 8:
            return "categorical_small"
        if n < 20:
            return "categorical"
        return "text"
    return "text"


class DashboardEngine:
    """
    Spec: kpi_cards; per column histogram/box for numeric/monetary; bar for categorical <20;
    pie for categorical <8; class_balance for binary; time_series for date; heatmap if 2+ numeric;
    missing_values_map if any missing_pct > 0.
    """

    def __init__(self, max_categories_bar: int = 20, max_categories_pie: int = 8):
        self.max_categories_bar = max_categories_bar
        self.max_categories_pie = max_categories_pie

    async def generate_dashboard(
        self,
        data: pd.DataFrame,
        title: str = "Data Dashboard",
        row_count: int | None = None,
        column_count: int | None = None,
        file_size: int | None = None,
        quality_score: float | None = None,
    ) -> DashboardLayout:
        """Generate dashboard config with chart data (spec)."""
        logger.info(f"Generating dashboard for dataset with shape {data.shape}")

        row_count = row_count or len(data)
        column_count = column_count or len(data.columns)
        charts: list[ChartRecommendation] = []

        # 1. Always add kpi_cards (spec)
        charts.append(
            ChartRecommendation(
                chart_type=ChartType.KPI_CARDS,
                title="Overview",
                config={
                    "data": {
                        "rows": row_count,
                        "columns": column_count,
                        "size": file_size or 0,
                        "quality": quality_score,
                    },
                },
            )
        )

        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

        # 2. Per column: histogram, box, bar, pie, class_balance, time_series
        for col in data.columns:
            series = data[col].dropna()
            inferred = _infer_type(col, data[col])
            n_unique = data[col].nunique()
            missing_pct = data[col].isna().mean() * 100

            if inferred in ("numeric", "monetary"):
                if len(series) > 0:
                    counts, edges = np.histogram(series, bins=min(30, max(5, len(series) // 10)))
                    charts.append(
                        ChartRecommendation(
                            chart_type=ChartType.HISTOGRAM,
                            title=f"Distribution of {col}",
                            x_axis=col,
                            config={"column": col},
                            data=[
                                {"bin_start": float(edges[i]), "bin_end": float(edges[i + 1]), "count": int(counts[i])}
                                for i in range(len(counts))
                            ],
                        )
                    )
                    q1, q2, q3 = series.quantile([0.25, 0.5, 0.75])
                    charts.append(
                        ChartRecommendation(
                            chart_type=ChartType.BOX_PLOT,
                            title=f"Box plot: {col}",
                            config={"column": col},
                            data=[
                                {
                                    "name": col,
                                    "min": float(series.min()),
                                    "q1": float(q1),
                                    "median": float(q2),
                                    "q3": float(q3),
                                    "max": float(series.max()),
                                }
                            ],
                        )
                    )

            elif inferred == "categorical" and n_unique < self.max_categories_bar:
                vc = data[col].value_counts()
                charts.append(
                    ChartRecommendation(
                        chart_type=ChartType.BAR_CHART,
                        title=f"Count by {col}",
                        config={"column": col},
                        data=[{"name": str(k), "value": int(v)} for k, v in vc.items()],
                    )
                )
            elif inferred == "categorical_small" and n_unique < self.max_categories_pie:
                vc = data[col].value_counts()
                charts.append(
                    ChartRecommendation(
                        chart_type=ChartType.PIE_CHART,
                        title=f"Distribution: {col}",
                        config={"column": col},
                        data=[{"name": str(k), "value": int(v)} for k, v in vc.items()],
                    )
                )
            elif inferred == "binary":
                vc = data[col].value_counts()
                charts.append(
                    ChartRecommendation(
                        chart_type=ChartType.CLASS_BALANCE,
                        title=f"Class balance: {col}",
                        config={"column": col},
                        data=[{"name": str(k), "count": int(v)} for k, v in vc.items()],
                    )
                )
            elif inferred == "date" and len(series) > 0:
                try:
                    dt = pd.to_datetime(data[col], errors="coerce").dropna()
                    counts = dt.dt.date.value_counts().sort_index()
                    charts.append(
                        ChartRecommendation(
                            chart_type=ChartType.TIME_SERIES,
                            title=f"Over time: {col}",
                            config={"column": col},
                            data=[{"date": str(k), "count": int(v)} for k, v in counts.items()],
                        )
                    )
                except Exception:
                    pass

        # 3. Heatmap if 2+ numeric (spec)
        if len(numeric_cols) >= 2:
            corr = data[numeric_cols].corr()
            heat_data = []
            for i, c1 in enumerate(corr.columns):
                for j, c2 in enumerate(corr.columns):
                    if i != j:
                        heat_data.append({"x": c1, "y": c2, "value": round(float(corr.iloc[i, j]), 3)})
            charts.append(
                ChartRecommendation(
                    chart_type=ChartType.HEATMAP,
                    title="Correlation matrix",
                    config={"columns": numeric_cols},
                    data=heat_data,
                )
            )

        # 4. Missing values map if any column has missing_pct > 0 (spec)
        missing_info = []
        for col in data.columns:
            pct = data[col].isna().mean() * 100
            if pct > 0:
                missing_info.append({
                    "column": col,
                    "missing_pct": round(pct, 2),
                    "missing_count": int(data[col].isna().sum()),
                })
        if missing_info:
            charts.append(
                ChartRecommendation(
                    chart_type=ChartType.MISSING_VALUES_MAP,
                    title="Missing values by column",
                    config={},
                    data=missing_info,
                )
            )

        # KPIs for layout (spec uses kpi_cards in charts; keep kpis list for pipeline)
        kpis = [
            {"label": "Rows", "value": row_count, "format": "number", "icon": None},
            {"label": "Columns", "value": column_count, "format": "number", "icon": None},
            {"label": "Size", "value": file_size or 0, "format": "bytes", "icon": None},
            {"label": "Quality", "value": quality_score, "format": "percent", "icon": None},
        ]

        layout_config = {
            "columns": 2,
            "rows": (len(charts) + 1) // 2,
            "chart_height": 350,
        }

        return DashboardLayout(
            title=title,
            charts=charts,
            kpis=kpis,
            filters=[],
            layout_config=layout_config,
        )
