from __future__ import annotations

from fastapi import APIRouter

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations.groq_client import GroqClient
from backend.app.integrations.llm import LLMClient
from backend.app.integrations.supabase_client import SupabaseClient

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, object]:
    """Health + which integrations are configured (booleans only, never keys)."""
    db = SupabaseClient()
    return {
        "status": "ok",
        "database": "memory" if db.use_memory else "supabase",
        "llm_provider": "groq",
        "llm_model": settings.groq_model,
        "llm_configured": bool(settings.groq_api_key),
        "tavily_configured": bool(settings.tavily_api_key),
    }


@router.get("/llm")
async def health_llm() -> dict[str, object]:
    """Makes one real call to Groq and shows the exact error if it fails (never exposes the key)."""
    llm = LLMClient()
    if not llm.configured:
        return {"ok": False, "error": "GROQ_API_KEY is empty - backend/.env was not found or the key is missing"}
    try:
        reply = await llm.generate("Reply with the single word OK.", temperature=0.0)
        return {"ok": True, "model": settings.groq_model, "reply": reply.strip()[:50]}
    except ClaimLensError as exc:
        return {"ok": False, "model": settings.groq_model, "error_code": exc.code, "error": exc.message}


@router.get("/llm/models")
async def health_llm_models() -> dict[str, object]:
    """Lists the model ids your Groq key can use - copy one into GROQ_MODEL."""
    try:
        models = await GroqClient().list_models()
        return {"ok": True, "current_model": settings.groq_model, "available": models}
    except ClaimLensError as exc:
        return {"ok": False, "error_code": exc.code, "error": exc.message}