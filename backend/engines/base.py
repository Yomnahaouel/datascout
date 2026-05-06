from abc import ABC, abstractmethod
from typing import Any


class BaseEngine(ABC):
    """Base class for all data-scouting engines."""

    @abstractmethod
    async def connect(self, connection_string: str) -> None:
        """Establish a connection to the data source."""

    @abstractmethod
    async def fetch(self, query: dict[str, Any] | None = None) -> list[dict]:
        """Fetch data from the source, optionally filtering by query."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up the connection."""
