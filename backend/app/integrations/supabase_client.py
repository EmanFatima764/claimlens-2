from __future__ import annotations

from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError


class SupabaseClient:
    """Supabase client wrapper placeholder.

    This will eventually initialize and expose database operations for investigation storage.
    """

    def __init__(self) -> None:
        self.url = settings.supabase_url
        self.anon_key = settings.supabase_anon_key
        self.service_role_key = settings.supabase_service_role_key

    async def healthcheck(self) -> dict[str, Any]:
        """Placeholder database health check."""
        if not self.url:
            raise ClaimLensError("Supabase URL is not configured", code="supabase_missing_url")
        return {"status": "not_implemented", "url": self.url}
