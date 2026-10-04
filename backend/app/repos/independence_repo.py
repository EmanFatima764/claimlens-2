from __future__ import annotations

import json
from typing import Any

from backend.app.repos.base import BaseRepository


class IndependenceRepository(BaseRepository):
    table = "independence_analysis"

    async def save_for_investigation(
        self, investigation_id: str, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """One independence_analysis row per investigation (upsert)."""
        return await self.client.upsert(
            self.table,
            {
                "investigation_id": investigation_id,
                "independent_source_count": analysis.get("independent_source_count", 0),
                "total_source_count": analysis.get("total_source_count", 0),
                "independence_ratio": analysis.get("independence_ratio", 0.0),
                "source_groups": json.dumps(analysis.get("source_groups") or []),
                "relationships": json.dumps(analysis.get("relationships") or []),
                "overall_independence": analysis.get("overall_independence", "unknown"),
                "explanation": analysis.get("explanation", ""),
                "llm_fallback": analysis.get("llm_fallback", False),
            },
            on_conflict="investigation_id",
        )

    async def get_for_investigation(self, investigation_id: str) -> dict[str, Any] | None:
        rows = await self.list(investigation_id=investigation_id)
        if not rows:
            return None
        row = rows[0]
        # Parse JSON string columns back to lists when coming from Supabase
        for key in ("source_groups", "relationships"):
            val = row.get(key)
            if isinstance(val, str):
                try:
                    row[key] = json.loads(val)
                except (ValueError, TypeError):
                    row[key] = []
        return row
