from __future__ import annotations

import json
from typing import Any

from backend.app.repos.base import BaseRepository


class VerificationRepository(BaseRepository):
    table = "verified_claims"

    async def save_for_investigation(
        self, investigation_id: str, verified_claims: list[dict[str, Any]]
    ) -> None:
        """Delete previous results then insert fresh ones (one row per claim)."""
        await self.delete_by_investigation(investigation_id)
        for vc in verified_claims:
            await self.create({
                "investigation_id": investigation_id,
                "claim_id": vc.get("claim_id"),
                "verification_status": vc.get("verification_status", "insufficient_evidence"),
                "confidence": vc.get("confidence", 0.5),
                "supporting_evidence": json.dumps(vc.get("supporting_evidence") or []),
                "contradicting_evidence": json.dumps(vc.get("contradicting_evidence") or []),
                "reasoning": vc.get("reasoning", ""),
                "unresolved_issues": json.dumps(vc.get("unresolved_issues") or []),
                "llm_fallback": vc.get("llm_fallback", False),
            })

    async def list_for_investigation(self, investigation_id: str) -> list[dict[str, Any]]:
        rows = await self.list(investigation_id=investigation_id)
        # Parse JSON string columns back to lists when coming from Supabase
        for row in rows:
            for key in ("supporting_evidence", "contradicting_evidence", "unresolved_issues"):
                val = row.get(key)
                if isinstance(val, str):
                    try:
                        row[key] = json.loads(val)
                    except (ValueError, TypeError):
                        row[key] = []
        return rows
