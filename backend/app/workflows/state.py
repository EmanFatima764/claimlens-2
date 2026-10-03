"""Shared contract between ALL agents. Change keys here only after telling the other agent author.

Convention: every agent subclasses BaseAgent and implements `run(state) -> dict` returning ONLY the keys
it adds/changes; BaseAgent merges them into the state. See docs/AGENT_CONTRACT.md.
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class Claim(TypedDict, total=False):
    id: str                  # DB uuid
    text: str
    normalized_text: str
    claim_type: str          # statistical | event | attribution | scientific | financial | legal | other
    entities: list[str]
    confidence: float        # 0-1, how checkable the claim is


class ResearchResult(TypedDict, total=False):
    claim_id: str
    query: str
    url: str
    title: str
    content: str
    score: float             # Tavily relevance 0-1


class EvaluatedSource(TypedDict, total=False):
    id: str                  # DB uuid
    url: str
    title: str
    domain: str
    publisher: str
    source_type: str         # government | academic | news | reference | organization | social | other
    quality_score: float     # 0-1
    relevance_score: float   # 0-1
    content: str
    claim_ids: list[str]


class Evidence(TypedDict, total=False):
    id: str                  # DB uuid
    claim_id: str
    source_id: str
    source_url: str
    evidence_text: str
    stance: str              # supporting | contradicting | neutral
    relevance_score: float
    confidence: float


class Conflict(TypedDict, total=False):
    id: str
    evidence_a_id: str
    evidence_b_id: str
    conflict_type: str
    severity: float
    explanation: str


class Verdict(TypedDict, total=False):
    label: str               # true | mostly_true | mixed | mostly_false | false | unverified
    explanation: str
    confidence: float
    uncertainty: float
    evidence_strength: float
    review_required: bool


class WorkflowState(TypedDict, total=False):
    investigation_id: str
    input_text: str
    input_type: str
    extracted_claims: list[Claim]            # ClaimAgent
    research_results: list[ResearchResult]   # ResearchAgent
    evaluated_sources: list[EvaluatedSource]  # SourceAgent
    extracted_evidence: list[Evidence]       # EvidenceAgent
    verified_claims: list[dict[str, Any]]    # VerificationAgent
    detected_conflicts: list[Conflict]       # ConflictAgent
    independence_analysis: dict[str, Any]    # IndependenceAgent
    evidence_graph: dict[str, Any]
    final_verdict: Optional[Verdict]         # VerdictAgent
    llm_error: Optional[str]                 # EvidenceAgent: why the LLM failed (shown in the report)
    llm_degraded: bool                       # EvidenceAgent: True if the LLM stance analysis failed
    workflow_status: str
    current_stage: str
    error: Optional[str]


__all__ = [
    "WorkflowState", "Claim", "ResearchResult", "EvaluatedSource", "Evidence", "Conflict", "Verdict",
]