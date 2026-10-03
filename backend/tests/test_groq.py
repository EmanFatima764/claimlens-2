from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.core.exceptions import ClaimLensError
from backend.app.integrations import groq_client
from backend.app.integrations.groq_client import GroqClient
from backend.app.integrations.llm import LLMClient
from backend.app.main import app

REAL_GENERATE = LLMClient.generate  # captured at import, before conftest replaces it with a fake


def capture_request(monkeypatch, reply=None):
    seen = {}

    async def fake_request_json(method, url, *, service, headers=None, json_body=None, **kw):
        seen.update(method=method, url=url, service=service, headers=headers, body=json_body, kw=kw)
        return reply if reply is not None else {"choices": [{"message": {"content": '{"ok": true}'}}]}

    monkeypatch.setattr(groq_client, "request_json", fake_request_json)
    return seen


async def test_groq_builds_openai_style_json_request(monkeypatch):
    seen = capture_request(monkeypatch)
    out = await GroqClient(api_key="k", model="m").generate("hello", system="be brief", json_mode=True)
    assert out == '{"ok": true}'
    assert seen["url"].endswith("/openai/v1/chat/completions") and seen["headers"]["Authorization"] == "Bearer k"
    body = seen["body"]
    assert body["model"] == "m" and body["response_format"] == {"type": "json_object"}
    assert body["messages"][0]["role"] == "system" and "JSON" in body["messages"][0]["content"]
    assert body["messages"][-1] == {"role": "user", "content": "hello"}


async def test_groq_plain_text_mode_has_no_json_format(monkeypatch):
    seen = capture_request(monkeypatch)
    await GroqClient(api_key="k").generate("hi")
    assert "response_format" not in seen["body"] and seen["body"]["messages"][0]["role"] == "user"


async def test_groq_requires_key_and_valid_response(monkeypatch):
    with pytest.raises(ClaimLensError) as e:
        await GroqClient(api_key="").generate("x")
    assert e.value.code == "groq_missing_key"
    capture_request(monkeypatch, reply={"unexpected": 1})
    with pytest.raises(ClaimLensError) as e:
        await GroqClient(api_key="k").generate("x")
    assert e.value.code == "groq_bad_response"


async def test_llm_client_without_key_gives_clear_error(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.groq_api_key", "")
    monkeypatch.setattr(LLMClient, "generate", REAL_GENERATE)
    with pytest.raises(ClaimLensError) as e:
        await LLMClient().generate("x")
    assert e.value.code == "llm_not_configured" and "GROQ_API_KEY" in e.value.message


def test_health_llm_reports_missing_key(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.groq_api_key", "")
    r = TestClient(app).get("/api/v1/health/llm").json()
    assert r["ok"] is False and "GROQ_API_KEY" in r["error"]


def test_health_llm_reports_success_and_exact_error(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.groq_api_key", "k")
    client = TestClient(app)

    async def ok(self, prompt, **kw):
        return "OK"

    monkeypatch.setattr(LLMClient, "generate", ok)
    assert client.get("/api/v1/health/llm").json()["ok"] is True

    async def bad(self, prompt, **kw):
        raise ClaimLensError("groq HTTP 401: invalid api key", code="groq_http_401")

    monkeypatch.setattr(LLMClient, "generate", bad)
    r = client.get("/api/v1/health/llm").json()
    assert r["ok"] is False and r["error_code"] == "groq_http_401" and "invalid api key" in r["error"]


async def test_gpt_oss_gets_low_reasoning_effort_but_other_models_do_not(monkeypatch):
    seen = capture_request(monkeypatch)
    await GroqClient(api_key="k", model="openai/gpt-oss-120b").generate("hi")
    assert seen["body"]["reasoning_effort"] == "low"
    await GroqClient(api_key="k", model="some-other-model").generate("hi")
    assert "reasoning_effort" not in seen["body"]


def test_default_model_is_a_public_groq_model():
    from backend.app.config import Settings

    assert Settings().groq_model.startswith("openai/gpt-oss")


async def test_list_models_returns_sorted_ids(monkeypatch):
    seen = capture_request(monkeypatch, reply={"data": [{"id": "openai/gpt-oss-20b"}, {"id": "openai/gpt-oss-120b"}]})
    assert await GroqClient(api_key="k").list_models() == ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    assert seen["method"] == "GET" and seen["url"].endswith("/models")


def test_models_endpoint(monkeypatch):
    async def fake(self):
        return ["openai/gpt-oss-120b"]

    monkeypatch.setattr(GroqClient, "list_models", fake)
    r = TestClient(app).get("/api/v1/health/llm/models").json()
    assert r["ok"] is True and r["available"] == ["openai/gpt-oss-120b"]