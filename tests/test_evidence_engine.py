from __future__ import annotations

from anw_kalan_evidence_agent.evidence_engine import EvidenceEngine
from anw_kalan_evidence_agent.models import Evidence, EvidenceKind, LearningState


LEARNER = "learner"
COMPETENCY = "competency"


def ev(
    identifier: str,
    kind: EvidenceKind,
    score: float,
    assisted: bool = False,
) -> Evidence:
    return Evidence(
        id=identifier,
        learner_id=LEARNER,
        competency_id=COMPETENCY,
        kind=kind,
        score=score,
        assisted=assisted,
        occurred_at=f"2026-10-09T10:{identifier[-1]}0:00Z",
        source=f"fixture-{identifier}",
    )


def analyze(items: list[Evidence]):
    return EvidenceEngine().analyze(LEARNER, COMPETENCY, items)


def test_no_evidence_is_not_evaluated():
    assert analyze([]).state == LearningState.NOT_EVALUATED


def test_assisted_success_is_not_mastery():
    result = analyze([
        ev("e1", EvidenceKind.GUIDED_ATTEMPT, 0.95, assisted=True),
    ])
    assert result.state == LearningState.ACQUIRING
    assert result.state != LearningState.MASTERED


def test_repeated_independent_failure_is_fragile():
    result = analyze([
        ev("e1", EvidenceKind.INDEPENDENT_ATTEMPT, 0.40),
        ev("e2", EvidenceKind.INDEPENDENT_ATTEMPT, 0.50),
    ])
    assert result.state == LearningState.FRAGILE


def test_first_independent_success_is_acquiring():
    result = analyze([
        ev("e1", EvidenceKind.GUIDED_ATTEMPT, 0.90, assisted=True),
        ev("e2", EvidenceKind.INDEPENDENT_ATTEMPT, 0.80),
    ])
    assert result.state == LearningState.ACQUIRING


def test_mastery_requires_independence_explanation_and_transfer():
    result = analyze([
        ev("e1", EvidenceKind.INDEPENDENT_ATTEMPT, 0.80),
        ev("e2", EvidenceKind.ARTIFACT, 0.85),
        ev("e3", EvidenceKind.EXPLANATION, 0.80),
        ev("e4", EvidenceKind.TRANSFER, 0.75),
    ])
    assert result.state == LearningState.MASTERED


def test_advanced_requires_delayed_retention():
    result = analyze([
        ev("e1", EvidenceKind.INDEPENDENT_ATTEMPT, 0.80),
        ev("e2", EvidenceKind.ARTIFACT, 0.85),
        ev("e3", EvidenceKind.EXPLANATION, 0.80),
        ev("e4", EvidenceKind.TRANSFER, 0.75),
        ev("e5", EvidenceKind.DELAYED_REVIEW, 0.80),
    ])
    assert result.state == LearningState.ADVANCED
