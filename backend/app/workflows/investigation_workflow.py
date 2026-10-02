from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.services.investigation_service import InvestigationService
from backend.app.workflows.executor import WorkflowExecutor

logger = get_logger(__name__)


class InvestigationWorkflowService:
    """Orchestrates investigation execution and persistence.

    This service coordinates between:
    - API layer (receives requests)
    - Workflow executor (runs investigation)
    - Investigation service (persists results)
    """

    def __init__(self, investigation_service: InvestigationService | None = None) -> None:
        self.investigation_service = investigation_service or InvestigationService()
        self.executor = WorkflowExecutor()

    async def start_investigation(self, title: str, input_text: str) -> dict[str, Any]:
        """Create and start a new investigation.

        Args:
            title: Investigation title
            input_text: Claim or input text to investigate

        Returns:
            Investigation record with ID and status
        """
        # Create investigation record
        investigation = await self.investigation_service.create_investigation(
            title=title,
            input_text=input_text,
        )

        investigation_id = investigation.get("id", "placeholder")
        logger.info(f"Investigation created: {investigation_id}")

        # Execute workflow (placeholder - in production this would be async/queued)
        try:
            final_state = await self.executor.execute(
                input_text=input_text,
                investigation_id=investigation_id,
            )
            investigation["workflow_status"] = final_state.get("workflow_status")
            investigation["final_verdict"] = final_state.get("final_verdict")
        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            investigation["workflow_status"] = "failed"

        return investigation

    async def get_investigation_status(self, investigation_id: str) -> dict[str, Any]:
        """Fetch the current status of an investigation."""
        investigation = await self.investigation_service.get_investigation(investigation_id)
        return investigation
