"""
Dataset API Routes - CRUD operations, search, and analysis endpoints.
"""

from __future__ import annotations

import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import pandas as pd
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api.schemas import (
    DataPreviewResponse,
    DatasetCreate,
    DatasetDetail,
    DatasetListResponse,
    DatasetResponse,
    QualityScoreResponse,
    DatasetSearchResult,
)
from config import settings
from db.database import get_async_db
from db.models import (
    ColumnProfile,
    DashboardConfig,
    Dataset,
    DatasetStatus,
    FileFormat,
    QualityScore,
    Tag,
)
from pipeline.ingestion import IngestionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    ".csv": FileFormat.CSV,
    ".tsv": FileFormat.TSV,
    ".json": FileFormat.JSON,
    ".parquet": FileFormat.PARQUET,
    ".xlsx": FileFormat.EXCEL,
    ".xls": FileFormat.EXCEL,
}

# Upload directory
UPLOAD_DIR = Path(settings.UPLOAD_DIR if hasattr(settings, "UPLOAD_DIR") else "/app/uploads")


def get_file_format(filename: str) -> FileFormat | None:
    """Determine file format from extension."""
    ext = Path(filename).suffix.lower()
    return ALLOWED_EXTENSIONS.get(ext)


async def save_upload_file(upload_file: UploadFile, dest_path: Path) -> None:
    """Save uploaded file to disk."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dest_path, "wb") as f:
        while chunk := await upload_file.read(1024 * 1024):  # 1MB chunks
            f.write(chunk)


# -----------------------------------------------------------------------------
# Upload endpoint
# -----------------------------------------------------------------------------


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    file: UploadFile = File(...),
    name: str | None = Form(None),
    description: str | None = Form(None),
    source: str | None = Form(None),
) -> DatasetResponse:
    """
    Upload a new dataset file and trigger processing pipeline.

    Supported formats: CSV, TSV, JSON, Parquet, Excel

    The file will be saved and processing will begin in the background.
    Check the dataset status to see when processing is complete.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_format = get_file_format(file.filename)
    if not file_format:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}",
        )

    # Generate unique file path
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"

    # Save file
    try:
        await save_upload_file(file, file_path)
    except Exception as e:
        logger.error(f"Failed to save upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    # Get file size
    file_size = file_path.stat().st_size

    # Create dataset record
    dataset = Dataset(
        name=name or file.filename,
        description=description,
        file_path=str(file_path),
        file_format=file_format,
        file_size_bytes=file_size,
        status=DatasetStatus.PENDING,
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)

    # Start background processing
    background_tasks.add_task(
        run_pipeline_background,
        dataset_id=dataset.id,
    )

    return DatasetResponse.model_validate(dataset)


async def run_pipeline_background(dataset_id: int) -> None:
    """Background task to run the ingestion pipeline."""
    from db.database import async_session_maker

    async with async_session_maker() as db:
        # Fetch dataset with all relationships
        result = await db.execute(
            select(Dataset)
            .options(selectinload(Dataset.column_profiles))
            .where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            logger.error(f"Dataset {dataset_id} not found for processing")
            return

        # Run pipeline
        chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
        chromadb_port = int(os.getenv("CHROMADB_PORT", "8000"))
        chromadb_token = os.getenv("CHROMADB_TOKEN")

        pipeline = IngestionPipeline(
            db=db,
            chromadb_host=chromadb_host,
            chromadb_port=chromadb_port,
            chromadb_token=chromadb_token,
        )

        await pipeline.process_dataset(dataset)


# -----------------------------------------------------------------------------
# List / Read endpoints
# -----------------------------------------------------------------------------


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    status_filter: DatasetStatus | None = Query(None, alias="status"),
    format_filter: FileFormat | None = Query(None, alias="format"),
    search_name: str | None = Query(None, description="Filter by name (case-insensitive)"),
    sort_by: str = Query("uploaded_at", description="Field to sort by"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
) -> DatasetListResponse:
    """
    List all datasets with optional filtering and pagination.
    """
    # Build query
    query = select(Dataset)

    # Apply filters
    if status_filter:
        query = query.where(Dataset.status == status_filter)
    if format_filter:
        query = query.where(Dataset.file_format == format_filter)
    if search_name:
        query = query.where(Dataset.name.ilike(f"%{search_name}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    sort_column = getattr(Dataset, sort_by, Dataset.uploaded_at)
    if sort_desc:
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    datasets = result.scalars().all()

    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return DatasetListResponse(
        items=[DatasetResponse.model_validate(d) for d in datasets],
        total=total,
        page=page,
        page_size=limit,
        pages=pages,
    )


@router.get("/{dataset_id}", response_model=DatasetDetail)
async def get_dataset(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> DatasetDetail:
    """
    Get detailed information about a specific dataset.

    Includes column profiles, tags, quality score, and dashboard config.
    """
    result = await db.execute(
        select(Dataset)
        .options(
            selectinload(Dataset.column_profiles),
            selectinload(Dataset.tags),
            selectinload(Dataset.quality_scores),
            selectinload(Dataset.dashboard_configs),
        )
        .where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return DatasetDetail.model_validate(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> None:
    """
    Delete a dataset and its associated file.

    This will also delete all related data (profiles, tags, quality scores, etc.)
    via cascade.
    """
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Delete file
    try:
        file_path = Path(dataset.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to delete file {dataset.file_path}: {e}")

    # Delete from database (cascades to related tables)
    await db.delete(dataset)
    await db.commit()


# -----------------------------------------------------------------------------
# Search endpoint
# -----------------------------------------------------------------------------


@router.get("/search", response_model=list[DatasetSearchResult])
async def search_datasets(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
) -> list[DatasetSearchResult]:
    """
    Semantic search across all datasets (spec: sentence-transformers + ChromaDB).
    """
    from engines import SearchEngine

    try:
        chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
        chromadb_port = int(os.getenv("CHROMADB_PORT", "8000"))
        chromadb_token = os.getenv("CHROMADB_TOKEN")

        search_engine = SearchEngine(
            collection_name="dataset_embeddings",
            chromadb_host=chromadb_host,
            chromadb_port=chromadb_port,
            chromadb_token=chromadb_token,
        )

        search_resp = await search_engine.search(q, top_k=limit)

        enriched = []
        for result in search_resp.results:
            dataset_id = result.metadata.get("dataset_id")
            if dataset_id is None and result.id.isdigit():
                dataset_id = int(result.id)
            if dataset_id is None:
                continue
            try:
                ds_result = await db.execute(
                    select(Dataset).where(Dataset.id == int(dataset_id))
                )
                dataset = ds_result.scalar_one_or_none()
                if dataset:
                    enriched.append(
                        DatasetSearchResult(
                            dataset_id=dataset.id,
                            name=dataset.name,
                            description=dataset.description,
                            relevance_score=result.score,
                            matched_columns=[],
                            snippet=result.content[:500] if result.content else None,
                        )
                    )
            except (ValueError, TypeError):
                continue

        return enriched

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search service unavailable")


# -----------------------------------------------------------------------------
# Profile endpoint
# -----------------------------------------------------------------------------


@router.get("/{dataset_id}/profile")
async def get_dataset_profile(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> list[dict[str, Any]]:
    """
    Get column profiles for a dataset.

    Returns statistical information about each column.
    """
    # Verify dataset exists
    ds_result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    if not ds_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = await db.execute(
        select(ColumnProfile)
        .where(ColumnProfile.dataset_id == dataset_id)
        .order_by(ColumnProfile.column_index)
    )
    profiles = result.scalars().all()

    return [
        {
            "column_name": p.column_name,
            "column_index": p.column_index,
            "raw_dtype": p.raw_dtype,
            "inferred_type": p.inferred_type,
            "missing_count": p.missing_count,
            "missing_pct": p.missing_pct,
            "unique_count": p.unique_count,
            "mean": p.mean,
            "median": p.median,
            "std_dev": p.std_dev,
            "min_value": p.min_value,
            "max_value": p.max_value,
            "distribution": p.distribution,
            "outlier_count": p.outlier_count,
            "sample_values": p.sample_values,
            "is_pii": p.is_pii,
            "pii_type": p.pii_type,
        }
        for p in profiles
    ]


# -----------------------------------------------------------------------------
# Quality endpoint
# -----------------------------------------------------------------------------


@router.get("/{dataset_id}/quality", response_model=QualityScoreResponse | None)
async def get_dataset_quality(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> QualityScoreResponse | None:
    """
    Get quality assessment for a dataset.

    Returns scores across 5 quality dimensions plus recommendations.
    """
    # Verify dataset exists
    ds_result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    if not ds_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = await db.execute(
        select(QualityScore).where(QualityScore.dataset_id == dataset_id)
    )
    quality = result.scalar_one_or_none()

    if not quality:
        return None

    return QualityScoreResponse.model_validate(quality)


# -----------------------------------------------------------------------------
# Dashboard endpoint
# -----------------------------------------------------------------------------


@router.get("/{dataset_id}/dashboard")
async def get_dataset_dashboard(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> dict[str, Any] | None:
    """
    Get auto-generated dashboard configuration for a dataset.

    Returns recommended charts, KPIs, and layout settings.
    """
    # Verify dataset exists
    ds_result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    if not ds_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = await db.execute(
        select(DashboardConfig).where(DashboardConfig.dataset_id == dataset_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        return None

    return {
        "id": dashboard.id,
        "dataset_id": dashboard.dataset_id,
        "charts": dashboard.charts,
        "kpis": dashboard.kpis,
        "filters": dashboard.filters,
        "layout": dashboard.layout,
        "created_at": dashboard.created_at.isoformat() if dashboard.created_at else None,
        "generated_at": dashboard.generated_at.isoformat() if dashboard.generated_at else None,
    }


# -----------------------------------------------------------------------------
# Preview endpoint
# -----------------------------------------------------------------------------


@router.get("/{dataset_id}/preview", response_model=DataPreviewResponse)
async def preview_dataset(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    rows: int = Query(100, ge=1, le=1000, description="Number of rows to preview"),
    offset: int = Query(0, ge=0, description="Row offset"),
) -> DataPreviewResponse:
    """
    Preview the raw data from a dataset.

    Returns column headers and row data for display.
    """
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if dataset.status != DatasetStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Dataset not ready. Status: {dataset.status.value}",
        )

    # Load data
    try:
        file_path = Path(dataset.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")

        # Load based on format
        format_loaders = {
            FileFormat.CSV: lambda: pd.read_csv(file_path, skiprows=range(1, offset + 1) if offset > 0 else None, nrows=rows),
            FileFormat.TSV: lambda: pd.read_csv(file_path, sep="\t", skiprows=range(1, offset + 1) if offset > 0 else None, nrows=rows),
            FileFormat.JSON: lambda: pd.read_json(file_path).iloc[offset:offset + rows],
            FileFormat.PARQUET: lambda: pd.read_parquet(file_path).iloc[offset:offset + rows],
            FileFormat.EXCEL: lambda: pd.read_excel(file_path, skiprows=range(1, offset + 1) if offset > 0 else None, nrows=rows),
        }

        loader = format_loaders.get(dataset.file_format)
        if not loader:
            raise HTTPException(status_code=400, detail="Unsupported format for preview")

        df = loader()

        # Convert to response format
        columns = df.columns.tolist()
        data = df.fillna("").values.tolist()

        # Convert non-serializable types
        data = [
            [
                str(cell) if not isinstance(cell, (int, float, bool, str, type(None))) else cell
                for cell in row
            ]
            for row in data
        ]

        return DataPreviewResponse(
            columns=columns,
            data=data,
            total_rows=dataset.row_count or len(df),
            preview_rows=len(data),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview dataset {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dataset preview")


# -----------------------------------------------------------------------------
# Tags endpoint
# -----------------------------------------------------------------------------


@router.get("/{dataset_id}/tags")
async def get_dataset_tags(
    dataset_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> list[dict[str, Any]]:
    """
    Get all tags associated with a dataset.

    Tags include domain classifications, data types, and PII detections.
    """
    # Verify dataset exists
    ds_result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    if not ds_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = await db.execute(
        select(Tag).where(Tag.dataset_id == dataset_id)
    )
    tags = result.scalars().all()

    return [
        {
            "id": t.id,
            "category": t.tag_category.value,
            "value": t.tag_value,
            "confidence": t.confidence,
            "method": t.method.value,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tags
    ]


# -----------------------------------------------------------------------------
# Reprocess endpoint
# -----------------------------------------------------------------------------


@router.post("/{dataset_id}/reprocess", response_model=DatasetResponse)
async def reprocess_dataset(
    dataset_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> DatasetResponse:
    """
    Trigger reprocessing of a dataset.

    Useful if processing failed or you want to update with new engine versions.
    """
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Clear existing analysis data
    await db.execute(delete(ColumnProfile).where(ColumnProfile.dataset_id == dataset_id))
    await db.execute(delete(Tag).where(Tag.dataset_id == dataset_id))
    await db.execute(delete(QualityScore).where(QualityScore.dataset_id == dataset_id))
    await db.execute(delete(DashboardConfig).where(DashboardConfig.dataset_id == dataset_id))

    # Reset status
    dataset.status = DatasetStatus.PENDING
    dataset.error_message = None
    await db.commit()
    await db.refresh(dataset)

    # Start background processing
    background_tasks.add_task(run_pipeline_background, dataset_id=dataset.id)

    return DatasetResponse.model_validate(dataset)
