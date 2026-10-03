from __future__ import annotations

import pytest

from backend.app.agents.conflict_agent.agent import ConflictAgent
from backend.app.agents.verdict_agent.agent import VerdictAgent
from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations.llm import LLMClient
from backend.app.repos import ConflictRepository, VerdictRepository

SOURCES = [
    {"id": "s1", "domain": "reuters.com", "url": "https://reuters.com/a", "quality_score": 0.85},
    {"id": "s2", "domain": "blog.example.com", "url": "https://blog.example.com/b", "quality_score": 0.5},
    {"id": "s3", "domain": "cdc.gov", "url": "https://cdc.gov/c", "quality_score": 0.88},
]
CLAIMS = [{"id": "c1", "text": "Claim one", "normalized_text": "Claim one."}]


def ev(i, stance, source="s1", claim="c1", rel=0.9, conf=0.9):
    return {"id": f"e{i}", "claim_id": claim, "source_id": source, "source_url": f"https://x/{i}",
            "evidence_text": f"evidence {i}", "stance": stance, "relevance_score": rel, "confidence": conf}


def state(evidence, claims=CLAIMS, conflicts=None, **extra):
    return {"investigation_id": "inv-1", "extracted_claims": claims, "evaluated_sources": SOURCES,
            "extracted_evidence": evidence, "detected_conflicts": conflicts or [], **extra}


def patch_llm(monkeypatch, result=None, error=False):
    async def fake(self, prompt, *, system=None, temperature=0.1):
        if error:
            raise ClaimLensError("down", code="llm_failed")
        return result

    monkeypatch.setattr(LLMClient, "generate_json", fake)


# ----------------------------------------------------------------------------- ConflictAgent
async def test_conflict_agent_detects_and_persists(monkeypatch):
    patch_llm(monkeypatch, {"pairs": [{"pair": 0, "is_conflict": True, "conflict_type": "temporal_discrepancy",
                                       "severity": 0.8, "explanation": "Dates differ."}]})
    out = await ConflictAgent().execute(state([ev(1, "supporting"), ev(2, "contradicting", "s2")]))
    [c] = out["detected_conflicts"]
    assert c["id"] and c["conflict_type"] == "temporal_discrepancy" and c["severity"] == 0.8
    assert {c["evidence_a_id"], c["evidence_b_id"]} == {"e1", "e2"}
    rows = await ConflictRepository().list(investigation_id="inv-1")
    assert len(rows) == 1 and rows[0]["explanation"] == "Dates differ."


async def test_conflict_agent_drops_pairs_the_llm_says_are_not_conflicts(monkeypatch):
    patch_llm(monkeypatch, {"pairs": [{"pair": 0, "is_conflict": False, "conflict_type": "scope_mismatch", "severity": 0.1}]})
    out = await ConflictAgent().execute(state([ev(1, "supporting"), ev(2, "contradicting", "s2")]))
    assert out["detected_conflicts"] == []


async def test_conflict_agent_sanitizes_llm_output(monkeypatch):
    patch_llm(monkeypatch, {"pairs": [
        {"pair": 0, "is_conflict": True, "conflict_type": "made-up", "severity": 9, "explanation": ""},
        {"pair": 42, "is_conflict": True},            # bad index ignored
        {"pair": 0, "is_conflict": True},             # duplicate index ignored
    ]})
    out = await ConflictAgent().execute(state([ev(1, "supporting"), ev(2, "contradicting", "s2")]))
    [c] = out["detected_conflicts"]
    assert c["conflict_type"] == "other" and c["severity"] == 1.0 and c["explanation"]


async def test_conflict_agent_falls_back_to_stance_conflict(monkeypatch):
    patch_llm(monkeypatch, error=True)
    out = await ConflictAgent().execute(state([ev(1, "supporting"), ev(2, "contradicting", "s2")]))
    [c] = out["detected_conflicts"]
    assert c["conflict_type"] == "stance_conflict" and "automatic" in c["explanation"]


async def test_conflict_agent_needs_both_sides(monkeypatch):
    patch_llm(monkeypatch, error=True)
    assert (await ConflictAgent().execute(state([ev(1, "supporting"), ev(2, "neutral")])))["detected_conflicts"] == []
    assert (await ConflictAgent().execute(state([ev(1, "supporting")], llm_degraded=True)))["detected_conflicts"] == []


async def test_conflict_agent_keeps_claims_separate(monkeypatch):
    patch_llm(monkeypatch, error=True)
    claims = [{"id": "c1", "text": "a"}, {"id": "c2", "text": "b"}]
    # support on c1, contradiction on c2 -> different claims, so no conflict
    out = await ConflictAgent().execute(state([ev(1, "supporting", claim="c1"), ev(2, "contradicting", claim="c2")], claims))
    assert out["detected_conflicts"] == []


# ----------------------------------------------------------------------------- VerdictAgent
async def test_verdict_clear_support_is_true_and_saved(monkeypatch):
    patch_llm(monkeypatch, {"label": "true", "explanation": "reuters.com and cdc.gov confirm it."})
    out = await VerdictAgent().execute(state([ev(1, "supporting"), ev(2, "supporting", "s3")]))
    v = out["final_verdict"]
    assert v["label"] == "true" and v["confidence"] > 0.7 and v["uncertainty"] < 0.3
    assert v["explanation"].startswith("reuters.com")
    [row] = await VerdictRepository().list(investigation_id="inv-1")
    assert row["label"] == "true"


async def test_verdict_rejects_llm_jump_of_more_than_one_step(monkeypatch):
    patch_llm(monkeypatch, {"label": "false", "explanation": "nope"})
    out = await VerdictAgent().execute(state([ev(1, "supporting"), ev(2, "supporting", "s3")]))
    assert out["final_verdict"]["label"] == "true"       # baseline kept


async def test_verdict_allows_one_step_nudge_but_lowers_confidence(monkeypatch):
    evidence = [ev(1, "supporting"), ev(2, "supporting", "s3")]
    patch_llm(monkeypatch, {"label": "true", "explanation": "x"})
    base = (await VerdictAgent().execute(state(evidence)))["final_verdict"]
    patch_llm(monkeypatch, {"label": "mostly_true", "explanation": "x"})
    nudged = (await VerdictAgent().execute(state(evidence)))["final_verdict"]
    assert nudged["label"] == "mostly_true" and nudged["confidence"] < base["confidence"]


async def test_verdict_llm_failure_uses_computed_baseline(monkeypatch):
    patch_llm(monkeypatch, error=True)
    v = (await VerdictAgent().execute(state([ev(1, "contradicting"), ev(2, "contradicting", "s3")])))["final_verdict"]
    assert v["label"] == "false" and "contradict" in v["explanation"]


async def test_verdict_split_evidence_is_mixed_and_flagged(monkeypatch):
    patch_llm(monkeypatch, error=True)
    v = (await VerdictAgent().execute(state([ev(1, "supporting"), ev(2, "contradicting", "s3")])))["final_verdict"]
    assert v["label"] == "mixed" and v["review_required"]


async def test_verdict_conflicts_lower_confidence_and_force_review(monkeypatch):
    patch_llm(monkeypatch, error=True)
    evidence = [ev(1, "supporting"), ev(2, "supporting", "s3"), ev(3, "contradicting", "s2", rel=0.1, conf=0.1)]
    clean = (await VerdictAgent().execute(state(evidence)))["final_verdict"]
    conflicted = (await VerdictAgent().execute(state(evidence, conflicts=[{"severity": 0.9}, {"severity": 0.8}])))["final_verdict"]
    assert conflicted["confidence"] < clean["confidence"] and conflicted["uncertainty"] > clean["uncertainty"]
    assert conflicted["review_required"]


async def test_verdict_one_false_claim_drags_multi_claim_text_to_mixed(monkeypatch):
    patch_llm(monkeypatch, error=True)
    claims = [{"id": "c1", "text": "a"}, {"id": "c2", "text": "b"}]
    evidence = [ev(1, "supporting", claim="c1"), ev(2, "supporting", "s3", claim="c1"),
                ev(3, "contradicting", claim="c2"), ev(4, "contradicting", "s3", claim="c2")]
    assert (await VerdictAgent().execute(state(evidence, claims)))["final_verdict"]["label"] == "mixed"


async def test_verdict_unverified_without_decisive_evidence(monkeypatch):
    patch_llm(monkeypatch, error=True)
    for evidence in ([], [ev(1, "neutral")]):
        v = (await VerdictAgent().execute(state(evidence)))["final_verdict"]
        assert v["label"] == "unverified" and v["review_required"]


async def test_verdict_reports_degraded_llm_honestly(monkeypatch):
    patch_llm(monkeypatch, error=True)
    v = (await VerdictAgent().execute(state([ev(1, "neutral")], llm_degraded=True)))["final_verdict"]
    assert v["label"] == "unverified" and "unavailable" in v["explanation"]
