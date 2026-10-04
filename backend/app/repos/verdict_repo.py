from __future__ import annotations

from typing import Any

from backend.app.repos.base import BaseRepository


class VerdictRepository(BaseRepository):
    table = "verdicts"

    async def save_for_investigation(self, data: dict[str, Any]) -> dict[str, Any]:
        """One verdict per investigation (UNIQUE constraint) - insert or overwrite."""
        return await self.client.upsert(
            self.table, {k: v for k, v in data.items() if v is not None}, on_conflict="investigation_id"
        )
