from __future__ import annotations

import pytest

from backend.app.integrations.llm import LLMClient
from backend.app.integrations.supabase_client import reset_memory
from backend.app.integrations.tavily_client import TavilyClient


@pytest.fixture(autouse=True)
def fresh_memory_db(monkeypatch):
    """Every test starts with an empty in-memory DB and no real network access."""
    monkeypatch.setattr("backend.app.integrations.supabase_client.settings.supabase_url", "")
    reset_memory()
    yield
    reset_memory()


@pytest.fixture(autouse=True)
def fake_external_services(monkeypatch):
    async def fake_generate_json(self, prompt, *, system=None, temperature=0.1):
        if "Evaluate each candidate pair" in prompt:
            return {"pairs": [{"pair": 0, "is_conflict": True, "conflict_type": "numerical_discrepancy",
                               "severity": 0.7, "explanation": "reuters.com and example.com report different figures."}]}
        if "Final verdict synthesis" in prompt:
            return {"label": "mixed", "explanation": "Sources disagree on the figures, so the claim is only partly supported."}
        if "Extract the distinct factual claims" in prompt:
            return {"claims": [
                {"text": "The company has 50,000 active users", "normalized_text": "The company has 50,000 active users.",
                 "claim_type": "statistical", "entities": ["The company"], "confidence": 0.9},
                {"text": "Revenue grew 180% in 12 months", "claim_type": "bogus-type", "confidence": 5},
            ]}
        if "web search queries" in prompt:
            return {"queries": ["company active users report", "company revenue growth audit"]}
        if "Rate each source" in prompt:
            return {"sources": [{"index": 0, "quality_score": 0.9, "source_type": "news", "publisher": "Reuters"}]}
        if "source excerpts" in prompt:
            return {"evidence": [
                {"source_index": 0, "evidence_text": "Reports 52,000 monthly users.", "stance": "supporting",
                 "relevance_score": 0.9, "confidence": 0.8},
                {"source_index": 1, "evidence_text": "Revenue growth was 90%.", "stance": "contradicting",
                 "relevance_score": 0.8, "confidence": 0.7},
                {"source_index": 99, "evidence_text": "ignored: bad index", "stance": "supporting"},
            ]}
        # VerificationAgent: verifies claims against collected evidence
        if "verification_status" in prompt or "evidence items" in prompt:
            return {
                "verification_status": "partially_supported",
                "confidence": 0.65,
                "supporting_evidence": ["Reports 52,000 monthly users."],
                "contradicting_evidence": ["Revenue growth was 90%."],
                "reasoning": "One source supports the user count claim, another contradicts the growth figure.",
                "unresolved_issues": ["Growth percentage differs across sources."],
            }
        # IndependenceAgent: analyses whether sources are independent
        if "origin group" in prompt or "independence" in prompt.lower():
            return {
                "groups": [
                    {"group_id": 0, "source_indices": [0], "origin_description": "Reuters primary report",
                     "is_independent_origin": True},
                    {"group_id": 1, "source_indices": [1, 2], "origin_description": "Blog and derived article",
                     "is_independent_origin": True},
                ],
                "relationships": [
                    {"source_a": 1, "source_b": 2, "relationship": "derived",
                     "explanation": "example.com blog appears to derive from the shared Reuters article."},
                ],
                "independent_origin_count": 2,
                "explanation": "Two independent evidence origins identified: Reuters and a blog cluster.",
            }
        raise AssertionError(f"unexpected prompt: {prompt[:80]}")

    async def fake_generate(self, prompt, *, system=None, temperature=0.2, json_mode=False):
        return "Because evidence is split [S1]."

    async def fake_search(self, query, *, max_results=5, search_depth="basic"):
        slug = query.replace(" ", "-")[:20]
        return [
            {"url": f"https://www.reuters.com/{slug}", "title": "Reuters piece", "content": "x" * 300, "score": 0.9},
            {"url": f"https://example.com/{slug}", "title": "Blog post", "content": "y" * 300, "score": 0.5},
            {"url": "https://www.reuters.com/shared/", "title": "Shared", "content": "z" * 400, "score": 0.7},
        ]

    monkeypatch.setattr(LLMClient, "generate_json", fake_generate_json)
    monkeypatch.setattr(LLMClient, "generate", fake_generate)
    monkeypatch.setattr(TavilyClient, "search", fake_search)
    monkeypatch.setattr(TavilyClient, "configured", property(lambda self: True))
