from __future__ import annotations

from backend.app.repos.base import BaseRepository


class ConflictRepository(BaseRepository):
    table = "conflicts"
    order_by = "severity"
