"""
Data Ingestion Pipeline - Orchestrates all AI engines for dataset processing.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import (
    Dataset,
    ColumnProfile,
    Tag,
    QualityScore,
    DashboardConfig,
    DatasetStatus,
    FileFormat,
    TagCategory,
    TagMethod,
)
from engines import (
    ProfilerEngine,
    TaggerEngine,
    QualityEngine,
    SearchEngine,
    DashboardEngine,
)

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of the ingestion pipeline."""
    success: bool
    dataset_id: int
    row_count: int
    column_count: int
    quality_score: float | None
    error_message: str | None = None
    processing_time_ms: float = 0


class IngestionPipeline:
    """
    Orchestrates the complete data ingestion and analysis pipeline.
    
    Pipeline stages:
    1. Load and validate file
    2. Run Profiler Engine (statistics, outliers)
    3. Run Tagger Engine (domain classification, PII detection)
    4. Run Quality Engine (5-dimension scoring)
    5. Index in Search Engine (semantic search)
    6. Run Dashboard Engine (chart recommendations)
    7. Persist results to database
    """

    def __init__(
        self,
        db: AsyncSession,
        chromadb_host: str = "localhost",
        chromadb_port: int = 8000,
        chromadb_token: str | None = None,
    ):
        self.db = db
        self.chromadb_host = chromadb_host
        self.chromadb_port = chromadb_port
        self.chromadb_token = chromadb_token

        # Initialize engines
        self.profiler = ProfilerEngine()
        self.tagger = TaggerEngine()
        self.quality = QualityEngine()
        self.search = SearchEngine(
            collection_name="dataset_embeddings",
            chromadb_host=chromadb_host,
            chromadb_port=chromadb_port,
            chromadb_token=chromadb_token,
        )
        self.dashboard = DashboardEngine()

    async def process_dataset(self, dataset: Dataset) -> IngestionResult:
        """
        Run the complete ingestion pipeline on a dataset.

        Args:
            dataset: Dataset model to process

        Returns:
            IngestionResult with processing summary
        """
        start_time = datetime.now()
        
        logger.info(f"Starting ingestion pipeline for dataset {dataset.id}: {dataset.name}")

        try:
            # Update status to processing
            dataset.status = DatasetStatus.PROCESSING
            await self.db.commit()

            # Stage 1: Load data
            logger.info(f"Stage 1: Loading data from {dataset.file_path}")
            df = await self._load_dataframe(dataset.file_path, dataset.file_format)
            
            dataset.row_count = len(df)
            dataset.column_count = len(df.columns)

            # Stage 2: Profile data
            logger.info("Stage 2: Running profiler engine")
            profile = await self.profiler.profile(df)
            await self._save_column_profiles(dataset, df, profile)

            # Stage 3: Tag data
            logger.info("Stage 3: Running tagger engine")
            tags = await self.tagger.tag_dataset(df)
            await self._save_tags(dataset, tags)

            # Stage 4: Quality assessment
            logger.info("Stage 4: Running quality engine")
            quality = await self.quality.assess_quality(df)
            await self._save_quality_score(dataset, quality)
            dataset.quality_score = quality.overall_score

            # Stage 5: Index for search
            logger.info("Stage 5: Indexing in search engine")
            await self._index_for_search(dataset, df, tags)

            # Stage 6: Generate dashboard
            logger.info("Stage 6: Running dashboard engine")
            dashboard = await self.dashboard.generate_dashboard(
                df,
                title=dataset.name,
                row_count=dataset.row_count,
                column_count=dataset.column_count,
                file_size=getattr(dataset, "file_size_bytes", None) or getattr(dataset, "file_size", None),
                quality_score=dataset.quality_score,
            )
            await self._save_dashboard_config(dataset, dashboard)

            # Mark as completed
            dataset.status = DatasetStatus.COMPLETED
            dataset.processed_at = datetime.utcnow()
            await self.db.commit()

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(f"Pipeline completed for dataset {dataset.id} in {processing_time:.0f}ms")

            return IngestionResult(
                success=True,
                dataset_id=dataset.id,
                row_count=dataset.row_count,
                column_count=dataset.column_count,
                quality_score=dataset.quality_score,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Pipeline failed for dataset {dataset.id}: {e}", exc_info=True)
            
            dataset.status = DatasetStatus.FAILED
            dataset.error_message = str(e)
            await self.db.commit()

            return IngestionResult(
                success=False,
                dataset_id=dataset.id,
                row_count=0,
                column_count=0,
                quality_score=None,
                error_message=str(e),
            )

    async def _load_dataframe(self, file_path: str, file_format: FileFormat) -> pd.DataFrame:
        """Load file into pandas DataFrame."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        format_loaders = {
            FileFormat.CSV: lambda p: pd.read_csv(p),
            FileFormat.TSV: lambda p: pd.read_csv(p, sep="\t"),
            FileFormat.JSON: lambda p: pd.read_json(p),
            FileFormat.PARQUET: lambda p: pd.read_parquet(p),
            FileFormat.EXCEL: lambda p: pd.read_excel(p),
        }

        loader = format_loaders.get(file_format)
        if not loader:
            raise ValueError(f"Unsupported file format: {file_format}")

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(None, loader, path)
        
        return df

    async def _save_column_profiles(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
        profile: Any,
    ) -> None:
        """Save column profiles to database."""
        for idx, col_profile in enumerate(profile.columns):
            # Histogram data for numeric columns (stored in distribution JSON)
            distribution = None
            if col_profile.mean is not None:
                hist_data = await self.profiler.get_histogram_data(df[col_profile.name])
                distribution = hist_data.get("bins") if isinstance(hist_data, dict) else hist_data

            sample_vals = getattr(col_profile, "sample_values", None)
            if not sample_vals:
                sample_vals = df[col_profile.name].dropna().head(5).tolist()
            sample_vals = [
                str(v) if not isinstance(v, (int, float, bool, str, type(None))) else v
                for v in sample_vals
            ]

            inferred_type = getattr(col_profile, "inferred_type", None) or self._infer_semantic_type(col_profile)

            column_profile = ColumnProfile(
                dataset_id=dataset.id,
                column_name=col_profile.name,
                column_index=idx,
                raw_dtype=col_profile.dtype,
                inferred_type=inferred_type,
                missing_count=col_profile.null_count,
                missing_pct=col_profile.null_percentage,
                unique_count=col_profile.unique_count,
                mean=col_profile.mean,
                median=col_profile.median,
                std_dev=col_profile.std,
                min_value=col_profile.min,
                max_value=col_profile.max,
                distribution=distribution,
                outlier_count=col_profile.outlier_count,
                sample_values=sample_vals,
                is_pii=False,
                pii_type=None,
            )
            self.db.add(column_profile)

        await self.db.flush()

    def _infer_semantic_type(self, col_profile: Any) -> str:
        """Infer semantic type from column profile."""
        dtype = col_profile.dtype.lower()
        name = col_profile.name.lower()

        # Check name patterns
        if any(kw in name for kw in ["id", "key", "code"]):
            return "identifier"
        if any(kw in name for kw in ["date", "time", "timestamp"]):
            return "datetime"
        if any(kw in name for kw in ["email"]):
            return "email"
        if any(kw in name for kw in ["phone", "tel"]):
            return "phone"
        if any(kw in name for kw in ["name", "first", "last"]):
            return "name"
        if any(kw in name for kw in ["address", "street", "city"]):
            return "address"
        if any(kw in name for kw in ["amount", "price", "cost"]):
            return "currency"

        # Check dtype
        if "int" in dtype:
            return "integer"
        if "float" in dtype:
            return "decimal"
        if "bool" in dtype:
            return "boolean"
        if "datetime" in dtype:
            return "datetime"

        return "text"

    async def _save_tags(self, dataset: Dataset, tagging_result: Any) -> None:
        """Save tags and PII info to database."""
        # Domain tags
        for domain in tagging_result.domains:
            tag = Tag(
                dataset_id=dataset.id,
                tag_category=TagCategory.DOMAIN,
                tag_value=domain.label,
                confidence=domain.confidence,
                method=TagMethod.AI_CLASSIFICATION,
            )
            self.db.add(tag)

        # Data type tags
        for data_type in tagging_result.data_types:
            tag = Tag(
                dataset_id=dataset.id,
                tag_category=TagCategory.DATA_TYPE,
                tag_value=data_type.label,
                confidence=data_type.confidence,
                method=TagMethod.AI_CLASSIFICATION,
            )
            self.db.add(tag)

        # PII tags
        pii_report = tagging_result.pii_report
        for pii_type, count in pii_report.pii_by_type.items():
            tag = Tag(
                dataset_id=dataset.id,
                tag_category=TagCategory.PII_TYPE,
                tag_value=pii_type,
                confidence=1.0,
                method=TagMethod.REGEX_DETECTION if pii_type not in ["person_name", "organization"] else TagMethod.NER_EXTRACTION,
            )
            self.db.add(tag)

        # Update column profiles with PII info.
        # Use a direct UPDATE instead of relying on dataset.column_profiles being
        # refreshed. The dataset is loaded before new ColumnProfile rows are
        # inserted, so the relationship can be stale during this same pipeline run.
        for col_name, pii_types in pii_report.pii_by_column.items():
            await self.db.execute(
                update(ColumnProfile)
                .where(
                    ColumnProfile.dataset_id == dataset.id,
                    ColumnProfile.column_name == col_name,
                )
                .values(is_pii=True, pii_type=", ".join(pii_types))
            )

        # Spec: if any column has PII, add dataset-level tag sensitivity/contains_pii
        if pii_report.pii_by_column:
            tag = Tag(
                dataset_id=dataset.id,
                tag_category=TagCategory.CUSTOM,
                tag_value="contains_pii",
                confidence=1.0,
                method=TagMethod.REGEX_DETECTION,
            )
            self.db.add(tag)

        await self.db.flush()

    async def _save_quality_score(self, dataset: Dataset, quality_report: Any) -> None:
        """Save quality score to database."""
        # Extract dimension scores
        dims = {d.name: d.score for d in quality_report.dimensions}

        quality_score = QualityScore(
            dataset_id=dataset.id,
            completeness=dims.get("completeness", 0.0),
            consistency=dims.get("consistency", 0.0),
            uniqueness=dims.get("uniqueness", 0.0),
            validity=dims.get("validity", 0.0),
            timeliness=dims.get("timeliness", 0.0),
            overall_score=quality_report.overall_score,
            grade=quality_report.grade,
            details={
                "critical_issues": quality_report.critical_issues,
                "column_quality": [
                    {
                        "name": cq.name,
                        "completeness": cq.completeness,
                        "validity": cq.validity,
                        "uniqueness": cq.uniqueness,
                        "overall": cq.overall,
                        "issues": cq.issues,
                    }
                    for cq in quality_report.column_quality
                ],
            },
            recommendations=quality_report.recommendations,
        )
        self.db.add(quality_score)
        await self.db.flush()

    async def _index_for_search(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
        tagging_result: Any,
    ) -> None:
        """Index dataset in ChromaDB per spec: name + description + column names + tag values → one document."""
        try:
            parts = [
                dataset.name or "",
                dataset.description or "",
                " ".join(df.columns.astype(str).tolist()),
            ]
            tag_values = []
            for d in getattr(tagging_result, "domains", []):
                tag_values.append(getattr(d, "label", str(d)))
            for dt in getattr(tagging_result, "data_types", []):
                tag_values.append(getattr(dt, "label", str(dt)))
            if tag_values:
                parts.append(" ".join(tag_values))
            text = " ".join(p for p in parts if p).strip()
            await self.search.index_dataset(
                dataset.id,
                text,
                metadata={"dataset_name": dataset.name},
            )
        except Exception as e:
            logger.warning(f"Failed to index dataset {dataset.id} for search: {e}")

    async def _save_dashboard_config(
        self,
        dataset: Dataset,
        dashboard_layout: Any,
    ) -> None:
        """Save dashboard configuration to database (charts include data for frontend)."""
        charts = []
        for c in dashboard_layout.charts:
            chart_type = c.chart_type.value if hasattr(c.chart_type, "value") else c.chart_type
            chart_dict = {
                "chart_type": chart_type,
                "title": c.title,
                "x_axis": c.x_axis,
                "y_axis": c.y_axis,
                "color_by": c.color_by,
                "size_by": c.size_by,
                "aggregation": c.aggregation,
                "confidence": c.confidence,
                "reason": c.reason,
                "config": c.config or {},
            }
            if getattr(c, "data", None) is not None:
                chart_dict["data"] = c.data
            charts.append(chart_dict)

        dashboard_config = DashboardConfig(
            dataset_id=dataset.id,
            charts=charts,
            kpis=dashboard_layout.kpis,
            filters=dashboard_layout.filters,
            layout=dashboard_layout.layout_config,
        )
        self.db.add(dashboard_config)
        await self.db.flush()


async def run_ingestion_background(
    dataset_id: int,
    db_url: str,
    chromadb_host: str = "localhost",
    chromadb_port: int = 8000,
    chromadb_token: str | None = None,
) -> None:
    """
    Run ingestion pipeline as a background task.
    Creates its own database session.
    """
    from db.database import async_session_maker

    async with async_session_maker() as db:
        # Fetch dataset
        from sqlalchemy import select
        result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()

        if not dataset:
            logger.error(f"Dataset {dataset_id} not found")
            return

        pipeline = IngestionPipeline(
            db=db,
            chromadb_host=chromadb_host,
            chromadb_port=chromadb_port,
            chromadb_token=chromadb_token,
        )

        await pipeline.process_dataset(dataset)
