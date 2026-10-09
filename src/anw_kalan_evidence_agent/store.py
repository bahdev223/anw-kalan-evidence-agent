from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import (
    ActionProposal,
    Evidence,
    EvidenceKind,
    HumanDecision,
    HumanDecisionKind,
    ProposalStatus,
)


class ChallengeStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or os.getenv("EVIDENCE_DB_PATH", "challenge.sqlite3"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS evidence (
                    id TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    competency_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    score REAL NOT NULL,
                    assisted INTEGER NOT NULL,
                    occurred_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    competency_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    evidence_ids TEXT NOT NULL,
                    requires_human_approval INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS human_approval_grants (
                    id TEXT PRIMARY KEY,
                    proposal_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    note TEXT NOT NULL,
                    modified_action TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    consumed_at TEXT,
                    FOREIGN KEY(proposal_id) REFERENCES proposals(id)
                );

                CREATE TABLE IF NOT EXISTS teacher_decisions (
                    id TEXT PRIMARY KEY,
                    proposal_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    note TEXT NOT NULL,
                    modified_action TEXT NOT NULL,
                    decided_at TEXT NOT NULL,
                    FOREIGN KEY(proposal_id) REFERENCES proposals(id)
                );

                CREATE TABLE IF NOT EXISTS tool_calls (
                    id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    output_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def add_evidence(self, item: Evidence) -> None:
        with self._connect() as db:
            db.execute(
                """
                INSERT OR REPLACE INTO evidence
                (id, learner_id, competency_id, kind, score, assisted, occurred_at, source, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.learner_id,
                    item.competency_id,
                    item.kind.value,
                    item.score,
                    int(item.assisted),
                    item.occurred_at,
                    item.source,
                    item.notes,
                ),
            )

    def list_evidence(
        self,
        learner_id: str,
        competency_id: str | None = None,
    ) -> list[Evidence]:
        query = "SELECT * FROM evidence WHERE learner_id = ?"
        params: list[object] = [learner_id]
        if competency_id:
            query += " AND competency_id = ?"
            params.append(competency_id)
        query += " ORDER BY occurred_at, id"

        with self._connect() as db:
            rows = db.execute(query, params).fetchall()

        return [
            Evidence(
                id=row["id"],
                learner_id=row["learner_id"],
                competency_id=row["competency_id"],
                kind=EvidenceKind(row["kind"]),
                score=float(row["score"]),
                assisted=bool(row["assisted"]),
                occurred_at=row["occurred_at"],
                source=row["source"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def save_proposal(self, proposal: ActionProposal) -> None:
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO proposals
                (id, learner_id, competency_id, action, rationale, evidence_ids,
                 requires_human_approval, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal.id,
                    proposal.learner_id,
                    proposal.competency_id,
                    proposal.action,
                    proposal.rationale,
                    json.dumps(proposal.evidence_ids),
                    int(proposal.requires_human_approval),
                    proposal.status.value,
                    proposal.created_at,
                ),
            )

    def get_proposal(self, proposal_id: str) -> ActionProposal:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM proposals WHERE id = ?", (proposal_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown proposal: {proposal_id}")
        return self._proposal_from_row(row)

    @staticmethod
    def _proposal_from_row(row: sqlite3.Row) -> ActionProposal:
        return ActionProposal(
            id=row["id"],
            learner_id=row["learner_id"],
            competency_id=row["competency_id"],
            action=row["action"],
            rationale=row["rationale"],
            evidence_ids=json.loads(row["evidence_ids"]),
            requires_human_approval=bool(row["requires_human_approval"]),
            status=ProposalStatus(row["status"]),
            created_at=row["created_at"],
        )

    def create_human_approval(
        self,
        proposal_id: str,
        decision: HumanDecisionKind,
        note: str = "",
        modified_action: str = "",
    ) -> str:
        """Human/UI boundary. This method is intentionally NOT an MCP tool."""

        proposal = self.get_proposal(proposal_id)
        if proposal.status != ProposalStatus.PROPOSED:
            raise ValueError("This proposal has already received a human decision.")
        if decision == HumanDecisionKind.MODIFY and not modified_action.strip():
            raise ValueError("A modified action is required when decision=modify.")

        approval_id = str(uuid4())
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO human_approval_grants
                (id, proposal_id, decision, note, modified_action, issued_at, consumed_at)
                VALUES (?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    approval_id,
                    proposal_id,
                    decision.value,
                    note.strip(),
                    modified_action.strip(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return approval_id

    def apply_human_approval(self, approval_id: str) -> HumanDecision:
        """Consume a one-time grant previously created by a human/UI action."""

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            grant = db.execute(
                "SELECT * FROM human_approval_grants WHERE id = ?",
                (approval_id,),
            ).fetchone()
            if grant is None:
                raise KeyError("Unknown human approval grant.")
            if grant["consumed_at"]:
                raise ValueError("This human approval grant has already been consumed.")

            proposal_row = db.execute(
                "SELECT * FROM proposals WHERE id = ?",
                (grant["proposal_id"],),
            ).fetchone()
            if proposal_row is None:
                raise KeyError("The proposal attached to this approval no longer exists.")
            proposal = self._proposal_from_row(proposal_row)
            if proposal.status != ProposalStatus.PROPOSED:
                raise ValueError("This proposal is no longer awaiting a human decision.")

            decision = HumanDecisionKind(grant["decision"])
            next_status = {
                HumanDecisionKind.ACCEPT: ProposalStatus.ACCEPTED,
                HumanDecisionKind.MODIFY: ProposalStatus.MODIFIED,
                HumanDecisionKind.REJECT: ProposalStatus.REJECTED,
            }[decision]
            result = HumanDecision(
                id=str(uuid4()),
                proposal_id=proposal.id,
                decision=decision,
                note=grant["note"],
                modified_action=grant["modified_action"],
                decided_at=now,
            )

            db.execute(
                """
                INSERT INTO teacher_decisions
                (id, proposal_id, decision, note, modified_action, decided_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result.id,
                    result.proposal_id,
                    result.decision.value,
                    result.note,
                    result.modified_action,
                    result.decided_at,
                ),
            )
            db.execute(
                "UPDATE proposals SET status = ? WHERE id = ?",
                (next_status.value, proposal.id),
            )
            db.execute(
                "UPDATE human_approval_grants SET consumed_at = ? WHERE id = ?",
                (now, approval_id),
            )
        return result

    def log_tool_call(
        self,
        tool_name: str,
        input_data: dict,
        output_data: dict,
        status: str,
    ) -> str:
        call_id = str(uuid4())
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO tool_calls
                (id, tool_name, input_json, output_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    call_id,
                    tool_name,
                    json.dumps(input_data, ensure_ascii=False, sort_keys=True),
                    json.dumps(output_data, ensure_ascii=False, sort_keys=True),
                    status,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return call_id

    def list_tool_calls(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM tool_calls ORDER BY created_at, id"
            ).fetchall()
        return [
            {
                "id": row["id"],
                "tool_name": row["tool_name"],
                "input": json.loads(row["input_json"]),
                "output": json.loads(row["output_json"]),
                "status": row["status"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
