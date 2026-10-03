from __future__ import annotations

from backend.app.services.answer_service import summarize_evidence

SRC = [{"id": "s1", "quality_score": 0.85}, {"id": "s2", "quality_score": 0.6}]


def ev(stance, source="s1", rel=0.9, conf=0.9):
    return {"stance": stance, "source_id": source, "relevance_score": rel, "confidence": conf}


def test_supported_claim_is_true():
    v = summarize_evidence([ev("supporting"), ev("supporting", "s2")], SRC)
    assert v["label"] == "true" and v["confidence"] > 0.6 and "Most likely true" in v["explanation"]


def test_contradicted_claim_is_false():
    assert summarize_evidence([ev("contradicting"), ev("contradicting", "s2")], SRC)["label"] == "false"


def test_split_evidence_is_mixed_and_needs_review():
    v = summarize_evidence([ev("supporting"), ev("contradicting", "s2")], SRC)
    assert v["label"] == "mixed" and v["review_required"]


def test_neutral_only_is_unverified():
    v = summarize_evidence([ev("neutral")], SRC)
    assert v["label"] == "unverified" and "none clearly confirm" in v["explanation"]


def test_no_evidence_is_unverified():
    assert "No relevant sources" in summarize_evidence([], SRC)["explanation"]


def test_llm_failure_is_reported_not_disguised():
    v = summarize_evidence([ev("neutral")], SRC, llm_degraded=True)
    assert v["label"] == "unverified" and "unavailable" in v["explanation"]
