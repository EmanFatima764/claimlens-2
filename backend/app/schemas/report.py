from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.investigation import InvestigationRead


class _Loose(BaseModel):
    model_config = ConfigDict(extra="ignore")


class ClaimOut(_Loose):
    id: str
    text: str
    normalized_text: Optional[str] = None
    claim_type: Optional[str] = None
    entities: list[Any] = Field(default_factory=list)
    confidence: Optional[float] = None


class SourceOut(_Loose):
    id: str
    title: Optional[str] = None
    url: Optional[str] = None
    publisher: Optional[str] = None
    domain: Optional[str] = None
    source_type: Optional[str] = None
    quality_score: Optional[float] = None
    relevance_score: Optional[float] = None


class EvidenceOut(_Loose):
    id: str
    claim_id: Optional[str] = None
    source_id: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    evidence_text: str
    stance: str = "neutral"  # supporting | contradicting | neutral
    relevance_score: Optional[float] = None
    confidence: Optional[float] = None


class ConflictOut(_Loose):
    id: str
    evidence_a_id: Optional[str] = None
    evidence_b_id: Optional[str] = None
    conflict_type: Optional[str] = None
    severity: Optional[float] = None
    explanation: Optional[str] = None


class VerdictOut(_Loose):
    label: Optional[str] = None  # true | mostly_true | mixed | mostly_false | false | unverified
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    uncertainty: Optional[float] = None
    evidence_strength: Optional[float] = None
    review_required: bool = False


class VerifiedClaimOut(BaseModel):
    """Per-claim result from VerificationAgent — stored in verified_claims table."""
    id: Optional[str] = None
    claim_id: Optional[str] = None
    verification_status: str = "insufficient_evidence"
    confidence: float = 0.0
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    reasoning: str = ""
    unresolved_issues: list[str] = Field(default_factory=list)
    llm_fallback: bool = False


class SourceGroupOut(BaseModel):
    """One origin group returned by IndependenceAgent."""
    group_id: int = 0
    source_ids: list[str] = Field(default_factory=list)
    source_domains: list[str] = Field(default_factory=list)
    origin_description: str = ""
    is_independent_origin: bool = True


class SourceRelationshipOut(BaseModel):
    """Pairwise source relationship returned by IndependenceAgent."""
    source_id_a: str = ""
    source_id_b: str = ""
    domain_a: str = ""
    domain_b: str = ""
    relationship: str = "unclear"
    explanation: str = ""


class IndependenceAnalysisOut(BaseModel):
    """Full analysis from IndependenceAgent — stored in independence_analysis table."""
    id: Optional[str] = None
    independent_source_count: int = 0
    total_source_count: int = 0
    independence_ratio: float = 0.0
    source_groups: list[SourceGroupOut] = Field(default_factory=list)
    relationships: list[SourceRelationshipOut] = Field(default_factory=list)
    overall_independence: str = "unknown"  # high | medium | low | unknown
    explanation: str = ""
    llm_fallback: bool = False


class ReportRead(_Loose):
    investigation: InvestigationRead
    claims: list[ClaimOut] = Field(default_factory=list)
    sources: list[SourceOut] = Field(default_factory=list)
    evidence: list[EvidenceOut] = Field(default_factory=list)
    conflicts: list[ConflictOut] = Field(default_factory=list)
    verdict: Optional[VerdictOut] = None
    # New: from VerificationAgent + IndependenceAgent
    verified_claims: list[VerifiedClaimOut] = Field(default_factory=list)
    independence_analysis: Optional[IndependenceAnalysisOut] = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
