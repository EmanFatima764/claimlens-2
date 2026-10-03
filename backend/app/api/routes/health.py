from __future__ import annotations

from fastapi import APIRouter

from backend.app.config import settings
from backend.app.integrations.supabase_client import SupabaseClient

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, object]:
    """Health + which integrations are configured (booleans only, never keys)."""
    db = SupabaseClient()
    return {
        "status": "ok",
        "database": "memory" if db.use_memory else "supabase",
        "llm_configured": bool(settings.gemini_api_key or settings.anthropic_api_key),
        "tavily_configured": bool(settings.tavily_api_key),
    }
