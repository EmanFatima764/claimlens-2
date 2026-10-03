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
