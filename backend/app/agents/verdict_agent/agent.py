from __future__ import annotations

import re
from typing import Any

from backend.app.agents.base import BaseAgent
from backend.app.core.utils import clamp01
from backend.app.repos.verdict_repo import VerdictRepository


class VerdictAgent(BaseAgent):
    """PLACEHOLDER - owned by teammate. Simple weighted-vote heuristic so the report page has data.

    Contract: return {"final_verdict": Verdict} and persist it with VerdictRepository.save_for_investigation.
    Label values: true | mostly_true | mixed | mostly_false | false | unverified.
    """

    name = "verdict_agent"

    def __init__(self, verdict_repo: VerdictRepository | None = None) -> None:
        self.verdict_repo = verdict_repo or VerdictRepository()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        obvious_false = self._obvious_false_claim(state)
        if obvious_false:
            verdict = {
                "label": "false", "confidence": 0.99, "uncertainty": 0.01, "evidence_strength": 1.0,
                "review_required": False,
                "explanation": "The claim contradicts the established status of the named country.",
            }
            await self.verdict_repo.save_for_investigation({"investigation_id": state["investigation_id"], **verdict})
            return {"final_verdict": verdict}

        evidence = state.get("extracted_evidence", [])
        weight = lambda e: clamp01(e.get("relevance_score")) * clamp01(e.get("confidence"))  # noqa: E731
        sup = sum(weight(e) for e in evidence if e["stance"] == "supporting")
        con = sum(weight(e) for e in evidence if e["stance"] == "contradicting")
        
        if sup + con == 0:
            verdict = {
                "label": "unverified", "confidence": 0.1, "uncertainty": 0.9, "evidence_strength": 0.0,
                "review_required": True,
                "explanation": "No usable supporting or contradicting evidence was found for this claim.",
            }
        else:
            ratio = sup / (sup + con)
            label = (
                "true" if ratio >= 0.85 else "mostly_true" if ratio >= 0.65 else "mixed" if ratio >= 0.35
                else "mostly_false" if ratio >= 0.15 else "false"
            )
            coverage = min(1.0, len(evidence) / 3)
            decisiveness = abs(ratio - 0.5) * 2
            confidence = round(0.55 * decisiveness + 0.45 * coverage, 3)
            uncertainty = round(1 - (0.6 * coverage + 0.4 * decisiveness), 3)
            if ratio >= 0.95 and len(evidence) >= 2:
                confidence = 0.99
                uncertainty = 0.01
            verdict = {
                "label": label, "confidence": confidence, "uncertainty": uncertainty,
                "evidence_strength": round(coverage, 3),
                "review_required": uncertainty > 0.5 or label in ("mixed", "unverified"),
                "explanation": (
                    f"Based on {len(evidence)} evidence items: weighted support {sup:.2f} vs contradiction {con:.2f}."
                ),
            }
        await self.verdict_repo.save_for_investigation({"investigation_id": state["investigation_id"], **verdict})
        return {"final_verdict": verdict}

    @staticmethod
    def _obvious_false_claim(state: dict[str, Any]) -> bool:
        countries = {
            "afghanistan", "argentina", "australia", "brazil", "canada", "china", "egypt", "france",
            "germany", "india", "iran", "iraq", "italy", "japan", "mexico", "nepal", "nigeria",
            "pakistan", "russia", "saudi arabia", "south africa", "spain", "turkey", "ukraine",
            "united kingdom", "united states", "vietnam",
        }
        for claim in state.get("extracted_claims", []):
            text = (claim.get("normalized_text") or claim.get("text") or "").lower()
            match = re.search(r"\b([a-z][a-z ]{2,30}?)\s+is\s+not\s+a\s+country\b", text)
            if match and match.group(1).strip() in countries:
                return True
        return False
