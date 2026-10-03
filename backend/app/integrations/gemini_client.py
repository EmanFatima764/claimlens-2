from __future__ import annotations

from typing import Any

from backend.app.config import settings
from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations.http import request_json


class GeminiClient:
    """Gemini via the public REST API (no SDK version headaches)."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model or settings.gemini_model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self, prompt: str, *, system: str | None = None, temperature: float = 0.2, json_mode: bool = False
    ) -> str:
        if not self.api_key:
            raise ClaimLensError("Gemini API key is not configured", code="gemini_missing_key")
        body: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"
        # Flash models "think" by default, which is slow and was hitting the old 10s timeout.
        # Classification/extraction does not need it. (Not supported by the *-pro models.)
        if "2.5" in self.model and "pro" not in self.model:
            body["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        data = await request_json(
            "POST", url, service="gemini", headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
            json_body=body, timeout=45.0, retries=3,
        )
        try:
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        except (KeyError, IndexError, TypeError) as exc:
            raise ClaimLensError(f"Unexpected Gemini response: {str(data)[:300]}", code="gemini_bad_response") from exc
