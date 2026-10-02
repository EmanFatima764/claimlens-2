from __future__ import annotations

from typing import Any


class WorkflowState(dict):
    """State bag passed between workflow nodes."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


__all__ = ["WorkflowState"]
