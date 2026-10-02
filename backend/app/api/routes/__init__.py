from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.services.investigation_service import InvestigationService
from backend.app.workflows.executor import WorkflowExecutor

logger = get_logger(__name__)


class InvestigationWorkflowService:
    """Orchestrates investigation creation and workflow execution."""

    def __init__(self, investigation_service: InvestigationService | None = None) -> None:
        self.investigation_service = investigation_service or InvestigationService()
        self.executor = WorkflowExecutor()

    async def start_investigation(
        self,
        title: str,
        input_text: str,
        source_type: str = "text",
    ) -> dict[str, Any]:
        """Create a new investigation and execute the workflow."""
        logger.info(f"Starting investigation: {title}")

        investigation = await self.investigation_service.create_investigation(
            title=title,
            input_text=input_text,
            source_type=source_type,
        )
        investigation_id = investigation.get("id", "placeholder")

        await self.investigation_service.update_investigation_status(
            investigation_id,
            "running",
        )

        try:
            final_state = await self.executor.execute(
                input_text=input_text,
                input_type=source_type,
                investigation_id=investigation_id,
            )
            workflow_status = final_state.get("workflow_status", "completed")
            investigation["workflow_status"] = workflow_status
            investigation["final_verdict"] = final_state.get("final_verdict")
            await self.investigation_service.update_investigation_status(
                investigation_id,
                "completed",
                final_verdict=final_state.get("final_verdict"),
                workflow_status=workflow_status,
            )
        except Exception as exc:  # pragma: no cover - placeholder path
            logger.error(f"Workflow failed for investigation {investigation_id}: {exc}")
            investigation["workflow_status"] = "failed"
            investigation["error"] = str(exc)
            await self.investigation_service.update_investigation_status(
                investigation_id,
                "failed",
                error=str(exc),
            )

        return investigation

    async def get_investigation_status(self, investigation_id: str) -> dict[str, Any] | None:
        return await self.investigation_service.get_investigation(investigation_id)
