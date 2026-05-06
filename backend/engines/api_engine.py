from typing import Any
import httpx

from engines.base import BaseEngine


class ApiEngine(BaseEngine):
    """Engine for fetching data from REST APIs."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._base_url: str = ""

    async def connect(self, connection_string: str) -> None:
        self._base_url = connection_string
        self._client = httpx.AsyncClient(base_url=self._base_url)

    async def fetch(self, query: dict[str, Any] | None = None) -> list[dict]:
        if self._client is None:
            raise RuntimeError("Engine not connected. Call connect() first.")
        params = query or {}
        response = await self._client.get("/", params=params)
        response.raise_for_status()
        result = response.json()
        return result if isinstance(result, list) else [result]

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
