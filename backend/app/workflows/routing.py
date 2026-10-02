"""Utilities for workflow state management and transitions."""

from __future__ import annotations

from typing import Any


def is_research_complete(state: dict[str, Any]) -> bool:
    """Check if research phase has collected sufficient evidence."""
    research_results = state.get("research_results", [])
    return len(research_results) > 0


def should_continue_research(state: dict[str, Any]) -> bool:
    """Determine if more research iterations are needed."""
    max_iterations = state.get("research_max_iterations", 3)
    current_iteration = state.get("research_iteration", 0)
    return current_iteration < max_iterations


def has_sufficient_evidence(state: dict[str, Any]) -> bool:
    """Check if we have enough evidence for a verdict."""
    evidence_count = len(state.get("extracted_evidence", []))
    return evidence_count > 0


def should_recommend_more_research(state: dict[str, Any]) -> bool:
    """Determine if the final verdict should recommend more research."""
    uncertainty = state.get("uncertainty_estimate", 0.5)
    return uncertainty > 0.6
