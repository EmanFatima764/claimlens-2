from __future__ import annotations

from typing import Any

from backend.app.repos.base import BaseRepository


class InvestigationRepository(BaseRepository):
    table = "investigations"

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        filters.setdefault("_limit", 100)
        return await super().list(**filters)
