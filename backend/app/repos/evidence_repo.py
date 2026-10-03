from __future__ import annotations

from backend.app.repos.base import BaseRepository


class EvidenceRepository(BaseRepository):
    table = "evidence"
    order_by = "relevance_score"
