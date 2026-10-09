from __future__ import annotations

from anw_kalan_evidence_agent.models import (
    ActionProposal,
    HumanDecisionKind,
    ProposalStatus,
)
from anw_kalan_evidence_agent.store import ChallengeStore


def proposal() -> ActionProposal:
    return ActionProposal(
        id="proposal-1",
        learner_id="learner",
        competency_id="competency",
        action="Ask for one independent production.",
        rationale="Assisted success is not mastery.",
        evidence_ids=["e1"],
        requires_human_approval=True,
        created_at="2026-10-09T12:00:00Z",
    )


def test_proposal_stays_proposed_until_human_decides(tmp_path):
    store = ChallengeStore(str(tmp_path / "test.sqlite3"))
    item = proposal()
    store.save_proposal(item)

    saved = store.get_proposal(item.id)
    assert saved.status == ProposalStatus.PROPOSED
    assert saved.requires_human_approval is True


def test_teacher_can_reject_proposal(tmp_path):
    store = ChallengeStore(str(tmp_path / "test.sqlite3"))
    item = proposal()
    store.save_proposal(item)

    store.record_teacher_decision(
        item.id,
        HumanDecisionKind.REJECT,
        note="Teacher wants another diagnostic first.",
    )

    saved = store.get_proposal(item.id)
    assert saved.status == ProposalStatus.REJECTED
