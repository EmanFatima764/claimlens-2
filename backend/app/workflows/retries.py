from __future__ import annotations

from typing import Any

from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class RetryPolicy:
    """Defines retry behavior for workflow nodes."""

    def __init__(self, max_retries: int = 3, backoff_seconds: float = 1.0) -> None:
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds


class RetryHandler:
    """Handles retries for failed node executions."""

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self.policy = policy or RetryPolicy()
        self.retry_counts: dict[str, int] = {}

    async def execute_with_retry(
        self,
        node_name: str,
        handler: Any,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a node handler with automatic retries on failure.

        Args:
            node_name: Name of the node being executed
            handler: The async handler function
            state: Current workflow state

        Returns:
            Result state after successful execution or final retry
        """
        retry_count = 0
        last_error = None

        while retry_count < self.policy.max_retries:
            try:
                result = await handler(state)
                self.retry_counts[node_name] = 0
                return result
            except Exception as e:
                last_error = e
                retry_count += 1
                logger.warning(
                    f"Node {node_name} failed (attempt {retry_count}/{self.policy.max_retries}): {e}"
                )

        # All retries exhausted
        logger.error(f"Node {node_name} failed after {self.policy.max_retries} attempts")
        raise last_error or Exception(f"Node {node_name} failed after {self.policy.max_retries} attempts")
