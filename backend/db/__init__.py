"""
DataScout Database Module - SQLAlchemy models and database utilities.
"""

from db.database import (
    engine,
    async_session_maker,
    get_async_db,
    init_models,
)
from db.models import Base
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

__all__ = [
    # Database utilities
    "Base",
    "engine",
    "async_session_maker",
    "get_async_db",
    "init_models",
    # Models
    "Dataset",
    "ColumnProfile",
    "Tag",
    "QualityScore",
    "DashboardConfig",
    # Enums
    "DatasetStatus",
    "FileFormat",
    "TagCategory",
    "TagMethod",
]
