from __future__ import annotations

APP_NAME = "ClaimLens 2.0"
DEFAULT_TIMEOUT_SECONDS = 30

STATUS_DRAFT = "draft"
STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Pipeline node names, in execution order (also used for progress reporting).
NODE_ORDER = [
    "claim_extraction",
    "research",
    "source_evaluation",
    "evidence_extraction",
    "verification",          # VerificationAgent: verify claims against evidence
    "conflict_detection",
    "independence",          # IndependenceAgent: assess source independence
    "verdict",
]

# Maps pipeline nodes to the stages shown in the frontend progress tracker.
STAGE_GROUPS = {
    "claim_extraction": "claim",
    "research": "research",
    "source_evaluation": "sources",
    "evidence_extraction": "evidence",
    "verification": "verification",
    "conflict_detection": "conflicts",
    "independence": "independence",
    "verdict": "verdict",
    "done": "done",
}

VERDICT_LABELS = ["true", "mostly_true", "mixed", "mostly_false", "false", "unverified"]
STANCES = ["supporting", "contradicting", "neutral"]
CONFLICT_TYPES = {
    "numerical_discrepancy", "temporal_discrepancy", "factual_contradiction",
    "attribution_conflict", "scope_mismatch", "stance_conflict", "other",
}
