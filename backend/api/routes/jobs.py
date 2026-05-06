from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from models.schemas import JobCreate, JobResponse
from models.job import Job

router = APIRouter()


@router.get("/", response_model=list[JobResponse])
async def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.id == job_id).first()
