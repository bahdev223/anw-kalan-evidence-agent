from __future__ import annotations

import json
import os

from anw_kalan_evidence_agent.evidence_engine import EvidenceEngine
from anw_kalan_evidence_agent.open_weights import OpenWeightsVerbalizer
from anw_kalan_evidence_agent.recommendation_engine import RecommendationEngine
from anw_kalan_evidence_agent.store import ChallengeStore


DB_PATH = os.getenv("EVIDENCE_DB_PATH", "demo/challenge-demo.sqlite3")
LEARNER_ID = "learner-demo-001"
COMPETENCY_ID = "math.fractions.unlike-denominators"


def main() -> None:
    store = ChallengeStore(DB_PATH)
    engine = EvidenceEngine()
    recommender = RecommendationEngine()
    verbalizer = OpenWeightsVerbalizer()

    evidence = store.list_evidence(LEARNER_ID, COMPETENCY_ID)
    summary = engine.analyze(LEARNER_ID, COMPETENCY_ID, evidence)
    proposal = recommender.propose(summary)
    store.save_proposal(proposal)
    explanation = verbalizer.verbalize(summary, proposal)

    result = {
        "summary": summary.to_dict(),
        "proposal": proposal.to_dict(),
        "verbalization": explanation,
        "next_step": (
            "Teacher must explicitly accept, modify, or reject the proposal. "
            "The agent cannot self-approve."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
