from __future__ import annotations

from typing import Any


class InvestigationService:
    """Placeholder service for investigation orchestration.

    This will eventually coordinate workflow execution, persistence, and report generation.
    """

    async def create_investigation(self, title: str, input_text: str | None = None) -> dict[str, Any]:
        return {
            "id": "investigation_placeholder",
            "title": title,
            "input_text": input_text,
            "status": "draft",
        }

    async def get_investigation(self, investigation_id: str) -> dict[str, Any]:
        return {
            "id": investigation_id,
            "status": "not_implemented",
        }
