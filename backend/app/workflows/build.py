from __future__ import annotations

from backend.app.agents.claim_agent.agent import ClaimAgent
from backend.app.agents.conflict_agent.agent import ConflictAgent
from backend.app.agents.evidence_agent.agent import EvidenceAgent
from backend.app.agents.independence_agent.agent import IndependenceAgent
from backend.app.agents.research_agent.agent import ResearchAgent
from backend.app.agents.source_agent.agent import SourceAgent
from backend.app.agents.verdict_agent.agent import VerdictAgent
from backend.app.agents.verification_agent.agent import VerificationAgent
from backend.app.core.logging import get_logger
from backend.app.workflows.graph import Graph

logger = get_logger(__name__)


def build_investigation_workflow() -> Graph:
    """Build the full 8-agent investigation pipeline.

    Execution order:
      claim_extraction
      → research
      → source_evaluation
      → evidence_extraction
      → verification          ← VerificationAgent: verifies each claim against collected evidence
      → conflict_detection
      → independence          ← IndependenceAgent: assesses whether sources are genuinely independent
      → verdict
    """
    graph = Graph()
    steps = [
        ("claim_extraction",    ClaimAgent()),
        ("research",            ResearchAgent(max_iterations=2, queries_per_round=2,
                                              results_per_query=5, min_results_per_claim=6)),
        ("source_evaluation",   SourceAgent()),
        ("evidence_extraction", EvidenceAgent()),
        ("verification",        VerificationAgent()),
        ("conflict_detection",  ConflictAgent()),
        ("independence",        IndependenceAgent()),
        ("verdict",             VerdictAgent()),
    ]
    for name, agent in steps:
        graph.add_node(name, agent.execute)
    for (a, _), (b, _) in zip(steps, steps[1:]):
        graph.add_edge(a, b)
    graph.set_entry_point(steps[0][0])
    logger.info(
        "Investigation workflow graph built: "
        "claim → research → source → evidence → verification → conflict → independence → verdict"
    )
    return graph
