from __future__ import annotations

from typing import Any

from backend.app.agents.base import BaseAgent


class IndependenceAgent(BaseAgent):
    """PLACEHOLDER - owned by teammate.

    Contract: return {"independence_analysis": {...}} describing whether sources are independent
    or just republishing each other.
    """

    name = "independence_agent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        return {"independence_analysis": {}}
