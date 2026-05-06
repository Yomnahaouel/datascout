import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DataScout"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database - PostgreSQL async
    DATABASE_URL: str = "postgresql+asyncpg://datascout:datascout@localhost:5432/datascout"

    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Pipeline
    MAX_CONCURRENT_JOBS: int = 4

    # File uploads
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # ChromaDB
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    CHROMADB_TOKEN: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
