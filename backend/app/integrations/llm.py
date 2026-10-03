from __future__ import annotations

from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError
from backend.app.core.logging import get_logger
from backend.app.core.utils import parse_json
from backend.app.integrations.anthropic_client import AnthropicClient
from backend.app.integrations.gemini_client import GeminiClient

logger = get_logger(__name__)


class LLMClient:
    """Provider-agnostic LLM facade: tries LLM_PROVIDER first, then any other configured provider."""

    def __init__(self, provider: str | None = None) -> None:
        clients = {"gemini": GeminiClient(), "anthropic": AnthropicClient()}
        primary = (provider or settings.llm_provider) if (provider or settings.llm_provider) in clients else "gemini"
        order = [primary] + [name for name in clients if name != primary]
        self.providers = [(name, clients[name]) for name in order if clients[name].configured]

    @property
    def configured(self) -> bool:
        return bool(self.providers)

    async def generate(
        self, prompt: str, *, system: str | None = None, temperature: float = 0.2, json_mode: bool = False
    ) -> str:
        if not self.providers:
            raise ClaimLensError("No LLM API key configured (set GEMINI_API_KEY or ANTHROPIC_API_KEY)", code="llm_not_configured")
        errors: list[str] = []
        for name, client in self.providers:
            try:
                return await client.generate(prompt, system=system, temperature=temperature, json_mode=json_mode)
            except ClaimLensError as exc:
                logger.warning("LLM provider %s failed: %s", name, exc.message)
                errors.append(f"{name}: {exc.message}")
        raise ClaimLensError("All LLM providers failed - " + " | ".join(errors), code="llm_failed")

    async def generate_json(self, prompt: str, *, system: str | None = None, temperature: float = 0.1) -> Any:
        text = await self.generate(prompt, system=system, temperature=temperature, json_mode=True)
        try:
            return parse_json(text)
        except ClaimLensError:
            raise ClaimLensError("LLM returned invalid JSON", code="llm_invalid_json")
