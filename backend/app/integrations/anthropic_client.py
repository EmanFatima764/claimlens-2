from __future__ import annotations

from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError


class AnthropicClient:
    """Wrapper for Anthropic LLM calls used for fallback or secondary reasoning.

    This is intentionally a placeholder to keep a clean architecture before implementation.
    """

    def __init__(self) -> None:
        self.api_key = settings.anthropic_api_key

    async def generate(self, prompt: str, *, temperature: float = 0.2) -> dict[str, Any]:
        if not self.api_key:
            raise ClaimLensError("Anthropic API key is not configured", code="anthropic_missing_key")
        return {
            "prompt": prompt,
            "temperature": temperature,
            "status": "not_implemented",
            "text": "",
        }
