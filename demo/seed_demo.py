from __future__ import annotations

from pathlib import Path

from anw_kalan_evidence_agent.models import Evidence, EvidenceKind
from anw_kalan_evidence_agent.store import ChallengeStore


DB_PATH = Path("demo/challenge-demo.sqlite3")
LEARNER_ID = "learner-demo-001"
COMPETENCY_ID = "math.fractions.unlike-denominators"


EVIDENCE = [
    Evidence(
        id="ev-001",
        learner_id=LEARNER_ID,
        competency_id=COMPETENCY_ID,
        kind=EvidenceKind.GUIDED_ATTEMPT,
        score=0.90,
        assisted=True,
        occurred_at="2026-09-22T10:00:00Z",
        source="guided-practice-01",
        notes="Succeeded after two hints.",
    ),
    Evidence(
        id="ev-002",
        learner_id=LEARNER_ID,
        competency_id=COMPETENCY_ID,
        kind=EvidenceKind.INDEPENDENT_ATTEMPT,
        score=0.45,
        assisted=False,
        occurred_at="2026-09-22T10:20:00Z",
        source="independent-check-01",
        notes="Common-denominator step was incorrect.",
    ),
    Evidence(
        id="ev-003",
        learner_id=LEARNER_ID,
        competency_id=COMPETENCY_ID,
        kind=EvidenceKind.GUIDED_ATTEMPT,
        score=0.85,
        assisted=True,
        occurred_at="2026-09-24T08:30:00Z",
        source="guided-practice-02",
        notes="Used one targeted hint about equivalent fractions.",
    ),
    Evidence(
        id="ev-004",
        learner_id=LEARNER_ID,
        competency_id=COMPETENCY_ID,
        kind=EvidenceKind.INDEPENDENT_ATTEMPT,
        score=0.80,
        assisted=False,
        occurred_at="2026-09-24T09:00:00Z",
        source="independent-check-02",
        notes="Solved without hint.",
    ),
    Evidence(
        id="ev-005",
        learner_id=LEARNER_ID,
        competency_id=COMPETENCY_ID,
        kind=EvidenceKind.EXPLANATION,
        score=0.78,
        assisted=False,
        occurred_at="2026-09-24T09:10:00Z",
        source="learner-explanation-01",
        notes="Explained why a common denominator is needed.",
    ),
]


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    store = ChallengeStore(str(DB_PATH))
    for item in EVIDENCE:
        store.add_evidence(item)
    print(f"Seeded {len(EVIDENCE)} synthetic evidence items in {DB_PATH}")


if __name__ == "__main__":
    main()
