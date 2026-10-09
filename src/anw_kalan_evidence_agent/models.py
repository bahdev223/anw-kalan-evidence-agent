from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class EvidenceKind(StrEnum):
    GUIDED_ATTEMPT = "guided_attempt"
    INDEPENDENT_ATTEMPT = "independent_attempt"
    EXPLANATION = "explanation"
    TRANSFER = "transfer"
    DELAYED_REVIEW = "delayed_review"
    ARTIFACT = "artifact"


class LearningState(StrEnum):
    NOT_EVALUATED = "not_evaluated"
    FRAGILE = "fragile"
    ACQUIRING = "acquiring"
    MASTERED = "mastered"
    ADVANCED = "advanced"


class ProposalStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    MODIFIED = "modified"
    REJECTED = "rejected"


class HumanDecisionKind(StrEnum):
    ACCEPT = "accept"
    MODIFY = "modify"
    REJECT = "reject"


@dataclass(frozen=True)
class Evidence:
    id: str
    learner_id: str
    competency_id: str
    kind: EvidenceKind
    score: float
    assisted: bool
    occurred_at: str
    source: str
    notes: str = ""

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 1:
            raise ValueError("Evidence score must be between 0 and 1.")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class EvidenceSummary:
    learner_id: str
    competency_id: str
    state: LearningState
    rationale: str
    evidence_ids: list[str]
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


@dataclass(frozen=True)
class ActionProposal:
    id: str
    learner_id: str
    competency_id: str
    action: str
    rationale: str
    evidence_ids: list[str]
    requires_human_approval: bool = True
    status: ProposalStatus = ProposalStatus.PROPOSED
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class HumanDecision:
    id: str
    proposal_id: str
    decision: HumanDecisionKind
    note: str
    modified_action: str
    decided_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["decision"] = self.decision.value
        return data
