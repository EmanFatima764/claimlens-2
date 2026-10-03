from __future__ import annotations

from backend.app.agents.claim_agent.agent import ClaimAgent
from backend.app.agents.evidence_agent.agent import EvidenceAgent
from backend.app.agents.research_agent.agent import ResearchAgent
from backend.app.agents.source_agent.agent import SourceAgent, heuristic
from backend.app.core.utils import parse_json


def base_state(text="The company has 50,000 users and 180% growth"):
    return {"investigation_id": "inv-1", "input_text": text, "input_type": "text"}


async def test_claim_agent_extracts_and_sanitizes():
    state = await ClaimAgent().execute(base_state())
    claims = state["extracted_claims"]
    assert len(claims) == 2
    assert all(c["id"] for c in claims)
    assert claims[1]["claim_type"] == "other"      # invalid type sanitized
    assert claims[1]["confidence"] == 1.0           # clamped
    assert claims[1]["normalized_text"]             # defaulted
    assert state["input_text"]                      # earlier keys preserved


async def test_claim_agent_falls_back_when_llm_fails(monkeypatch):
    from backend.app.core.exceptions import ClaimLensError
    from backend.app.integrations.llm import LLMClient

    async def boom(self, *a, **k):
        raise ClaimLensError("down", code="llm_failed")

    monkeypatch.setattr(LLMClient, "generate_json", boom)
    state = await ClaimAgent().execute(base_state("Water boils at 100C at sea level"))
    assert len(state["extracted_claims"]) == 1
    assert state["extracted_claims"][0]["text"].startswith("Water boils")


async def test_research_agent_dedupes_per_claim():
    s = await ClaimAgent().execute(base_state())
    s = await ResearchAgent().execute(s)
    results = s["research_results"]
    assert results
    for claim in s["extracted_claims"]:
        urls = [r["url"] for r in results if r["claim_id"] == claim["id"]]
        assert len(urls) == len(set(urls))


async def test_source_agent_merges_across_claims_and_scores():
    s = await ClaimAgent().execute(base_state())
    s = await ResearchAgent().execute(s)
    s = await SourceAgent().execute(s)
    sources = s["evaluated_sources"]
    shared = [x for x in sources if x["url"].endswith("/shared/")]
    assert len(shared) == 1 and len(shared[0]["claim_ids"]) == 2   # same URL found for both claims -> one source
    assert all(0 <= x["quality_score"] <= 1 for x in sources)
    assert all(x["id"] for x in sources)


async def test_evidence_agent_validates_llm_output():
    s = await ClaimAgent().execute(base_state())
    s = await ResearchAgent().execute(s)
    s = await SourceAgent().execute(s)
    s = await EvidenceAgent().execute(s)
    ev = s["extracted_evidence"]
    assert ev and {e["stance"] for e in ev} <= {"supporting", "contradicting", "neutral"}
    assert not any("bad index" in e["evidence_text"] for e in ev)
    assert all(e["source_id"] and e["claim_id"] for e in ev)


def test_source_heuristics():
    assert heuristic("cdc.gov")[1] == "government"
    assert heuristic("reddit.com")[0] < 0.4
    assert heuristic("news.reuters.com")[0] > 0.8


def test_parse_json_handles_fences_and_prose():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Sure! Here: {"a": [1,2]} hope it helps') == {"a": [1, 2]}


async def test_evidence_agent_flags_llm_failure(monkeypatch):
    from backend.app.core.exceptions import ClaimLensError
    from backend.app.integrations.llm import LLMClient

    s = await ClaimAgent().execute(base_state())
    s = await ResearchAgent().execute(s)
    s = await SourceAgent().execute(s)

    async def boom(self, *a, **k):
        raise ClaimLensError("down", code="llm_failed")

    monkeypatch.setattr(LLMClient, "generate_json", boom)
    s = await EvidenceAgent().execute(s)
    assert s["llm_degraded"] is True
    assert all(e["stance"] == "neutral" for e in s["extracted_evidence"])  # no guessed stances
