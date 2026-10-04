from __future__ import annotations

from typing import Any

from backend.app.integrations.supabase_client import SupabaseClient


class BaseRepository:
    """Generic table repository over the Supabase client. Subclasses just set `table`."""

    table: str = ""
    order_by: str | None = "created_at"
    order_desc: bool = True

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient()

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self.client.insert(self.table, {k: v for k, v in data.items() if v is not None})

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        rows = await self.client.select(self.table, filters={"id": item_id}, limit=1)
        return rows[0] if rows else None

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        limit = filters.pop("_limit", None)
        return await self.client.select(
            self.table, filters=filters or None, order=self.order_by, desc=self.order_desc, limit=limit
        )

    async def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        rows = await self.client.update(self.table, {"id": item_id}, data)
        return rows[0] if rows else None

    async def delete_by_investigation(self, investigation_id: str) -> None:
        await self.client.delete(self.table, {"investigation_id": investigation_id})
