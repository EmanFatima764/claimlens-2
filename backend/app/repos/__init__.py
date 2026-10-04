"""Repository package for the backend persistence layer."""

from backend.app.repos.base import BaseRepository
from backend.app.repos.claim_repo import ClaimRepository
from backend.app.repos.conflict_repo import ConflictRepository
from backend.app.repos.evidence_repo import EvidenceRepository
from backend.app.repos.independence_repo import IndependenceRepository
from backend.app.repos.investigation_repo import InvestigationRepository
from backend.app.repos.source_repo import SourceRepository
from backend.app.repos.verdict_repo import VerdictRepository
from backend.app.repos.verification_repo import VerificationRepository

__all__ = [
    "BaseRepository", "InvestigationRepository", "ClaimRepository", "SourceRepository",
    "EvidenceRepository", "ConflictRepository", "VerdictRepository",
    "VerificationRepository", "IndependenceRepository",
]
