from __future__ import annotations

from typing import Any

from backend.app.agents.base import BaseAgent
from backend.app.core.logging import get_logger
from backend.app.core.utils import clamp01, domain_of, normalize_url, truncate
from backend.app.repos.source_repo import SourceRepository

logger = get_logger(__name__)

HIGH_TRUST = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nature.com", "science.org", "who.int", "un.org",
    "worldbank.org", "imf.org", "oecd.org", "nih.gov", "cdc.gov", "sec.gov", "nasa.gov", "economist.com",
    "ft.com", "wsj.com", "nytimes.com", "washingtonpost.com", "theguardian.com", "dawn.com", "arxiv.org",
    "pubmed.ncbi.nlm.nih.gov", "thelancet.com", "bloomberg.com",
}
LOW_TRUST = {
    "reddit.com", "quora.com", "facebook.com", "x.com", "twitter.com", "tiktok.com", "instagram.com",
    "pinterest.com", "medium.com", "blogspot.com", "wordpress.com", "youtube.com", "answers.com",
}


def _in(domain: str, names: set[str]) -> bool:
    return any(domain == n or domain.endswith("." + n) for n in names)


def heuristic(domain: str) -> tuple[float, str]:
    d = domain.lower()
    if _in(d, LOW_TRUST):
        return 0.25, "social"
    if d.endswith(".gov") or ".gov." in d or d.endswith(".mil"):
        return 0.88, "government"
    if d.endswith(".edu") or ".edu." in d or ".ac." in d:
        return 0.85, "academic"
    if d.endswith(".int"):
        return 0.85, "organization"
    if _in(d, HIGH_TRUST):
        return 0.85, "news"
    if d.endswith("wikipedia.org"):
        return 0.65, "reference"
    if d.endswith(".org"):
        return 0.6, "organization"
    return 0.5, "other"


class SourceAgent(BaseAgent):
    """Agent 3: research results -> deduplicated, scored, persisted sources (`evaluated_sources`)."""

    name = "source_agent"

    def __init__(self, source_repo: SourceRepository | None = None, max_sources: int = 15) -> None:
        self.source_repo = source_repo or SourceRepository()
        self.max_sources = max_sources

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        merged = self._dedupe(state.get("research_results", []))
        if not merged:
            logger.warning("No research results to evaluate")
            return {"evaluated_sources": []}

        for s in merged:
            s["_h_score"], s["_h_type"] = heuristic(s["domain"])
        merged.sort(key=lambda s: s["relevance_score"] * s["_h_score"], reverse=True)
        merged = merged[: self.max_sources]

        # Credibility is scored from the publisher's domain: instant, free and predictable.
        evaluated: list[dict[str, Any]] = []
        for s in merged:
            quality = s["_h_score"]
            stype = s["_h_type"]
            publisher = truncate(s["domain"], 120)
            relevance = round(s["relevance_score"], 3)
            row = await self.source_repo.create(
                {
                    "investigation_id": state["investigation_id"],
                    "title": truncate(s["title"], 300),
                    "url": s["url"],
                    "publisher": publisher,
                    "source_type": stype,
                    "quality_score": quality,
                    "relevance_score": relevance,
                    "domain": s["domain"],
                }
            )
            evaluated.append(
                {
                    "id": row["id"], "url": s["url"], "title": s["title"], "domain": s["domain"],
                    "publisher": publisher, "source_type": stype, "quality_score": quality,
                    "relevance_score": relevance, "content": s["content"], "claim_ids": sorted(s["claim_ids"]),
                }
            )
        evaluated.sort(key=lambda s: s["quality_score"] * s["relevance_score"], reverse=True)
        return {"evaluated_sources": evaluated}

    @staticmethod
    def _dedupe(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_key: dict[str, dict[str, Any]] = {}
        for r in results:
            key = normalize_url(r["url"])
            if not key:
                continue
            cur = by_key.get(key)
            if cur is None:
                by_key[key] = {
                    "url": r["url"], "title": r.get("title", ""), "content": r.get("content", ""),
                    "domain": domain_of(r["url"]), "relevance_score": clamp01(r.get("score"), 0.0),
                    "claim_ids": {r["claim_id"]},
                }
            else:
                cur["claim_ids"].add(r["claim_id"])
                cur["relevance_score"] = max(cur["relevance_score"], clamp01(r.get("score"), 0.0))
                if len(r.get("content", "")) > len(cur["content"]):
                    cur["content"] = r["content"]
        return list(by_key.values())
