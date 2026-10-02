from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.integrations.supabase_client import SupabaseClient
from backend.app.repos.base import BaseRepository

logger = get_logger(__name__)


class InvestigationRepository(BaseRepository):
    """Repository for investigation records using Supabase."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient()

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new investigation record.

        Args:
            data: Investigation data (title, description, input_text, etc.)

        Returns:
            Created investigation record with ID
        """
        sql = """
            INSERT INTO investigations (
                title, description, input_text, source_type, status
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id, title, description, input_text, source_type, status,
                      created_at, updated_at
        """
        params = [
            data.get("title"),
            data.get("description"),
            data.get("input_text"),
            data.get("source_type", "text"),
            data.get("status", "draft"),
        ]

        results = await self.client.query(sql, params)
        if results:
            logger.info(f"Investigation created: {results[0].get('id')}")
            return results[0]
        return data

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        """Retrieve an investigation by ID.

        Args:
            item_id: Investigation ID

        Returns:
            Investigation record or None if not found
        """
        sql = """
            SELECT id, title, description, input_text, source_type, status,
                   workflow_status, final_verdict, created_at, updated_at
            FROM investigations
            WHERE id = %s
        """
        results = await self.client.query(sql, [item_id])
        if results:
            logger.info(f"Investigation retrieved: {item_id}")
            return results[0]
        return None

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        """List investigations with optional filters.

        Args:
            **filters: Filter criteria (status, source_type, etc.)

        Returns:
            List of investigation records
        """
        sql = "SELECT id, title, description, source_type, status, created_at FROM investigations"
        where_clauses = []
        params = []

        if "status" in filters:
            where_clauses.append("status = %s")
            params.append(filters["status"])

        if "source_type" in filters:
            where_clauses.append("source_type = %s")
            params.append(filters["source_type"])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY created_at DESC LIMIT 100"

        results = await self.client.query(sql, params)
        logger.info(f"Listed {len(results)} investigations")
        return results

    async def update(self, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update an investigation record.

        Args:
            item_id: Investigation ID
            data: Fields to update

        Returns:
            Updated investigation record or None if not found
        """
        set_clauses = []
        params = []

        for key, value in data.items():
            if key not in ["id", "created_at"]:
                set_clauses.append(f"{key} = %s")
                params.append(value)

        params.append(item_id)

        sql = f"""
            UPDATE investigations
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s
            RETURNING id, title, description, input_text, source_type, status,
                      workflow_status, final_verdict, created_at, updated_at
        """

        results = await self.client.query(sql, params)
        if results:
            logger.info(f"Investigation updated: {item_id}")
            return results[0]
        return None
