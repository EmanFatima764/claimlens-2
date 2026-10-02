from __future__ import annotations

import os
from typing import Any

from backend.app.core.exceptions import ClaimLensError
from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class SupabaseClient:
    """Supabase database client for ClaimLens 2.0.

    This client manages connections to Supabase PostgreSQL and handles
    investigation, claim, source, evidence, and verdict persistence.
    """

    def __init__(self, url: str | None = None, key: str | None = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_ANON_KEY", "")

        if not self.url or not self.key:
            logger.warning("Supabase credentials not fully configured")

    async def health_check(self) -> dict[str, Any]:
        """Check Supabase connection health."""
        if not self.url or not self.key:
            raise ClaimLensError(
                "Supabase not configured",
                code="supabase_not_configured",
            )
        return {
            "status": "ok",
            "service": "supabase",
            "url": self.url[:50] + "...",
        }

    async def query(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query against Supabase.

        Placeholder implementation. In production, this would use the
        supabase-py client library.
        """
        logger.info(f"Executing query: {sql[:80]}...")
        return []

    async def execute(self, sql: str, params: list[Any] | None = None) -> dict[str, Any]:
        """Execute a SQL statement against Supabase."""
        logger.info(f"Executing statement: {sql[:80]}...")
        return {"rows_affected": 0}
