from __future__ import annotations

from typing import Any

from backend.app.agents.base import BaseAgent


class ConflictAgent(BaseAgent):
    """PLACEHOLDER - owned by teammate.

    Contract: return {"detected_conflicts": [Conflict, ...]} (see workflows/state.py) and persist them
    with ConflictRepository so GET /reports/{id} (and the frontend ConflictList) can show them.
    """

    name = "conflict_agent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        return {"detected_conflicts": []}
