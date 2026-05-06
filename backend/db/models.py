"""
SQLAlchemy ORM models for DataScout.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Boolean,
    BigInteger,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class DatasetStatus(str, PyEnum):
    """Status of dataset processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileFormat(str, PyEnum):
    """Supported file formats."""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "excel"
    TSV = "tsv"


class TagCategory(str, PyEnum):
    """Categories for dataset tags."""
    DOMAIN = "domain"
    DATA_TYPE = "data_type"
    PII_TYPE = "pii_type"
    CUSTOM = "custom"


class TagMethod(str, PyEnum):
    """Method used to generate tag."""
    AI_CLASSIFICATION = "ai_classification"
    REGEX_DETECTION = "regex_detection"
    NER_EXTRACTION = "ner_extraction"
    MANUAL = "manual"


# ─────────────────────────────────────────────────────────────────────────────
# Dataset Model
# ─────────────────────────────────────────────────────────────────────────────

class Dataset(Base):
    """
    Main dataset model representing an uploaded file.
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    file_format = Column(Enum(FileFormat), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    quality_score = Column(Float, nullable=True)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    column_profiles = relationship(
        "ColumnProfile",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tags = relationship(
        "Tag",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quality_scores = relationship(
        "QualityScore",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    dashboard_configs = relationship(
        "DashboardConfig",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_datasets_name_status", "name", "status"),
        Index("ix_datasets_uploaded_at", "uploaded_at"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# ColumnProfile Model
# ─────────────────────────────────────────────────────────────────────────────

class ColumnProfile(Base):
    """
    Statistical profile for a single column in a dataset.
    """
    __tablename__ = "column_profiles"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    column_name = Column(String(255), nullable=False)
    column_index = Column(Integer, nullable=False)
    
    # Data types
    raw_dtype = Column(String(100), nullable=False)
    inferred_type = Column(String(100), nullable=True)
    
    # Missing data
    missing_count = Column(Integer, default=0)
    missing_pct = Column(Float, default=0.0)
    
    # Uniqueness
    unique_count = Column(Integer, nullable=True)
    
    # Numeric statistics (null for non-numeric columns)
    mean = Column(Float, nullable=True)
    median = Column(Float, nullable=True)
    std_dev = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    
    # Distribution data (JSON histogram bins)
    distribution = Column(JSON, nullable=True)
    
    # Outliers
    outlier_count = Column(Integer, default=0)
    
    # Sample values (JSON array)
    sample_values = Column(JSON, nullable=True)
    
    # PII detection
    is_pii = Column(Boolean, default=False, index=True)
    pii_type = Column(String(100), nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="column_profiles")

    __table_args__ = (
        Index("ix_column_profiles_dataset_pii", "dataset_id", "is_pii"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tag Model
# ─────────────────────────────────────────────────────────────────────────────

class Tag(Base):
    """
    Tags and classifications for datasets.
    """
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_category = Column(Enum(TagCategory), nullable=False, index=True)
    tag_value = Column(String(255), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    method = Column(Enum(TagMethod), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="tags")

    __table_args__ = (
        Index("ix_tags_category_value", "tag_category", "tag_value"),
        Index("ix_tags_dataset_category", "dataset_id", "tag_category"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# QualityScore Model
# ─────────────────────────────────────────────────────────────────────────────

class QualityScore(Base):
    """
    Data quality scores across 5 dimensions.
    """
    __tablename__ = "quality_scores"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 5 quality dimensions (0.0 - 1.0)
    completeness = Column(Float, nullable=False)
    consistency = Column(Float, nullable=False)
    uniqueness = Column(Float, nullable=False)
    validity = Column(Float, nullable=False)
    timeliness = Column(Float, nullable=False)
    
    # Overall weighted score
    overall_score = Column(Float, nullable=False, index=True)
    grade = Column(String(2), nullable=False)  # A, B, C, D, F
    
    # Detailed report (JSON)
    details = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    scored_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="quality_scores")


# ─────────────────────────────────────────────────────────────────────────────
# DashboardConfig Model
# ─────────────────────────────────────────────────────────────────────────────

class DashboardConfig(Base):
    """
    Auto-generated dashboard configuration.
    """
    __tablename__ = "dashboard_configs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chart configurations (JSON array)
    charts = Column(JSON, nullable=False)
    
    # KPI configurations (JSON array)
    kpis = Column(JSON, nullable=True)
    
    # Filter configurations (JSON array)
    filters = Column(JSON, nullable=True)
    
    # Layout configuration (JSON)
    layout = Column(JSON, nullable=True)
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="dashboard_configs")
