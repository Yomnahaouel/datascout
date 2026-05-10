from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from db.models import DataSource
from models.schemas import DataSourceCreate, DataSourceResponse

router = APIRouter()


@router.get("/", response_model=list[DataSourceResponse])
async def list_sources(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> list[DataSourceResponse]:
    result = await db.execute(select(DataSource).order_by(DataSource.id.desc()))
    return list(result.scalars().all())


@router.post("/", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: DataSourceCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> DataSourceResponse:
    source = DataSource(**payload.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.get("/{source_id}", response_model=DataSourceResponse)
async def get_source(
    source_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> DataSourceResponse:
    result = await db.execute(select(DataSource).where(DataSource.id == source_id))
    source = result.scalar_one_or_none()
    if source is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    return source
