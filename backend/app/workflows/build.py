from __future__ import annotations

import json
from typing import Any

from backend.app.agents.claim_agent.agent import ClaimAgent
from backend.app.agents.conflict_agent.agent import ConflictAgent
from backend.app.agents.evidence_agent.agent import EvidenceAgent
from backend.app.agents.independence_agent.agent import IndependenceAgent
from backend.app.agents.research_agent.agent import ResearchAgent
from backend.app.agents.source_agent.agent import SourceAgent
from backend.app.agents.verification_agent.agent import VerificationAgent
from backend.app.agents.verdict_agent.agent import VerdictAgent
from backend.app.core.logging import get_logger
from backend.app.workflows.graph import Graph

logger = get_logger(__name__)


def build_investigation_workflow() -> Graph:
    """Build the investigation workflow graph.

    Constructs a directed graph that chains agents in the following order:

    1. ClaimAgent: Extract and normalize claims from input
    2. ResearchAgent: Search for evidence sources
    3. SourceAgent: Evaluate source credibility
    4. EvidenceAgent: Extract evidence from sources
    5. VerificationAgent: Verify claims against evidence
    6. ConflictAgent: Detect conflicts between evidence
    7. IndependenceAgent: Analyze source independence
    8. VerdictAgent: Generate final verdict

    Returns:
        Compiled Graph ready for execution
    """
    graph = Graph()

    # Initialize agents
    claim_agent = ClaimAgent()
    research_agent = ResearchAgent(max_iterations=3)
    source_agent = SourceAgent()
    evidence_agent = EvidenceAgent()
    verification_agent = VerificationAgent()
    conflict_agent = ConflictAgent()
    independence_agent = IndependenceAgent()
    verdict_agent = VerdictAgent()

    # Add nodes to graph
    graph.add_node("claim_extraction", claim_agent.execute)
    graph.add_node("research", research_agent.execute)
    graph.add_node("source_evaluation", source_agent.execute)
    graph.add_node("evidence_extraction", evidence_agent.execute)
    graph.add_node("verification", verification_agent.execute)
    graph.add_node("conflict_detection", conflict_agent.execute)
    graph.add_node("independence_analysis", independence_agent.execute)
    graph.add_node("verdict_generation", verdict_agent.execute)

    # Add edges connecting nodes in sequence
    graph.add_edge("claim_extraction", "research")
    graph.add_edge("research", "source_evaluation")
    graph.add_edge("source_evaluation", "evidence_extraction")
    graph.add_edge("evidence_extraction", "verification")
    graph.add_edge("verification", "conflict_detection")
    graph.add_edge("conflict_detection", "independence_analysis")
    graph.add_edge("independence_analysis", "verdict_generation")

    # Set entry point
    graph.set_entry_point("claim_extraction")

    logger.info("Investigation workflow graph built successfully")
    return graph
