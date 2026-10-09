from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .models import ActionProposal, EvidenceSummary, LearningState


class RecommendationEngine:
    """Maps deterministic evidence states to a narrow next-step proposal."""

    def propose(self, summary: EvidenceSummary) -> ActionProposal:
        actions = {
            LearningState.NOT_EVALUATED: (
                "Run a brief diagnostic without giving the final answer.",
                "There is not enough evidence to infer a learning need yet.",
            ),
            LearningState.FRAGILE: (
                "Consolidate the precise prerequisite, then ask for a short independent attempt.",
                "The learner has not yet demonstrated successful independent performance.",
            ),
            LearningState.ACQUIRING: (
                "Reduce assistance and require one independent production plus a short explanation.",
                "Progress is visible, but assisted success or limited independent evidence is not mastery.",
            ),
            LearningState.MASTERED: (
                "Offer a novel transfer problem, then schedule a delayed retention check.",
                "The current evidence supports mastery, but transfer over time still needs confirmation.",
            ),
            LearningState.ADVANCED: (
                "Offer a more complex transfer task and keep only spaced maintenance reviews.",
                "The learner has independent, explanatory, transfer and delayed-retention evidence.",
            ),
        }
        action, reason = actions[summary.state]
        return ActionProposal(
            id=str(uuid4()),
            learner_id=summary.learner_id,
            competency_id=summary.competency_id,
            action=action,
            rationale=f"{reason} Engine rationale: {summary.rationale}",
            evidence_ids=list(summary.evidence_ids),
            requires_human_approval=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
