from __future__ import annotations

from typing import Any

from backend.app.core.exceptions import ClaimLensError
from backend.app.core.utils import parse_json
from backend.app.integrations.groq_client import GroqClient


class LLMClient:
    """LLM facade used by every agent. Groq is the only provider."""

    def __init__(self) -> None:
        self.client = GroqClient()

    @property
    def configured(self) -> bool:
        return self.client.configured

    async def generate(
        self, prompt: str, *, system: str | None = None, temperature: float = 0.2, json_mode: bool = False
    ) -> str:
        if not self.client.configured:
            raise ClaimLensError("GROQ_API_KEY is not set (put it in backend/.env and restart)", code="llm_not_configured")
        return await self.client.generate(prompt, system=system, temperature=temperature, json_mode=json_mode)

    async def generate_json(self, prompt: str, *, system: str | None = None, temperature: float = 0.1) -> Any:
        text = await self.generate(prompt, system=system, temperature=temperature, json_mode=True)
        try:
            return parse_json(text)
        except ClaimLensError:
            raise ClaimLensError("LLM returned invalid JSON", code="llm_invalid_json")