from __future__ import annotations

from typing import Any

from backend.app.repos.investigation_repo import InvestigationRepository


class InvestigationService:
    """Service layer for investigation operations."""

    def __init__(self, repo: InvestigationRepository | None = None) -> None:
        self.repo = repo or InvestigationRepository()

    async def create_investigation(
        self,
        title: str,
        input_text: str | None = None,
        description: str | None = None,
        source_type: str = "text",
    ) -> dict[str, Any]:
        payload = {
            "title": title,
            "description": description,
            "input_text": input_text,
            "source_type": source_type,
            "status": "draft",
        }
        investigation = await self.repo.create(payload)
        return investigation

    async def get_investigation(self, investigation_id: str) -> dict[str, Any] | None:
        return await self.repo.get_by_id(investigation_id)

    async def list_investigations(self, **filters: Any) -> list[dict[str, Any]]:
        return await self.repo.list(**filters)

    async def update_investigation_status(
        self,
        investigation_id: str,
        status: str,
        **updates: Any,
    ) -> dict[str, Any] | None:
        investigation = await self.get_investigation(investigation_id)
        if not investigation:
            return None
        investigation["status"] = status
        investigation.update(updates)
        return investigation
