from __future__ import annotations

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations.http import request_json


class AnthropicClient:
    """Claude via the Messages REST API. Used as primary or fallback LLM."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.anthropic_api_key
        self.model = model or settings.anthropic_model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self, prompt: str, *, system: str | None = None, temperature: float = 0.2, json_mode: bool = False
    ) -> str:
        if not self.api_key:
            raise ClaimLensError("Anthropic API key is not configured", code="anthropic_missing_key")
        sys_prompt = system or ""
        if json_mode:
            sys_prompt += "\n\nRespond with a single valid JSON value only. No prose, no code fences."
        body = {
            "model": self.model,
            "max_tokens": 3000,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if sys_prompt.strip():
            body["system"] = sys_prompt.strip()
        data = await request_json(
            "POST", "https://api.anthropic.com/v1/messages", service="anthropic",
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json_body=body, timeout=45.0, retries=3,
        )
        try:
            return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise ClaimLensError(f"Unexpected Anthropic response: {str(data)[:300]}", code="anthropic_bad_response") from exc
