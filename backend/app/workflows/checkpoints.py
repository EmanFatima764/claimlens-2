from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowStateCheckpoint:
    """Represents a saved checkpoint of workflow execution state."""

    def __init__(self, checkpoint_id: str, node_name: str, state: dict[str, Any]) -> None:
        self.checkpoint_id = checkpoint_id
        self.node_name = node_name
        self.state = state


class CheckpointManager:
    """Manages workflow checkpoints for recovery and debugging.

    In production, checkpoints would be persisted to a database or message queue.
    """

    def __init__(self) -> None:
        self.checkpoints: dict[str, WorkflowStateCheckpoint] = {}

    def save_checkpoint(self, checkpoint_id: str, node_name: str, state: dict[str, Any]) -> None:
        """Save a workflow state checkpoint."""
        checkpoint = WorkflowStateCheckpoint(checkpoint_id, node_name, state)
        self.checkpoints[checkpoint_id] = checkpoint
        logger.info(f"Checkpoint saved: {checkpoint_id} at node {node_name}")

    def load_checkpoint(self, checkpoint_id: str) -> WorkflowStateCheckpoint | None:
        """Retrieve a saved checkpoint."""
        return self.checkpoints.get(checkpoint_id)

    def list_checkpoints(self) -> list[WorkflowStateCheckpoint]:
        """List all saved checkpoints."""
        return list(self.checkpoints.values())
