from __future__ import annotations

from typing import Any, Awaitable, Callable

from backend.app.workflows.state import WorkflowState


class Node:
    """Represents a single node in the workflow graph."""

    def __init__(self, name: str, handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]) -> None:
        self.name = name
        self.handler = handler

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        return await self.handler(state)


class Edge:
    """Represents a connection between two nodes."""

    def __init__(self, from_node: str, to_node: str, condition: Callable[[dict[str, Any]], bool] | None = None) -> None:
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition or (lambda _: True)


class Graph:
    """Simple directed acyclic graph for workflow orchestration.

    This is a placeholder implementation that mimics LangGraph behavior.
    In production, this would be replaced with actual LangGraph StateGraph.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, list[Edge]] = {}
        self.entry_point: str | None = None

    def add_node(self, name: str, handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]) -> None:
        """Add a node to the graph."""
        self.nodes[name] = Node(name, handler)
        self.edges[name] = []

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an unconditional edge between nodes."""
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(Edge(from_node, to_node))

    def add_conditional_edge(
        self,
        from_node: str,
        to_node: str,
        condition: Callable[[dict[str, Any]], bool],
    ) -> None:
        """Add a conditional edge between nodes."""
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(Edge(from_node, to_node, condition))

    def set_entry_point(self, node_name: str) -> None:
        """Set the starting node for workflow execution."""
        self.entry_point = node_name

    async def invoke(self, initial_state: dict[str, Any]) -> WorkflowState:
        """Execute the workflow starting from the entry point.

        Args:
            initial_state: Initial workflow state

        Returns:
            Final workflow state after all nodes execute
        """
        state = WorkflowState(**initial_state)
        current_node = self.entry_point

        visited = set()
        max_iterations = 100
        iteration = 0

        while current_node and iteration < max_iterations:
            if current_node in visited:
                # Prevent infinite loops
                break

            visited.add(current_node)
            iteration += 1

            if current_node not in self.nodes:
                break

            node = self.nodes[current_node]
            state = WorkflowState(**await node.execute(dict(state)))

            # Find next node based on edges
            next_node = None
            if current_node in self.edges:
                for edge in self.edges[current_node]:
                    if edge.condition(dict(state)):
                        next_node = edge.to_node
                        break

            current_node = next_node

        return state
