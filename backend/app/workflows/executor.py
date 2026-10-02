from __future__ import annotations

import json
from typing import Any

from backend.app.core.logging import get_logger
from backend.app.workflows.build import build_investigation_workflow
from backend.app.workflows.state import WorkflowState

logger = get_logger(__name__)


class WorkflowExecutor:
    """High-level executor for investigation workflows.

    This class is responsible for:
    - Building the workflow graph
    - Executing the workflow with initial state
    - Tracking execution progress
    - Logging and error handling
    """

    def __init__(self) -> None:
        self.graph = build_investigation_workflow()
        self.execution_log = []

    async def execute(
        self,
        input_text: str,
        input_type: str = "text",
        investigation_id: str | None = None,
    ) -> WorkflowState:
        """Execute a full investigation workflow.

        Args:
            input_text: The claim or input text to investigate
            input_type: Type of input (text, url, pdf, audio)
            investigation_id: Optional investigation ID for tracking

        Returns:
            Final workflow state containing all results
        """
        logger.info(f"Starting investigation workflow: {investigation_id}")

        initial_state: dict[str, Any] = {
            "investigation_id": investigation_id or "placeholder",
            "input_text": input_text,
            "input_type": input_type,
            "extracted_claims": [],
            "research_results": [],
            "sources": [],
            "evaluated_sources": [],
            "extracted_evidence": [],
            "verified_claims": [],
            "detected_conflicts": [],
            "independence_analysis": {},
            "evidence_graph": {},
            "final_verdict": None,
            "workflow_status": "running",
        }

        try:
            final_state = await self.graph.invoke(initial_state)
            final_state["workflow_status"] = "completed"
            logger.info(f"Workflow completed: {investigation_id}")
            return final_state
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            initial_state["workflow_status"] = "failed"
            initial_state["error"] = str(e)
            return WorkflowState(**initial_state)

    def log_execution_event(self, node_name: str, status: str, **metadata: Any) -> None:
        """Log a workflow execution event."""
        event = {
            "node": node_name,
            "status": status,
            "metadata": metadata,
        }
        self.execution_log.append(event)
        logger.info(f"Node executed: {node_name} ({status})")

    def get_execution_log(self) -> list[dict[str, Any]]:
        """Return the execution log for the workflow."""
        return self.execution_log
