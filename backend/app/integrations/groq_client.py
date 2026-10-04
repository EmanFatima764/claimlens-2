from __future__ import annotations

import asyncio

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations.http import request_json

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Groq's free tier limits tokens per minute. The agents fire several calls in parallel, so cap how many
# Groq requests may be in flight at once (per event loop) instead of tripping 429s.
MAX_CONCURRENT_REQUESTS = 2
_semaphores: dict[int, asyncio.Semaphore] = {}


def _semaphore() -> asyncio.Semaphore:
    key = id(asyncio.get_running_loop())
    if key not in _semaphores:
        _semaphores[key] = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    return _semaphores[key]


class GroqClient:
    """Groq via its OpenAI-compatible chat completions REST API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        self.model = model or settings.groq_model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self, prompt: str, *, system: str | None = None, temperature: float = 0.2, json_mode: bool = False
    ) -> str:
        if not self.api_key:
            raise ClaimLensError("Groq API key is not configured", code="groq_missing_key")
        sys_prompt = system or ""
        if json_mode:
            # Groq's JSON mode requires the word "JSON" to appear in the messages.
            sys_prompt += "\n\nRespond with a single valid JSON object only. No prose, no code fences."
        messages = []
        if sys_prompt.strip():
            messages.append({"role": "system", "content": sys_prompt.strip()})
        messages.append({"role": "user", "content": prompt})

        body: dict = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": 4096}
        if "gpt-oss" in self.model:
            # gpt-oss are reasoning models: keep the thinking short so it is fast and cannot cut off the JSON.
            body["reasoning_effort"] = "low"
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        async with _semaphore():
            data = await request_json(
                "POST", GROQ_URL, service="groq",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json_body=body, timeout=45.0, retries=5,
            )
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise ClaimLensError(f"Unexpected Groq response: {str(data)[:300]}", code="groq_bad_response") from exc

    async def list_models(self) -> list[str]:
        """Model ids this API key can actually use (handy when a model name is rejected)."""
        if not self.api_key:
            raise ClaimLensError("Groq API key is not configured", code="groq_missing_key")
        data = await request_json(
            "GET", "https://api.groq.com/openai/v1/models", service="groq",
            headers={"Authorization": f"Bearer {self.api_key}"}, timeout=20.0, retries=2,
        )
        try:
            return sorted(m["id"] for m in data["data"])
        except (KeyError, TypeError) as exc:
            raise ClaimLensError(f"Unexpected Groq response: {str(data)[:300]}", code="groq_bad_response") from exc