from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.integrations.supabase_client import SupabaseClient
from backend.app.repos.base import BaseRepository

logger = get_logger(__name__)


class VerdictRepository(BaseRepository):
    """Repository for verdict records using Supabase."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient()

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new verdict record."""
        sql = """
            INSERT INTO verdicts (
                investigation_id, label, explanation, evidence_strength, uncertainty,
                review_required
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, investigation_id, label, explanation, evidence_strength,
                      uncertainty, review_required, created_at
        """
        params = [
            data.get("investigation_id"),
            data.get("label"),
            data.get("explanation"),
            data.get("evidence_strength", 0.5),
            data.get("uncertainty", 0.5),
            data.get("review_required", False),
        ]

        results = await self.client.query(sql, params)
        if results:
            logger.info(f"Verdict created: {results[0].get('id')}")
            return results[0]
        return data

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        """Retrieve a verdict by ID."""
        sql = """
            SELECT id, investigation_id, label, explanation, evidence_strength,
                   uncertainty, review_required, created_at
            FROM verdicts
            WHERE id = %s
        """
        results = await self.client.query(sql, [item_id])
        return results[0] if results else None

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        """List verdicts with optional filters."""
        sql = """
            SELECT id, investigation_id, label, explanation, evidence_strength,
                   uncertainty, review_required
            FROM verdicts
        """
        where_clauses = []
        params = []

        if "investigation_id" in filters:
            where_clauses.append("investigation_id = %s")
            params.append(filters["investigation_id"])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY created_at DESC"

        results = await self.client.query(sql, params)
        logger.info(f"Listed {len(results)} verdicts")
        return results
