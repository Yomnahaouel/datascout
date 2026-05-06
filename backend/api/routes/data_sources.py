from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from models.schemas import DataSourceCreate, DataSourceResponse
from models.data_source import DataSource

router = APIRouter()


@router.get("/", response_model=list[DataSourceResponse])
async def list_sources(db: Session = Depends(get_db)):
    return db.query(DataSource).all()


@router.post("/", response_model=DataSourceResponse, status_code=201)
async def create_source(payload: DataSourceCreate, db: Session = Depends(get_db)):
    source = DataSource(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/{source_id}", response_model=DataSourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    return db.query(DataSource).filter(DataSource.id == source_id).first()
