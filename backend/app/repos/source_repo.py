from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.integrations.supabase_client import SupabaseClient
from backend.app.repos.base import BaseRepository

logger = get_logger(__name__)


class SourceRepository(BaseRepository):
    """Repository for source records using Supabase."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient()

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new source record."""
        sql = """
            INSERT INTO sources (
                investigation_id, title, url, publisher, source_type, quality_score
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, investigation_id, title, url, publisher, source_type,
                      quality_score, created_at
        """
        params = [
            data.get("investigation_id"),
            data.get("title"),
            data.get("url"),
            data.get("publisher"),
            data.get("source_type"),
            data.get("quality_score", 0.5),
        ]

        results = await self.client.query(sql, params)
        if results:
            logger.info(f"Source created: {results[0].get('id')}")
            return results[0]
        return data

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        """Retrieve a source by ID."""
        sql = """
            SELECT id, investigation_id, title, url, publisher, source_type, quality_score
            FROM sources
            WHERE id = %s
        """
        results = await self.client.query(sql, [item_id])
        return results[0] if results else None

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        """List sources with optional filters."""
        sql = "SELECT id, investigation_id, title, url, source_type, quality_score FROM sources"
        where_clauses = []
        params = []

        if "investigation_id" in filters:
            where_clauses.append("investigation_id = %s")
            params.append(filters["investigation_id"])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY quality_score DESC, created_at DESC"

        results = await self.client.query(sql, params)
        logger.info(f"Listed {len(results)} sources")
        return results
