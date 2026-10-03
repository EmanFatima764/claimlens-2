from __future__ import annotations

from typing import Any, Awaitable, Callable

from backend.app.core.exceptions import ClaimLensError
from backend.app.core.logging import get_logger

logger = get_logger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
StageCallback = Callable[[str, dict[str, Any]], Awaitable[None]]


class Node:
    def __init__(self, name: str, handler: Handler) -> None:
        self.name = name
        self.handler = handler

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        return await self.handler(state)


class Edge:
    def __init__(self, from_node: str, to_node: str, condition: Callable[[dict[str, Any]], bool] | None = None) -> None:
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition or (lambda _: True)


class Graph:
    """Minimal sequential graph runner (first matching edge wins). Errors propagate to the caller."""

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, list[Edge]] = {}
        self.entry_point: str | None = None

    def add_node(self, name: str, handler: Handler) -> None:
        self.nodes[name] = Node(name, handler)
        self.edges.setdefault(name, [])

    def add_edge(self, from_node: str, to_node: str) -> None:
        self.edges.setdefault(from_node, []).append(Edge(from_node, to_node))

    def add_conditional_edge(self, from_node: str, to_node: str, condition: Callable[[dict[str, Any]], bool]) -> None:
        self.edges.setdefault(from_node, []).append(Edge(from_node, to_node, condition))

    def set_entry_point(self, node_name: str) -> None:
        self.entry_point = node_name

    async def invoke(self, initial_state: dict[str, Any], on_stage: StageCallback | None = None) -> dict[str, Any]:
        state: dict[str, Any] = dict(initial_state)
        current = self.entry_point
        visited: set[str] = set()
        while current:
            if current not in self.nodes:
                raise ClaimLensError(f"Unknown workflow node '{current}'", code="workflow_bad_node")
            if current in visited:
                raise ClaimLensError(f"Cycle detected at node '{current}'", code="workflow_cycle")
            visited.add(current)
            state["current_stage"] = current
            if on_stage:
                await on_stage(current, state)
            logger.info("Running node: %s", current)
            state = await self.nodes[current].execute(state)
            current = next((e.to_node for e in self.edges.get(current, []) if e.condition(state)), None)
        return state
