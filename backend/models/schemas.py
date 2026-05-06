from datetime import datetime
from pydantic import BaseModel


# --- DataSource ---

class DataSourceCreate(BaseModel):
    name: str
    source_type: str
    connection_string: str | None = None


class DataSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    connection_string: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


# --- Job ---

class JobCreate(BaseModel):
    name: str
    source_id: int


class JobResponse(BaseModel):
    id: int
    name: str
    status: str
    source_id: int
    created_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}


# --- Result ---

class ResultResponse(BaseModel):
    id: int
    job_id: int
    data: dict | None
    summary: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}
