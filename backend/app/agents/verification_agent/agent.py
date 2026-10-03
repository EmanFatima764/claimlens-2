from __future__ import annotations

from typing import Any

from backend.app.agents.base import BaseAgent


class VerificationAgent(BaseAgent):
    """PLACEHOLDER - owned by teammate (agents 5-8).

    Contract: read `extracted_claims` + `extracted_evidence`, return {"verified_claims": [...]}.
    This stub only counts stances per claim so the pipeline runs end to end.
    """

    name = "verification_agent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        verified = []
        for claim in state.get("extracted_claims", []):
            ev = [e for e in state.get("extracted_evidence", []) if e.get("claim_id") == claim["id"]]
            verified.append(
                {
                    "claim_id": claim["id"],
                    "supporting": sum(e["stance"] == "supporting" for e in ev),
                    "contradicting": sum(e["stance"] == "contradicting" for e in ev),
                    "neutral": sum(e["stance"] == "neutral" for e in ev),
                }
            )
        return {"verified_claims": verified}
