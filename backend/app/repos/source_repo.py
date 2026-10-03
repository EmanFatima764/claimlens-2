from __future__ import annotations

from backend.app.repos.base import BaseRepository


class SourceRepository(BaseRepository):
    table = "sources"
    order_by = "quality_score"
