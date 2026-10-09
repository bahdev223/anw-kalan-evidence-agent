from __future__ import annotations

import pytest

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


def test_proposal_stays_proposed_without_human_grant(tmp_path):
    store = ChallengeStore(str(tmp_path / "test.sqlite3"))
    item = proposal()
    store.save_proposal(item)

    saved = store.get_proposal(item.id)
    assert saved.status == ProposalStatus.PROPOSED
    assert saved.requires_human_approval is True


def test_valid_human_grant_can_reject_proposal(tmp_path):
    store = ChallengeStore(str(tmp_path / "test.sqlite3"))
    item = proposal()
    store.save_proposal(item)

    approval_id = store.create_human_approval(
        item.id,
        HumanDecisionKind.REJECT,
        note="Teacher wants another diagnostic first.",
    )
    store.apply_human_approval(approval_id)

    saved = store.get_proposal(item.id)
    assert saved.status == ProposalStatus.REJECTED


def test_human_grant_is_one_time_only(tmp_path):
    store = ChallengeStore(str(tmp_path / "test.sqlite3"))
    item = proposal()
    store.save_proposal(item)

    approval_id = store.create_human_approval(
        item.id,
        HumanDecisionKind.ACCEPT,
    )
    store.apply_human_approval(approval_id)

    with pytest.raises(ValueError):
        store.apply_human_approval(approval_id)


def test_modify_requires_a_human_supplied_replacement(tmp_path):
    store = ChallengeStore(str(tmp_path / "test.sqlite3"))
    item = proposal()
    store.save_proposal(item)

    with pytest.raises(ValueError):
        store.create_human_approval(
            item.id,
            HumanDecisionKind.MODIFY,
            modified_action="",
        )
