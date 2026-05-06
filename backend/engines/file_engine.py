from typing import Any
import csv
import io
from pathlib import Path

from engines.base import BaseEngine


class FileEngine(BaseEngine):
    """Engine for reading data from local CSV files."""

    def __init__(self) -> None:
        self._file_path: Path | None = None

    async def connect(self, connection_string: str) -> None:
        self._file_path = Path(connection_string)
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {connection_string}")

    async def fetch(self, query: dict[str, Any] | None = None) -> list[dict]:
        if self._file_path is None:
            raise RuntimeError("Engine not connected. Call connect() first.")
        with open(self._file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    async def disconnect(self) -> None:
        self._file_path = None
