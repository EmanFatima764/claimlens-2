from __future__ import annotations

import asyncio
from typing import Any

from backend.app.agents.base import BaseAgent
from backend.app.core.exceptions import ClaimLensError
from backend.app.core.logging import get_logger
from backend.app.core.utils import normalize_url, truncate
from backend.app.integrations.llm import LLMClient
from backend.app.integrations.tavily_client import TavilyClient

logger = get_logger(__name__)

SYSTEM = "You write precise web-search queries for fact-checking. Prefer primary sources and official data."

PROMPT = """Claim to verify: "{claim}"
{previous}
Write {n} different web search queries that would find evidence for OR against this claim.
- Keep each query short and specific (names, numbers, dates that appear in the claim).
- Make the first query a neutral lookup of the fact itself; make the others look for official sources,
  fact-checks or opposing information.
Return JSON: {{"queries": ["...", "..."]}}"""

FALLBACK_SUFFIXES = ["", " fact check", " official source", " evidence"]


class ResearchAgent(BaseAgent):
    """Agent 2: claims -> web results (`research_results`). Iterates up to `max_iterations` if results are thin."""

    name = "research_agent"

    def __init__(
        self,
        llm: LLMClient | None = None,
        tavily: TavilyClient | None = None,
        max_iterations: int = 3,
        queries_per_round: int = 2,
        results_per_query: int = 5,
        min_results_per_claim: int = 5,
        concurrency: int = 3,
    ) -> None:
        self.llm = llm or LLMClient()
        self.tavily = tavily or TavilyClient()
        self.max_iterations = max_iterations
        self.queries_per_round = queries_per_round
        self.results_per_query = results_per_query
        self.min_results_per_claim = min_results_per_claim
        self.concurrency = concurrency

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        if not self.tavily.configured:
            raise ClaimLensError("TAVILY_API_KEY is not configured - cannot research claims", code="tavily_missing_key")
        sem = asyncio.Semaphore(self.concurrency)
        claims = state.get("extracted_claims", [])
        per_claim = await asyncio.gather(*[self._research_claim(c, sem) for c in claims])
        results = [r for group in per_claim for r in group]
        logger.info("Research collected %d results for %d claims", len(results), len(claims))
        return {"research_results": results}

    async def _research_claim(self, claim: dict[str, Any], sem: asyncio.Semaphore) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        used_queries: list[str] = []

        for iteration in range(self.max_iterations):
            queries = [q for q in await self._queries(claim, used_queries, iteration) if q not in used_queries]
            if not queries:
                break
            used_queries.extend(queries)
            batches = await asyncio.gather(*[self._search(q, sem) for q in queries])
            for query, hits in zip(queries, batches):
                for hit in hits:
                    key = normalize_url(hit["url"])
                    if key in seen_urls:
                        continue
                    seen_urls.add(key)
                    collected.append(
                        {
                            "claim_id": claim["id"],
                            "query": query,
                            "url": hit["url"],
                            "title": hit["title"],
                            "content": truncate(hit["content"], 2000),
                            "score": hit["score"],
                        }
                    )
            if len(collected) >= self.min_results_per_claim:
                break
        return collected

    async def _search(self, query: str, sem: asyncio.Semaphore) -> list[dict[str, Any]]:
        async with sem:
            try:
                return await self.tavily.search(query, max_results=self.results_per_query)
            except ClaimLensError as exc:
                logger.warning("Search failed for %r: %s", query, exc.message)
                return []

    async def _queries(self, claim: dict[str, Any], used: list[str], iteration: int) -> list[str]:
        text = claim.get("normalized_text") or claim["text"]
        previous = f"Queries already tried (do not repeat): {used}\n" if used else ""
        try:
            data = await self.llm.generate_json(
                PROMPT.format(claim=text, previous=previous, n=self.queries_per_round), system=SYSTEM, temperature=0.4
            )
            queries = [str(q).strip() for q in data.get("queries", []) if str(q).strip()] if isinstance(data, dict) else []
            if queries:
                return queries[: self.queries_per_round]
        except ClaimLensError as exc:
            logger.warning("Query generation failed (%s) - using fallback queries", exc.message)
        base = truncate(text, 200)
        start = iteration * self.queries_per_round
        return [(base + s).strip() for s in FALLBACK_SUFFIXES[start : start + self.queries_per_round]]
