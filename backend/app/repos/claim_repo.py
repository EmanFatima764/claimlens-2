from __future__ import annotations

from backend.app.repos.base import BaseRepository


class ClaimRepository(BaseRepository):
    table = "claims"
    order_desc = False
