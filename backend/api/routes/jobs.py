from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from db.models import DataSource, Job
from models.schemas import JobCreate, JobResponse

router = APIRouter()


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> list[JobResponse]:
    result = await db.execute(select(Job).order_by(Job.id.desc()))
    return list(result.scalars().all())


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> JobResponse:
    source_result = await db.execute(
        select(DataSource).where(DataSource.id == payload.source_id)
    )
    if source_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Data source not found")

    job = Job(**payload.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> JobResponse:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
