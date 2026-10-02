from __future__ import annotations

from typing import Any

from backend.app.repos.base import BaseRepository


class EvidenceRepository(BaseRepository):
    """Repository placeholder for evidence records."""

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"id": "evidence_placeholder", **data}

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        return {"id": item_id, "status": "not_implemented"}

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        return []
