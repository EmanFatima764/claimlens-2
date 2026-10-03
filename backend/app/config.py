from __future__ import annotations

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(BACKEND_ENV_FILE)
load_dotenv()


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


class Settings(BaseModel):
    """Environment-driven settings for the backend application."""

    app_name: str = "ClaimLens 2.0"
    environment: str = Field(default_factory=lambda: _env("APP_ENV", "development"))
    debug: bool = Field(default_factory=lambda: _env("DEBUG", "false").lower() == "true")
    version: str = "0.2.0"

    supabase_url: str = Field(default_factory=lambda: _env("SUPABASE_URL"))
    supabase_anon_key: str = Field(default_factory=lambda: _env("SUPABASE_ANON_KEY"))
    supabase_service_role_key: str = Field(default_factory=lambda: _env("SUPABASE_SERVICE_ROLE_KEY"))

    llm_provider: str = Field(default_factory=lambda: _env("LLM_PROVIDER", "gemini").lower())
    gemini_api_key: str = Field(default_factory=lambda: _env("GEMINI_API_KEY"))
    gemini_model: str = Field(default_factory=lambda: _env("GEMINI_MODEL", "gemini-2.5-flash"))
    anthropic_api_key: str = Field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    anthropic_model: str = Field(default_factory=lambda: _env("ANTHROPIC_MODEL", "claude-sonnet-5-5"))
    tavily_api_key: str = Field(default_factory=lambda: _env("TAVILY_API_KEY"))

    cors_origins: List[str] = Field(
        default_factory=lambda: [
            o.strip()
            for o in _env("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
            if o.strip()
        ]
    )


settings = Settings()
