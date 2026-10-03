from __future__ import annotations

from typing import Any

from backend.app.core.utils import clamp01

HEADLINES = {
    "true": "Most likely true",
    "mostly_true": "Probably true",
    "mixed": "Mixed evidence - sources disagree",
    "mostly_false": "Probably false",
    "false": "Most likely false",
}


def summarize_evidence(
    evidence: list[dict[str, Any]], sources: list[dict[str, Any]], *, llm_degraded: bool = False
) -> dict[str, Any]:
    """Turn extracted evidence into a short 'most likely answer' (no extra agents, no extra API calls).

    Each supporting/contradicting item is weighted by relevance x confidence x source quality.
    The returned dict matches the existing Verdict contract so the report page and DB need no changes.
    """
    if llm_degraded:
        return _verdict(
            "unverified", 0.0, 1.0, 0.0,
            "The AI evidence analysis was unavailable (API error or timeout), so sources are listed without a "
            "judgement. Check the server logs and your LLM API key, then run the investigation again.",
        )

    quality = {s["id"]: clamp01(s.get("quality_score"), 0.5) for s in sources}
    sup = con = 0.0
    n_sup = n_con = n_neu = 0
    for e in evidence:
        stance = e.get("stance")
        if stance == "neutral":
            n_neu += 1
            continue
        w = clamp01(e.get("relevance_score")) * clamp01(e.get("confidence")) * (0.5 + 0.5 * quality.get(e.get("source_id"), 0.5))
        if stance == "supporting":
            sup, n_sup = sup + w, n_sup + 1
        elif stance == "contradicting":
            con, n_con = con + w, n_con + 1

    if n_sup + n_con == 0:
        if not evidence:
            msg = "No relevant sources were found for this claim, so no answer can be given."
        else:
            msg = f"{len(evidence)} source(s) discuss the topic but none clearly confirm or dispute the claim."
        return _verdict("unverified", 0.1, 0.9, 0.0, msg)

    ratio = sup / (sup + con)
    label = (
        "true" if ratio >= 0.85 else "mostly_true" if ratio >= 0.65 else "mixed" if ratio >= 0.35
        else "mostly_false" if ratio >= 0.15 else "false"
    )
    decisiveness = abs(ratio - 0.5) * 2
    coverage = min(1.0, (n_sup + n_con) / 3)
    confidence = round(min(0.95, 0.6 * decisiveness + 0.4 * coverage), 2)
    explanation = (
        f"{HEADLINES[label]}. {n_sup} source(s) support the claim, {n_con} contradict it"
        + (f", and {n_neu} give only background." if n_neu else ".")
    )
    return _verdict(label, confidence, round(1 - confidence, 2), round(coverage, 2), explanation)


def _verdict(label: str, confidence: float, uncertainty: float, strength: float, explanation: str) -> dict[str, Any]:
    return {
        "label": label, "confidence": confidence, "uncertainty": uncertainty, "evidence_strength": strength,
        "review_required": confidence < 0.5 or label in ("mixed", "unverified"), "explanation": explanation,
    }
