from __future__ import annotations

from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError


class GeminiClient:
    """Wrapper for Gemini-based LLM calls.

    This will be used by agents for structured reasoning and evidence synthesis.
    """

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> dict[str, Any]:
        if not self.api_key:
            raise ClaimLensError("Gemini API key is not configured", code="gemini_missing_key")
        return {
            "prompt": prompt,
            "temperature": temperature,
            "status": "not_implemented",
            "text": "",
        }
