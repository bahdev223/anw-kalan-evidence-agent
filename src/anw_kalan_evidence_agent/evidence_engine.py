from __future__ import annotations

from .models import Evidence, EvidenceKind, EvidenceSummary, LearningState


SUCCESS_THRESHOLD = 0.70


class EvidenceEngine:
    """Deterministic advisory analysis.

    The engine deliberately treats assisted success differently from independent
    evidence. It produces an advisory state for the challenge demo; it does not
    write an official learner label.
    """

    def analyze(
        self,
        learner_id: str,
        competency_id: str,
        evidence: list[Evidence],
    ) -> EvidenceSummary:
        relevant = sorted(
            [
                item
                for item in evidence
                if item.learner_id == learner_id
                and item.competency_id == competency_id
            ],
            key=lambda item: (item.occurred_at, item.id),
        )

        if not relevant:
            return EvidenceSummary(
                learner_id=learner_id,
                competency_id=competency_id,
                state=LearningState.NOT_EVALUATED,
                rationale="No evidence exists yet. A brief diagnostic is needed before making a learning claim.",
                evidence_ids=[],
                counts=self._empty_counts(),
            )

        successes = [item for item in relevant if item.score >= SUCCESS_THRESHOLD]
        assisted_successes = [
            item for item in successes if item.assisted
        ]
        independent_attempt_successes = [
            item
            for item in successes
            if not item.assisted
            and item.kind in {
                EvidenceKind.INDEPENDENT_ATTEMPT,
                EvidenceKind.ARTIFACT,
            }
        ]
        independent_attempt_failures = [
            item
            for item in relevant
            if not item.assisted
            and item.kind in {
                EvidenceKind.INDEPENDENT_ATTEMPT,
                EvidenceKind.ARTIFACT,
            }
            and item.score < SUCCESS_THRESHOLD
        ]
        explanation_successes = [
            item
            for item in successes
            if not item.assisted and item.kind == EvidenceKind.EXPLANATION
        ]
        transfer_successes = [
            item
            for item in successes
            if not item.assisted and item.kind == EvidenceKind.TRANSFER
        ]
        delayed_successes = [
            item
            for item in successes
            if not item.assisted and item.kind == EvidenceKind.DELAYED_REVIEW
        ]

        counts = {
            "total": len(relevant),
            "assisted_successes": len(assisted_successes),
            "independent_successes": len(independent_attempt_successes),
            "independent_failures": len(independent_attempt_failures),
            "explanation_successes": len(explanation_successes),
            "transfer_successes": len(transfer_successes),
            "delayed_review_successes": len(delayed_successes),
        }

        mastery_evidence = (
            len(independent_attempt_successes) >= 2
            and bool(explanation_successes)
            and bool(transfer_successes)
        )

        if mastery_evidence and delayed_successes:
            state = LearningState.ADVANCED
            rationale = (
                "Independent performance is repeated, the learner can explain and transfer the skill, "
                "and a later review shows retention."
            )
        elif mastery_evidence:
            state = LearningState.MASTERED
            rationale = (
                "The learner has repeated independent success plus successful explanation and transfer. "
                "A later retention check is still needed before calling the evidence advanced."
            )
        elif independent_attempt_successes:
            state = LearningState.ACQUIRING
            rationale = (
                "There is independent success, but the evidence is not yet complete enough for mastery. "
                "The next step should reduce assistance and require explanation or transfer."
            )
        elif assisted_successes:
            state = LearningState.ACQUIRING
            rationale = (
                "Success exists only with assistance. This is progress, not mastery. "
                "An independent attempt is required."
            )
        else:
            state = LearningState.FRAGILE
            rationale = (
                "The available evidence does not yet contain a successful independent performance. "
                "Consolidation and a new independent check are needed."
            )

        return EvidenceSummary(
            learner_id=learner_id,
            competency_id=competency_id,
            state=state,
            rationale=rationale,
            evidence_ids=[item.id for item in relevant],
            counts=counts,
        )

    @staticmethod
    def _empty_counts() -> dict[str, int]:
        return {
            "total": 0,
            "assisted_successes": 0,
            "independent_successes": 0,
            "independent_failures": 0,
            "explanation_successes": 0,
            "transfer_successes": 0,
            "delayed_review_successes": 0,
        }
