from __future__ import annotations

from abc import ABC
from typing import Any


class BaseRepository(ABC):
    """Low-level persistence interface for repositories.

    Actual database implementation is intentionally deferred.
    """

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        raise NotImplementedError
