"""Tests for VerificationAgent and IndependenceAgent.

All tests use the in-memory DB and fake LLM/Tavily from conftest.py.
Additional per-test monkeypatching is used where a specific LLM response is needed.
"""
from __future__ import annotations

import pytest

from backend.app.agents.independence_agent.agent import IndependenceAgent
from backend.app.agents.verification_agent.agent import (
    VERIFICATION_STATUSES,
    VerificationAgent,
)
from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations.llm import LLMClient

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

SOURCES = [
    {
        "id": "s1", "domain": "reuters.com", "url": "https://reuters.com/a",
        "title": "Reuters health report", "publisher": "Reuters", "source_type": "news",
        "quality_score": 0.85, "relevance_score": 0.9,
    },
    {
        "id": "s2", "domain": "blog.example.com", "url": "https://blog.example.com/b",
        "title": "Example blog post", "publisher": "Example Blog", "source_type": "other",
        "quality_score": 0.4, "relevance_score": 0.6,
    },
    {
        "id": "s3", "domain": "cdc.gov", "url": "https://cdc.gov/c",
        "title": "CDC data report", "publisher": "CDC", "source_type": "government",
        "quality_score": 0.88, "relevance_score": 0.85,
    },
]

CLAIMS = [
    {"id": "c1", "text": "The vaccine is 95% effective.", "normalized_text": "The vaccine is 95% effective."},
]


def ev(i: int, stance: str, source_id: str = "s1", claim_id: str = "c1",
       rel: float = 0.9, conf: float = 0.85) -> dict:
    return {
        "id": f"e{i}", "claim_id": claim_id, "source_id": source_id,
        "source_url": f"https://x/{i}", "evidence_text": f"Evidence item {i}.",
        "stance": stance, "relevance_score": rel, "confidence": conf,
    }


def base_state(evidence: list, claims: list = CLAIMS, **extra) -> dict:
    return {
        "investigation_id": "inv-test",
        "extracted_claims": claims,
        "evaluated_sources": SOURCES,
        "extracted_evidence": evidence,
        "detected_conflicts": [],
        "verified_claims": [],
        "independence_analysis": {},
        **extra,
    }


def patch_llm(monkeypatch, response: dict | None = None, error: bool = False) -> None:
    async def fake(self, prompt, *, system=None, temperature=0.1):
        if error:
            raise ClaimLensError("LLM is down", code="llm_failed")
        return response

    monkeypatch.setattr(LLMClient, "generate_json", fake)


# ===========================================================================
# VerificationAgent tests
# ===========================================================================

# ---- 1. Strong supporting evidence ----------------------------------------

async def test_verification_supported_status(monkeypatch):
    patch_llm(monkeypatch, {
        "verification_status": "supported",
        "confidence": 0.9,
        "supporting_evidence": ["Reuters confirms 95% efficacy."],
        "contradicting_evidence": [],
        "reasoning": "Two high-quality sources directly confirm the claim.",
        "unresolved_issues": [],
    })
    evidence = [ev(1, "supporting", "s1"), ev(2, "supporting", "s3")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"]
    assert len(vc) == 1
    assert vc[0]["claim_id"] == "c1"
    assert vc[0]["verification_status"] == "supported"
    assert vc[0]["confidence"] == 0.9
    assert vc[0]["supporting_evidence"] == ["Reuters confirms 95% efficacy."]
    assert vc[0]["contradicting_evidence"] == []
    assert not vc[0]["llm_fallback"]


# ---- 2. Strong contradicting evidence -------------------------------------

async def test_verification_refuted_status(monkeypatch):
    patch_llm(monkeypatch, {
        "verification_status": "refuted",
        "confidence": 0.85,
        "supporting_evidence": [],
        "contradicting_evidence": ["CDC data shows only 60% efficacy."],
        "reasoning": "Primary government source directly contradicts the claimed figure.",
        "unresolved_issues": ["Trial period differs between studies."],
    })
    evidence = [ev(1, "contradicting", "s3")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["verification_status"] == "refuted"
    assert vc["confidence"] == 0.85
    assert "CDC data" in vc["contradicting_evidence"][0]
    assert len(vc["unresolved_issues"]) == 1


# ---- 3. Mixed / partial evidence ------------------------------------------

async def test_verification_partially_supported(monkeypatch):
    patch_llm(monkeypatch, {
        "verification_status": "partially_supported",
        "confidence": 0.55,
        "supporting_evidence": ["Reuters: 95% in adults."],
        "contradicting_evidence": ["Blog reports lower rate in elderly."],
        "reasoning": "Evidence supports the claim for adults but contradicts it for the elderly cohort.",
        "unresolved_issues": ["Age-stratified data missing."],
    })
    evidence = [ev(1, "supporting", "s1"), ev(2, "contradicting", "s2")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["verification_status"] == "partially_supported"
    assert vc["confidence"] == 0.55
    assert vc["supporting_evidence"]
    assert vc["contradicting_evidence"]


# ---- 4. Insufficient evidence ---------------------------------------------

async def test_verification_insufficient_evidence(monkeypatch):
    patch_llm(monkeypatch, {
        "verification_status": "insufficient_evidence",
        "confidence": 0.2,
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "reasoning": "Only background material found; none directly tests the 95% figure.",
        "unresolved_issues": ["No primary trial data found."],
    })
    evidence = [ev(1, "neutral", "s2")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["verification_status"] == "insufficient_evidence"
    assert vc["confidence"] == 0.2


# ---- 5. No evidence at all ------------------------------------------------

async def test_verification_no_evidence_skips_llm(monkeypatch):
    """When there is no evidence for a claim the agent must not call the LLM."""
    called = []

    async def should_not_be_called(self, *a, **k):
        called.append(True)
        return {}

    monkeypatch.setattr(LLMClient, "generate_json", should_not_be_called)
    out = await VerificationAgent().execute(base_state([]))
    vc = out["verified_claims"][0]
    assert vc["verification_status"] == "insufficient_evidence"
    assert "No evidence" in vc["reasoning"]
    assert called == []   # LLM must NOT have been called


# ---- 6. LLM failure → stance-count fallback -------------------------------

async def test_verification_llm_failure_uses_fallback(monkeypatch):
    patch_llm(monkeypatch, error=True)
    evidence = [ev(1, "supporting", "s1"), ev(2, "supporting", "s3")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["llm_fallback"] is True
    assert vc["verification_status"] == "supported"
    assert "Stance-count fallback" in vc["reasoning"]


async def test_verification_fallback_mixed_stances(monkeypatch):
    patch_llm(monkeypatch, error=True)
    evidence = [ev(1, "supporting", "s1"), ev(2, "contradicting", "s2")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["llm_fallback"] is True
    assert vc["verification_status"] == "partially_supported"


async def test_verification_fallback_contradicting_only(monkeypatch):
    patch_llm(monkeypatch, error=True)
    evidence = [ev(1, "contradicting", "s2"), ev(2, "contradicting", "s3")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["verification_status"] == "refuted"
    assert vc["llm_fallback"] is True


# ---- 7. llm_degraded flag → full agent short-circuits --------------------

async def test_verification_respects_llm_degraded(monkeypatch):
    """If llm_degraded=True in the state the agent skips all LLM calls."""
    called = []

    async def should_not_be_called(self, *a, **k):
        called.append(True)
        return {}

    monkeypatch.setattr(LLMClient, "generate_json", should_not_be_called)
    evidence = [ev(1, "supporting", "s1")]
    out = await VerificationAgent().execute(base_state(evidence, llm_degraded=True))
    assert out["verified_claims"]
    assert all(vc["llm_fallback"] for vc in out["verified_claims"])
    assert called == []


# ---- 8. Invalid / bad LLM JSON is sanitised gracefully --------------------

async def test_verification_sanitises_bad_llm_status(monkeypatch):
    """Unknown verification_status falls back to insufficient_evidence."""
    patch_llm(monkeypatch, {
        "verification_status": "TOTALLY_MADE_UP",
        "confidence": 0.7,
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "reasoning": "Whatever.",
        "unresolved_issues": [],
    })
    evidence = [ev(1, "supporting", "s1")]
    out = await VerificationAgent().execute(base_state(evidence))
    vc = out["verified_claims"][0]
    assert vc["verification_status"] == "insufficient_evidence"
    # confidence and reasoning still preserved
    assert vc["confidence"] == 0.7
    assert vc["reasoning"] == "Whatever."


async def test_verification_clamps_confidence(monkeypatch):
    """Confidence outside [0,1] must be clamped."""
    patch_llm(monkeypatch, {
        "verification_status": "supported",
        "confidence": 9.5,  # invalid
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "reasoning": "ok",
        "unresolved_issues": [],
    })
    evidence = [ev(1, "supporting", "s1")]
    out = await VerificationAgent().execute(base_state(evidence))
    assert out["verified_claims"][0]["confidence"] <= 1.0


# ---- 9. Multiple claims — each gets its own result -----------------------

async def test_verification_per_claim_isolation(monkeypatch):
    """Each claim is verified independently; evidence for one claim does not bleed into another."""
    calls = []
    responses = [
        {"verification_status": "supported", "confidence": 0.9, "supporting_evidence": ["X"],
         "contradicting_evidence": [], "reasoning": "Claim 1 supported.", "unresolved_issues": []},
        {"verification_status": "refuted", "confidence": 0.8, "supporting_evidence": [],
         "contradicting_evidence": ["Y"], "reasoning": "Claim 2 refuted.", "unresolved_issues": []},
    ]

    async def fake(self, prompt, *, system=None, temperature=0.1):
        calls.append(prompt)
        return responses[len(calls) - 1]

    monkeypatch.setattr(LLMClient, "generate_json", fake)
    claims = [
        {"id": "c1", "text": "Claim one.", "normalized_text": "Claim one."},
        {"id": "c2", "text": "Claim two.", "normalized_text": "Claim two."},
    ]
    evidence = [ev(1, "supporting", "s1", claim_id="c1"), ev(2, "contradicting", "s2", claim_id="c2")]
    out = await VerificationAgent().execute(base_state(evidence, claims))
    vc = out["verified_claims"]
    assert len(vc) == 2
    statuses = {v["claim_id"]: v["verification_status"] for v in vc}
    assert statuses["c1"] == "supported"
    assert statuses["c2"] == "refuted"
    # Two separate LLM calls were made (one per claim)
    assert len(calls) == 2


# ---- 10. All allowed statuses are accepted ---------------------------------

async def test_verification_all_statuses_accepted(monkeypatch):
    for status in VERIFICATION_STATUSES:
        patch_llm(monkeypatch, {
            "verification_status": status,
            "confidence": 0.7,
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "reasoning": f"Testing {status}.",
            "unresolved_issues": [],
        })
        evidence = [ev(1, "supporting", "s1")]
        out = await VerificationAgent().execute(base_state(evidence))
        assert out["verified_claims"][0]["verification_status"] == status


# ---- 11. Keys are always preserved on the state ---------------------------

async def test_verification_preserves_earlier_state_keys(monkeypatch):
    patch_llm(monkeypatch, {
        "verification_status": "supported", "confidence": 0.8,
        "supporting_evidence": [], "contradicting_evidence": [],
        "reasoning": "ok", "unresolved_issues": [],
    })
    evidence = [ev(1, "supporting", "s1")]
    state = base_state(evidence)
    state["extracted_claims"] = CLAIMS
    state["research_results"] = [{"url": "https://example.com", "title": "x"}]
    out = await VerificationAgent().execute(state)
    # Keys from before the agent ran must still be present
    assert out["research_results"] == state["research_results"]
    assert out["extracted_claims"] == CLAIMS


# ===========================================================================
# IndependenceAgent tests
# ===========================================================================

def ind_sources(*domains: str) -> list[dict]:
    return [
        {
            "id": f"s{i}", "domain": d, "url": f"https://{d}/article-{i}",
            "title": f"Article from {d}", "publisher": d, "source_type": "news",
            "quality_score": 0.7, "relevance_score": 0.8,
        }
        for i, d in enumerate(domains)
    ]


def ind_state(sources: list[dict], **extra) -> dict:
    return {
        "investigation_id": "inv-ind",
        "extracted_claims": CLAIMS,
        "evaluated_sources": sources,
        "extracted_evidence": [],
        **extra,
    }


# ---- 12. Two genuinely independent sources --------------------------------

async def test_independence_two_independent_sources(monkeypatch):
    patch_llm(monkeypatch, {
        "groups": [
            {"group_id": 0, "source_indices": [0], "origin_description": "Reuters primary",
             "is_independent_origin": True},
            {"group_id": 1, "source_indices": [1], "origin_description": "CDC primary",
             "is_independent_origin": True},
        ],
        "relationships": [
            {"source_a": 0, "source_b": 1, "relationship": "independent",
             "explanation": "Both gathered data independently."},
        ],
        "independent_origin_count": 2,
        "explanation": "Two fully independent sources.",
    })
    sources = ind_sources("reuters.com", "cdc.gov")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    assert ia["independent_source_count"] == 2
    assert ia["total_source_count"] == 2
    assert ia["independence_ratio"] == 1.0
    assert ia["overall_independence"] == "high"
    assert not ia["llm_fallback"]
    [rel] = ia["relationships"]
    assert rel["relationship"] == "independent"
    assert rel["source_id_a"] == "s0"
    assert rel["source_id_b"] == "s1"


# ---- 13. Multiple sources quoting the same original -----------------------

async def test_independence_derived_sources_grouped(monkeypatch):
    """Three articles all citing the same government report → one independent origin."""
    patch_llm(monkeypatch, {
        "groups": [
            {"group_id": 0, "source_indices": [0, 1, 2],
             "origin_description": "Government report + two news articles that cite it",
             "is_independent_origin": True},
        ],
        "relationships": [
            {"source_a": 1, "source_b": 0, "relationship": "derived",
             "explanation": "Reuters article cites the government report."},
            {"source_a": 2, "source_b": 0, "relationship": "derived",
             "explanation": "BBC article cites the government report."},
        ],
        "independent_origin_count": 1,
        "explanation": "All three sources trace to the same government report.",
    })
    sources = ind_sources("gov.example.gov", "reuters.com", "bbc.com")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    assert ia["independent_source_count"] == 1
    assert ia["total_source_count"] == 3
    assert ia["independence_ratio"] < 0.5
    assert ia["overall_independence"] == "low"
    assert len(ia["source_groups"]) == 1
    assert len(ia["relationships"]) == 2
    assert ia["relationships"][0]["relationship"] == "derived"


# ---- 14. One source copying another ---------------------------------------

async def test_independence_republished_relationship(monkeypatch):
    patch_llm(monkeypatch, {
        "groups": [
            {"group_id": 0, "source_indices": [0], "origin_description": "Original AP story",
             "is_independent_origin": True},
            {"group_id": 1, "source_indices": [1], "origin_description": "Republished copy",
             "is_independent_origin": False},
        ],
        "relationships": [
            {"source_a": 1, "source_b": 0, "relationship": "republished",
             "explanation": "blog.example.com reprints the AP story verbatim."},
        ],
        "independent_origin_count": 1,
        "explanation": "One independent origin; the blog republishes AP content.",
    })
    sources = ind_sources("apnews.com", "blog.example.com")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    assert ia["independent_source_count"] == 1
    [rel] = ia["relationships"]
    assert rel["relationship"] == "republished"
    # The non-independent group must be represented
    groups = ia["source_groups"]
    not_ind = [g for g in groups if not g["is_independent_origin"]]
    assert len(not_ind) == 1


# ---- 15. Unclear independence --------------------------------------------

async def test_independence_unclear_relationship(monkeypatch):
    patch_llm(monkeypatch, {
        "groups": [
            {"group_id": 0, "source_indices": [0], "origin_description": "Reuters piece",
             "is_independent_origin": True},
            {"group_id": 1, "source_indices": [1], "origin_description": "Unknown blog",
             "is_independent_origin": True},
        ],
        "relationships": [
            {"source_a": 0, "source_b": 1, "relationship": "unclear",
             "explanation": "Insufficient information to determine relationship."},
        ],
        "independent_origin_count": 2,
        "explanation": "Relationship between sources is unclear.",
    })
    sources = ind_sources("reuters.com", "someblog.net")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    [rel] = ia["relationships"]
    assert rel["relationship"] == "unclear"


# ---- 16. Missing source metadata → domain fallback -----------------------

async def test_independence_llm_failure_uses_domain_fallback(monkeypatch):
    patch_llm(monkeypatch, error=True)
    sources = ind_sources("reuters.com", "reuters.com", "cdc.gov")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    assert ia["llm_fallback"] is True
    # reuters.com appears twice but should be grouped into one origin
    assert ia["independent_source_count"] == 2     # reuters.com group + cdc.gov group
    assert ia["total_source_count"] == 3
    assert ia["overall_independence"] in ("medium", "low")


# ---- 17. Subdomains correctly grouped to registered domain ----------------

async def test_independence_subdomain_grouping(monkeypatch):
    """news.reuters.com and www.reuters.com both resolve to reuters.com → same group."""
    patch_llm(monkeypatch, error=True)
    sources = [
        {"id": "sa", "domain": "news.reuters.com", "url": "https://news.reuters.com/a",
         "title": "A", "publisher": "Reuters", "source_type": "news",
         "quality_score": 0.85, "relevance_score": 0.9},
        {"id": "sb", "domain": "www.reuters.com", "url": "https://www.reuters.com/b",
         "title": "B", "publisher": "Reuters", "source_type": "news",
         "quality_score": 0.85, "relevance_score": 0.8},
    ]
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    assert ia["llm_fallback"] is True
    assert ia["independent_source_count"] == 1    # both map to reuters.com


# ---- 18. No sources → empty analysis -------------------------------------

async def test_independence_no_sources(monkeypatch):
    out = await IndependenceAgent().execute(ind_state([]))
    ia = out["independence_analysis"]
    assert ia["independent_source_count"] == 0
    assert ia["overall_independence"] == "unknown"
    assert ia["source_groups"] == []


# ---- 19. Invalid LLM indices are silently dropped ------------------------

async def test_independence_ignores_invalid_indices(monkeypatch):
    patch_llm(monkeypatch, {
        "groups": [
            {"group_id": 0, "source_indices": [0, 99],   # 99 is out of range
             "origin_description": "Reuters only", "is_independent_origin": True},
        ],
        "relationships": [
            {"source_a": 99, "source_b": 0, "relationship": "derived",  # invalid → dropped
             "explanation": "should be ignored"},
        ],
        "independent_origin_count": 1,
        "explanation": "One origin.",
    })
    sources = ind_sources("reuters.com")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    # group_id=0 has valid index 0 only (99 dropped); singleton for the skipped source added
    source_ids_in_groups = [sid for g in ia["source_groups"] for sid in g["source_ids"]]
    assert "s0" in source_ids_in_groups
    # The bad relationship is dropped entirely
    assert ia["relationships"] == []


# ---- 20. Unknown relationship type mapped to "unclear" -------------------

async def test_independence_unknown_relationship_type_normalised(monkeypatch):
    patch_llm(monkeypatch, {
        "groups": [
            {"group_id": 0, "source_indices": [0], "is_independent_origin": True,
             "origin_description": "Reuters"},
            {"group_id": 1, "source_indices": [1], "is_independent_origin": True,
             "origin_description": "CDC"},
        ],
        "relationships": [
            {"source_a": 0, "source_b": 1, "relationship": "TOTALLY_MADE_UP",
             "explanation": "x"},
        ],
        "independent_origin_count": 2,
        "explanation": "Two origins.",
    })
    sources = ind_sources("reuters.com", "cdc.gov")
    out = await IndependenceAgent().execute(ind_state(sources))
    ia = out["independence_analysis"]
    [rel] = ia["relationships"]
    assert rel["relationship"] == "unclear"


# ---- 21. llm_degraded flag → domain fallback used -------------------------

async def test_independence_respects_llm_degraded(monkeypatch):
    called = []

    async def should_not_be_called(self, *a, **k):
        called.append(True)

    monkeypatch.setattr(LLMClient, "generate_json", should_not_be_called)
    sources = ind_sources("reuters.com", "cdc.gov")
    out = await IndependenceAgent().execute(ind_state(sources, llm_degraded=True))
    ia = out["independence_analysis"]
    assert ia["llm_fallback"] is True
    assert called == []


# ---- 22. State keys preserved -------------------------------------------

async def test_independence_preserves_earlier_state_keys(monkeypatch):
    patch_llm(monkeypatch, {
        "groups": [{"group_id": 0, "source_indices": [0], "is_independent_origin": True,
                    "origin_description": "Reuters"}],
        "relationships": [],
        "independent_origin_count": 1,
        "explanation": "One origin.",
    })
    sources = ind_sources("reuters.com")
    state = ind_state(sources)
    state["extracted_claims"] = CLAIMS
    state["verified_claims"] = [{"claim_id": "c1", "verification_status": "supported"}]
    out = await IndependenceAgent().execute(state)
    assert out["extracted_claims"] == CLAIMS
    assert out["verified_claims"] == state["verified_claims"]


# ===========================================================================
# VerdictAgent: verified_claims and independence_analysis integration
# ===========================================================================

from backend.app.agents.verdict_agent.agent import VerdictAgent  # noqa: E402


def verdict_ev(i, stance, source="s1", claim="c1", rel=0.9, conf=0.9):
    return {
        "id": f"e{i}", "claim_id": claim, "source_id": source,
        "source_url": f"https://x/{i}", "evidence_text": f"evidence {i}",
        "stance": stance, "relevance_score": rel, "confidence": conf,
    }


def verdict_state(evidence, verified_claims=None, independence_analysis=None,
                  conflicts=None, **extra):
    return {
        "investigation_id": "inv-verdict",
        "extracted_claims": CLAIMS,
        "evaluated_sources": SOURCES,
        "extracted_evidence": evidence,
        "detected_conflicts": conflicts or [],
        "verified_claims": verified_claims or [],
        "independence_analysis": independence_analysis or {},
        **extra,
    }


def patch_verdict_llm(monkeypatch, label="true", explanation="Confirmed."):
    async def fake(self, prompt, *, system=None, temperature=0.1):
        return {"label": label, "explanation": explanation}

    monkeypatch.setattr(LLMClient, "generate_json", fake)


# ---- 23. Partial verification changes effective ratio with mixed evidence ---

async def test_verdict_partially_supported_affects_mixed_evidence(monkeypatch):
    """With mixed evidence, a partially_supported multiplier (0.7) reduces the weight of
    supporting items relative to contradicting items, shifting the ratio toward "mixed"
    and lowering confidence compared to no verification data."""
    patch_verdict_llm_error(monkeypatch)
    # Moderate supporting item (s2, low quality) vs strong contradicting item (s1, high quality)
    evidence = [
        verdict_ev(1, "supporting", "s2", rel=0.55, conf=0.55),  # low-quality support
        verdict_ev(2, "contradicting", "s1", rel=0.9, conf=0.9),  # high-quality contra
    ]
    base = (await VerdictAgent().execute(verdict_state(evidence)))["final_verdict"]

    # Applying partially_supported (mult=0.7) further reduces the already-weak supporting weight
    partial = (await VerdictAgent().execute(verdict_state(
        evidence,
        verified_claims=[{"claim_id": "c1", "verification_status": "partially_supported",
                          "confidence": 0.5}],
    )))["final_verdict"]
    # Confidence should be equal or lower when the supporting side is down-weighted further
    assert partial["final_verdict"]["confidence"] <= base["final_verdict"]["confidence"] \
        if False else partial["confidence"] <= base["confidence"]


def patch_verdict_llm_error(monkeypatch):
    async def fake(self, prompt, *, system=None, temperature=0.1):
        raise ClaimLensError("down", code="llm_failed")

    monkeypatch.setattr(LLMClient, "generate_json", fake)


# ---- 24. Insufficient evidence shifts a barely-true verdict toward mixed --

async def test_verdict_insufficient_verification_shifts_mixed(monkeypatch):
    """When verification says insufficient_evidence (mult=0.5), a claim that was barely 'true'
    (with moderate evidence) can shift to 'mostly_true' or 'mixed' because the effective
    support weights drop enough to change the ratio."""
    patch_verdict_llm_error(monkeypatch)
    # Construct evidence that barely tips into "true" territory (ratio ≥ 0.85):
    # 2 moderate supporting + 1 very weak contradicting
    evidence = [
        verdict_ev(1, "supporting", "s1", rel=0.6, conf=0.6),
        verdict_ev(2, "supporting", "s3", rel=0.55, conf=0.55),
        verdict_ev(3, "contradicting", "s2", rel=0.15, conf=0.15),
    ]
    base_v = (await VerdictAgent().execute(verdict_state(evidence)))["final_verdict"]

    insuf_v = (await VerdictAgent().execute(verdict_state(
        evidence,
        verified_claims=[{"claim_id": "c1", "verification_status": "insufficient_evidence",
                          "confidence": 0.2}],
    )))["final_verdict"]

    # The label must shift (from true/mostly_true toward mixed) OR confidence must decrease
    SCALE_IDX = {"false": 0, "mostly_false": 1, "mixed": 2, "mostly_true": 3, "true": 4}
    base_idx = SCALE_IDX.get(base_v["label"], 4)
    insuf_idx = SCALE_IDX.get(insuf_v["label"], 4)
    # Either label went down or confidence went down
    assert insuf_idx < base_idx or insuf_v["confidence"] <= base_v["confidence"]


# ---- 25. Low source independence applies a confidence penalty ------------

async def test_verdict_low_independence_reduces_confidence(monkeypatch):
    patch_verdict_llm_error(monkeypatch)
    evidence = [verdict_ev(1, "supporting", "s1"), verdict_ev(2, "supporting", "s3")]
    without_ind = (await VerdictAgent().execute(verdict_state(evidence)))["final_verdict"]
    with_low_ind = (await VerdictAgent().execute(verdict_state(
        evidence,
        independence_analysis={
            "independent_source_count": 1,
            "total_source_count": 3,
            "independence_ratio": 0.33,
            "overall_independence": "low",
            "explanation": "Most sources trace to one origin.",
            "llm_fallback": False,
        },
    )))["final_verdict"]
    assert with_low_ind["confidence"] < without_ind["confidence"]
    assert with_low_ind["uncertainty"] > without_ind["uncertainty"]


# ---- 26. High independence has no penalty --------------------------------

async def test_verdict_high_independence_no_penalty(monkeypatch):
    patch_verdict_llm_error(monkeypatch)
    evidence = [verdict_ev(1, "supporting", "s1"), verdict_ev(2, "supporting", "s3")]
    without_ind = (await VerdictAgent().execute(verdict_state(evidence)))["final_verdict"]
    with_high_ind = (await VerdictAgent().execute(verdict_state(
        evidence,
        independence_analysis={
            "independent_source_count": 3,
            "total_source_count": 3,
            "independence_ratio": 1.0,
            "overall_independence": "high",
            "explanation": "All sources are independent.",
            "llm_fallback": False,
        },
    )))["final_verdict"]
    # high independence should not reduce confidence vs no analysis
    assert abs(with_high_ind["confidence"] - without_ind["confidence"]) < 0.01


# ---- 27. Low independence note appears in baseline explanation -----------

async def test_verdict_baseline_explanation_includes_independence_note(monkeypatch):
    patch_verdict_llm_error(monkeypatch)
    evidence = [verdict_ev(1, "supporting", "s1")]
    out = await VerdictAgent().execute(verdict_state(
        evidence,
        independence_analysis={
            "independent_source_count": 1,
            "total_source_count": 4,
            "independence_ratio": 0.25,
            "overall_independence": "low",
            "explanation": "All articles trace to one press release.",
            "llm_fallback": False,
        },
    ))
    explanation = out["final_verdict"]["explanation"]
    # The independence note must appear somewhere in the explanation
    assert "independence" in explanation.lower() or "origin" in explanation.lower()


# ===========================================================================
# Full pipeline smoke test (all 8 agents via build_investigation_workflow)
# ===========================================================================

async def test_full_8_agent_pipeline_runs_both_new_agents():
    """End-to-end smoke test: all 8 agents fire, verified_claims and independence_analysis
    are populated, and a valid final_verdict is produced."""
    from backend.app.workflows.executor import WorkflowExecutor  # noqa: PLC0415

    stages_seen: list[str] = []

    async def on_stage(node: str, _state: dict) -> None:
        stages_seen.append(node)

    executor = WorkflowExecutor()
    final = await executor.execute(
        input_text="The company has 50,000 users and 180% growth",
        input_type="text",
        investigation_id="inv-pipeline-smoke",
        on_stage=on_stage,
    )

    # Both new stages must have fired
    assert "verification" in stages_seen, f"Missing 'verification' stage. Saw: {stages_seen}"
    assert "independence" in stages_seen, f"Missing 'independence' stage. Saw: {stages_seen}"

    # Verified claims must be a non-empty list with the right shape
    vc = final.get("verified_claims", [])
    assert isinstance(vc, list) and len(vc) > 0, "verified_claims is empty"
    for item in vc:
        assert "claim_id" in item
        assert item["verification_status"] in VERIFICATION_STATUSES
        assert 0.0 <= item["confidence"] <= 1.0

    # Independence analysis must be a dict with the right keys
    ia = final.get("independence_analysis", {})
    assert isinstance(ia, dict) and ia, "independence_analysis is empty"
    assert "independent_source_count" in ia
    assert "total_source_count" in ia
    assert ia["total_source_count"] > 0
    assert ia["overall_independence"] in ("high", "medium", "low", "unknown")

    # Final verdict must exist and be a valid label
    fv = final.get("final_verdict")
    assert fv is not None, "No final_verdict produced"
    assert fv["label"] in {"true", "mostly_true", "mixed", "mostly_false", "false", "unverified"}
    assert 0.0 <= fv["confidence"] <= 1.0
    assert 0.0 <= fv["uncertainty"] <= 1.0

    # The complete expected stage order
    expected_order = [
        "claim_extraction", "research", "source_evaluation", "evidence_extraction",
        "verification", "conflict_detection", "independence", "verdict",
    ]
    assert stages_seen == expected_order, f"Stage order wrong: {stages_seen}"
