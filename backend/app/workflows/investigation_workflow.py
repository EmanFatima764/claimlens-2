from __future__ import annotations

from typing import Any

from backend.app.core.constants import (
    STATUS_COMPLETED, STATUS_FAILED, STATUS_RUNNING,
)
from backend.app.core.logging import get_logger
from backend.app.repos import (
    ClaimRepository, ConflictRepository, EvidenceRepository, SourceRepository, VerdictRepository,
)
from backend.app.services.answer_service import summarize_evidence
from backend.app.services.investigation_service import InvestigationService
from backend.app.workflows.executor import WorkflowExecutor

logger = get_logger(__name__)


class InvestigationWorkflowService:
    """Creates investigations and runs the agent pipeline (meant to be called from a background task)."""

    def __init__(self, investigation_service: InvestigationService | None = None, executor: WorkflowExecutor | None = None) -> None:
        self.investigation_service = investigation_service or InvestigationService()
        self._executor = executor

    @property
    def executor(self) -> WorkflowExecutor:
        if self._executor is None:
            self._executor = WorkflowExecutor()
        return self._executor

    async def create(self, title: str, input_text: str, source_type: str = "text", description: str | None = None) -> dict[str, Any]:
        return await self.investigation_service.create_investigation(
            title=title, input_text=input_text, description=description, source_type=source_type
        )

    async def _clear_previous_results(self, investigation_id: str) -> None:
        for repo in (ClaimRepository(), SourceRepository(), EvidenceRepository(), ConflictRepository(), VerdictRepository()):
            await repo.delete_by_investigation(investigation_id)

    async def run_workflow(self, investigation_id: str) -> None:
        """Run the pipeline for a stored investigation. Never raises - failures are saved on the record."""
        svc = self.investigation_service
        inv = await svc.get_investigation(investigation_id)
        if not inv:
            logger.error("run_workflow: investigation %s not found", investigation_id)
            return

        async def on_stage(node: str, _state: dict[str, Any]) -> None:
            try:
                await svc.update_fields(investigation_id, current_stage=node)
            except Exception as exc:  # progress is best-effort (e.g. migration 002 not applied)
                logger.warning("Could not save stage %s: %s", node, exc)

        try:
            await self._clear_previous_results(investigation_id)
            await svc.update_investigation_status(
                investigation_id, STATUS_RUNNING, workflow_status="running", error=None, final_verdict=None
            )
            final = await self.executor.execute(
                input_text=inv.get("input_text") or inv.get("title") or "",
                input_type=inv.get("source_type") or "text",
                investigation_id=investigation_id,
                on_stage=on_stage,
            )
            # The VerdictAgent already saved the verdict; only fall back if it somehow returned nothing.
            if not final.get("final_verdict"):
                answer = summarize_evidence(
                    final.get("extracted_evidence", []), final.get("evaluated_sources", []),
                    llm_degraded=bool(final.get("llm_degraded")),
                )
                await VerdictRepository().save_for_investigation({"investigation_id": investigation_id, **answer})
                final["final_verdict"] = answer
            await svc.update_investigation_status(
                investigation_id, STATUS_COMPLETED, workflow_status="completed",
                final_verdict=final.get("final_verdict"), current_stage="done",
            )
        except Exception as exc:
            logger.exception("Workflow failed for investigation %s", investigation_id)
            await svc.update_investigation_status(
                investigation_id, STATUS_FAILED, workflow_status="failed", error=str(exc)[:1000]
            )
