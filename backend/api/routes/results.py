from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from db.models import Job, Result
from models.schemas import ResultCreate, ResultResponse

router = APIRouter()


@router.get("/", response_model=list[ResultResponse])
async def list_results(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    job_id: int | None = Query(None, description="Filter results by job id"),
) -> list[ResultResponse]:
    query = select(Result).order_by(Result.id.desc())
    if job_id is not None:
        query = query.where(Result.job_id == job_id)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
async def create_result(
    payload: ResultCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> ResultResponse:
    job_result = await db.execute(select(Job).where(Job.id == payload.job_id))
    if job_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Job not found")

    result_row = Result(**payload.model_dump())
    db.add(result_row)
    await db.commit()
    await db.refresh(result_row)
    return result_row


@router.get("/{result_id}", response_model=ResultResponse)
async def get_result(
    result_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> ResultResponse:
    result = await db.execute(select(Result).where(Result.id == result_id))
    result_row = result.scalar_one_or_none()
    if result_row is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result_row
