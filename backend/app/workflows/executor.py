from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger
from backend.app.workflows.build import build_investigation_workflow
from backend.app.workflows.graph import StageCallback

logger = get_logger(__name__)


class WorkflowExecutor:
    """Builds the graph once and runs investigations. Raises on failure (callers record the error)."""

    def __init__(self) -> None:
        self.graph = build_investigation_workflow()

    async def execute(
        self,
        input_text: str,
        input_type: str = "text",
        investigation_id: str | None = None,
        on_stage: StageCallback | None = None,
    ) -> dict[str, Any]:
        initial_state: dict[str, Any] = {
            "investigation_id": investigation_id or "",
            "input_text": input_text,
            "input_type": input_type,
            "extracted_claims": [],
            "research_results": [],
            "evaluated_sources": [],
            "extracted_evidence": [],
            "verified_claims": [],
            "detected_conflicts": [],
            "independence_analysis": {},
            "evidence_graph": {},
            "final_verdict": None,
            "workflow_status": "running",
            "error": None,
        }
        final_state = await self.graph.invoke(initial_state, on_stage=on_stage)
        final_state["workflow_status"] = "completed"
        logger.info("Workflow completed: %s", investigation_id)
        return final_state
