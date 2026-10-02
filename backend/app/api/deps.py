"""API dependency placeholders shared across routes."""

from __future__ import annotations


async def get_current_user() -> dict[str, str]:
    """Placeholder auth dependency for future user/session logic."""
    return {"user_id": "anonymous", "role": "guest"}
