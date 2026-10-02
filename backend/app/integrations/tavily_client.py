from __future__ import annotations

from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError


class TavilyClient:
    """Wrapper for the Tavily search API.

    This is intentionally not a real implementation yet. It provides a single seam for future agent research calls.
    """

    def __init__(self) -> None:
        self.api_key = settings.tavily_api_key

    async def search(self, query: str, *, max_results: int = 5) -> dict[str, Any]:
        if not self.api_key:
            raise ClaimLensError("Tavily API key is not configured", code="tavily_missing_key")
        return {
            "query": query,
            "results": [],
            "max_results": max_results,
            "status": "not_implemented",
        }
