from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.integrations.supabase_client import SupabaseClient
from backend.app.repos.base import BaseRepository

logger = get_logger(__name__)


class ClaimRepository(BaseRepository):
    """Repository for claim records using Supabase."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient()

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new claim record."""
        sql = """
            INSERT INTO claims (
                investigation_id, text, normalized_text, claim_type, entities, confidence
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, investigation_id, text, normalized_text, claim_type, entities,
                      confidence, created_at
        """
        params = [
            data.get("investigation_id"),
            data.get("text"),
            data.get("normalized_text"),
            data.get("claim_type"),
            data.get("entities"),
            data.get("confidence", 0.5),
        ]

        results = await self.client.query(sql, params)
        if results:
            logger.info(f"Claim created: {results[0].get('id')}")
            return results[0]
        return data

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        """Retrieve a claim by ID."""
        sql = """
            SELECT id, investigation_id, text, normalized_text, claim_type, entities,
                   confidence, created_at
            FROM claims
            WHERE id = %s
        """
        results = await self.client.query(sql, [item_id])
        return results[0] if results else None

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        """List claims with optional filters."""
        sql = "SELECT id, investigation_id, text, claim_type, confidence FROM claims"
        where_clauses = []
        params = []

        if "investigation_id" in filters:
            where_clauses.append("investigation_id = %s")
            params.append(filters["investigation_id"])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY created_at DESC"

        results = await self.client.query(sql, params)
        logger.info(f"Listed {len(results)} claims")
        return results
