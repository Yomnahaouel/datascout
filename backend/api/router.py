from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes import datasets
from db.database import get_async_db
from db.models import Dataset

api_router = APIRouter()


@api_router.get("/stats")
async def get_global_stats(db: AsyncSession = Depends(get_async_db)):
    """Global dashboard statistics for the frontend home page."""
    total_result = await db.execute(select(func.count(Dataset.id)))
    total_datasets = total_result.scalar() or 0

    rows_result = await db.execute(select(func.coalesce(func.sum(Dataset.row_count), 0)))
    total_rows = rows_result.scalar() or 0

    quality_result = await db.execute(select(func.avg(Dataset.quality_score)))
    avg_quality = quality_result.scalar()
    avg_quality_pct = round(float(avg_quality) * 100, 1) if avg_quality is not None else 0

    return {
        "total_datasets": total_datasets,
        "total_rows": total_rows,
        "avg_quality": avg_quality_pct,
        "domain_count": 0,
    }

api_router.include_router(datasets.router, tags=["datasets"])
