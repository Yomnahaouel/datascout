"""
DataScout Pipeline Module - Data ingestion and processing orchestration.
"""

from pipeline.ingestion import IngestionPipeline, IngestionResult, run_ingestion_background

__all__ = [
    "IngestionPipeline",
    "IngestionResult",
    "run_ingestion_background",
]
