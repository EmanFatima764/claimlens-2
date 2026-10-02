from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.integrations.supabase_client import SupabaseClient
from backend.app.repos.base import BaseRepository

logger = get_logger(__name__)


class EvidenceRepository(BaseRepository):
    """Repository for evidence records using Supabase."""

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self.client = client or SupabaseClient()

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new evidence record."""
        sql = """
            INSERT INTO evidence (
                investigation_id, claim_id, source_id, evidence_text, evidence_type,
                relevance_score, confidence
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, investigation_id, claim_id, source_id, evidence_text,
                      evidence_type, relevance_score, confidence, created_at
        """
        params = [
            data.get("investigation_id"),
            data.get("claim_id"),
            data.get("source_id"),
            data.get("evidence_text"),
            data.get("evidence_type"),
            data.get("relevance_score", 0.5),
            data.get("confidence", 0.5),
        ]

        results = await self.client.query(sql, params)
        if results:
            logger.info(f"Evidence created: {results[0].get('id')}")
            return results[0]
        return data

    async def get_by_id(self, item_id: str) -> dict[str, Any] | None:
        """Retrieve evidence by ID."""
        sql = """
            SELECT id, investigation_id, claim_id, source_id, evidence_text,
                   evidence_type, relevance_score, confidence
            FROM evidence
            WHERE id = %s
        """
        results = await self.client.query(sql, [item_id])
        return results[0] if results else None

    async def list(self, **filters: Any) -> list[dict[str, Any]]:
        """List evidence with optional filters."""
        sql = """
            SELECT id, investigation_id, claim_id, source_id, evidence_text,
                   evidence_type, relevance_score, confidence
            FROM evidence
        """
        where_clauses = []
        params = []

        if "investigation_id" in filters:
            where_clauses.append("investigation_id = %s")
            params.append(filters["investigation_id"])

        if "claim_id" in filters:
            where_clauses.append("claim_id = %s")
            params.append(filters["claim_id"])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY relevance_score DESC, created_at DESC"

        results = await self.client.query(sql, params)
        logger.info(f"Listed {len(results)} evidence records")
        return results
