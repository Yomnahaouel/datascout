"""
DataScout AI Engines
====================

This package contains the core AI/ML engines for data analysis:

- ProfilerEngine: Statistical analysis, distributions, outlier detection
- TaggerEngine: Domain classification, PII detection
- QualityEngine: 5-dimension data quality scoring
- SearchEngine: Semantic search with sentence-transformers + ChromaDB
- DashboardEngine: Automatic chart recommendation
"""

from engines.base import BaseEngine  # noqa: F401
from engines.profiler_engine import ProfilerEngine, DatasetProfile, ColumnProfile  # noqa: F401
from engines.tagger_engine import TaggerEngine, TaggingResult, PIIReport  # noqa: F401
from engines.quality_engine import QualityEngine, QualityReport  # noqa: F401
from engines.search_engine import SearchEngine, SearchResponse, SearchResult  # noqa: F401
from engines.dashboard_engine import DashboardEngine, DashboardLayout, ChartRecommendation, ChartType  # noqa: F401

__all__ = [
    # Base
    "BaseEngine",
    # Profiler
    "ProfilerEngine",
    "DatasetProfile",
    "ColumnProfile",
    # Tagger
    "TaggerEngine",
    "TaggingResult",
    "PIIReport",
    # Quality
    "QualityEngine",
    "QualityReport",
    # Search
    "SearchEngine",
    "SearchResponse",
    "SearchResult",
    # Dashboard
    "DashboardEngine",
    "DashboardLayout",
    "ChartRecommendation",
    "ChartType",
]
