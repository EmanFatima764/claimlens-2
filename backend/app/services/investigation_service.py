from __future__ import annotations

from typing import Any

from backend.app.core.constants import STAGE_GROUPS, STATUS_QUEUED
from backend.app.repos.investigation_repo import InvestigationRepository


class InvestigationService:
    """Service layer for investigation records."""

    def __init__(self, repo: InvestigationRepository | None = None) -> None:
        self.repo = repo or InvestigationRepository()

    @staticmethod
    def _decorate(inv: dict[str, Any] | None) -> dict[str, Any] | None:
        if inv is None:
            return None
        out = dict(inv)
        out["stage_group"] = STAGE_GROUPS.get(out.get("current_stage") or "", None)
        return out

    async def create_investigation(
        self, title: str, input_text: str | None = None, description: str | None = None, source_type: str = "text"
    ) -> dict[str, Any]:
        row = await self.repo.create(
            {
                "title": title, "description": description, "input_text": input_text,
                "source_type": source_type, "status": STATUS_QUEUED,
            }
        )
        return self._decorate(row)  # type: ignore[return-value]

    async def get_investigation(self, investigation_id: str) -> dict[str, Any] | None:
        return self._decorate(await self.repo.get_by_id(investigation_id))

    async def list_investigations(self, **filters: Any) -> list[dict[str, Any]]:
        return [self._decorate(r) for r in await self.repo.list(**filters)]  # type: ignore[misc]

    async def update_investigation_status(self, investigation_id: str, status: str, **updates: Any) -> dict[str, Any] | None:
        return self._decorate(await self.repo.update(investigation_id, {"status": status, **updates}))

    async def update_fields(self, investigation_id: str, **updates: Any) -> dict[str, Any] | None:
        return self._decorate(await self.repo.update(investigation_id, updates))
