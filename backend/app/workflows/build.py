from __future__ import annotations

from backend.app.agents.claim_agent.agent import ClaimAgent
from backend.app.agents.evidence_agent.agent import EvidenceAgent
from backend.app.agents.research_agent.agent import ResearchAgent
from backend.app.agents.source_agent.agent import SourceAgent
from backend.app.core.logging import get_logger
from backend.app.workflows.graph import Graph

logger = get_logger(__name__)


def build_investigation_workflow() -> Graph:
    """claim -> research -> source -> evidence.

    The "most likely answer" is derived from the extracted evidence right after this graph
    finishes (see services/answer_service.py). Verification, conflict detection, independence
    analysis and the full verdict agent belong to the next phase and are intentionally not wired in.
    """
    graph = Graph()
    steps = [
        ("claim_extraction", ClaimAgent()),
        ("research", ResearchAgent(max_iterations=2, queries_per_round=2, results_per_query=5, min_results_per_claim=6)),
        ("source_evaluation", SourceAgent()),
        ("evidence_extraction", EvidenceAgent()),
    ]
    for name, agent in steps:
        graph.add_node(name, agent.execute)
    for (a, _), (b, _) in zip(steps, steps[1:]):
        graph.add_edge(a, b)
    graph.set_entry_point(steps[0][0])
    logger.info("Investigation workflow graph built (claim -> research -> source -> evidence)")
    return graph
