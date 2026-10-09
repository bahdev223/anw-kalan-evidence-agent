from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from .curriculum import get_curriculum_context as load_curriculum_context
from .evidence_engine import EvidenceEngine
from .recommendation_engine import RecommendationEngine
from .store import ChallengeStore


store = ChallengeStore()
evidence_engine = EvidenceEngine()
recommendation_engine = RecommendationEngine()

mcp_server = MCPServer(
    "anw-kalan-evidence-agent",
    instructions=(
        "Human-governed learning-evidence tools. "
        "The agent may analyze and propose, but it cannot create human approval. "
        "Every learning claim must be backed by evidence IDs."
    ),
)


def _audited(
    tool_name: str,
    input_data: dict[str, Any],
    operation,
) -> dict[str, Any]:
    try:
        output = operation()
        call_id = store.log_tool_call(
            tool_name, input_data, output, status="success"
        )
        return {"tool_call_id": call_id, **output}
    except Exception as exc:
        error = {"error": str(exc)}
        call_id = store.log_tool_call(
            tool_name, input_data, error, status="failed"
        )
        return {"tool_call_id": call_id, **error}


@mcp_server.tool()
def get_learner_timeline(
    learner_id: str,
    competency_id: str | None = None,
) -> dict[str, Any]:
    """Read synthetic longitudinal evidence for a learner."""

    args = {
        "learner_id": learner_id,
        "competency_id": competency_id,
    }

    def operation() -> dict[str, Any]:
        items = store.list_evidence(learner_id, competency_id)
        return {
            "learner_id": learner_id,
            "competency_id": competency_id,
            "count": len(items),
            "evidence": [item.to_dict() for item in items],
        }

    return _audited("get_learner_timeline", args, operation)


@mcp_server.tool()
def get_curriculum_context(
    learner_id: str,
    competency_id: str,
) -> dict[str, Any]:
    """Read the learner's permitted synthetic curriculum context."""

    args = {
        "learner_id": learner_id,
        "competency_id": competency_id,
    }
    return _audited(
        "get_curriculum_context",
        args,
        lambda: load_curriculum_context(learner_id, competency_id),
    )


@mcp_server.tool()
def analyze_learning_evidence(
    learner_id: str,
    competency_id: str,
) -> dict[str, Any]:
    """Compute an advisory state from evidence using deterministic rules."""

    args = {
        "learner_id": learner_id,
        "competency_id": competency_id,
    }

    def operation() -> dict[str, Any]:
        items = store.list_evidence(learner_id, competency_id)
        return evidence_engine.analyze(
            learner_id, competency_id, items
        ).to_dict()

    return _audited("analyze_learning_evidence", args, operation)


@mcp_server.tool()
def propose_next_learning_action(
    learner_id: str,
    competency_id: str,
) -> dict[str, Any]:
    """Create a grounded proposal that always requires explicit human approval."""

    args = {
        "learner_id": learner_id,
        "competency_id": competency_id,
    }

    def operation() -> dict[str, Any]:
        curriculum = load_curriculum_context(learner_id, competency_id)
        if not curriculum.get("found"):
            raise ValueError(
                "The competency is outside the learner's permitted curriculum context."
            )
        items = store.list_evidence(learner_id, competency_id)
        summary = evidence_engine.analyze(
            learner_id, competency_id, items
        )
        proposal = recommendation_engine.propose(summary)
        store.save_proposal(proposal)
        return {
            **proposal.to_dict(),
            "curriculum_context": curriculum,
        }

    return _audited("propose_next_learning_action", args, operation)


@mcp_server.tool()
def apply_human_approved_decision(
    approval_id: str,
) -> dict[str, Any]:
    """Apply a one-time approval grant created outside MCP by a human action."""

    args = {"approval_id": approval_id}

    def operation() -> dict[str, Any]:
        result = store.apply_human_approval(approval_id)
        proposal = store.get_proposal(result.proposal_id)
        return {
            "human_decision": result.to_dict(),
            "proposal": proposal.to_dict(),
        }

    return _audited("apply_human_approved_decision", args, operation)


@mcp_server.tool()
def get_tool_audit_log() -> dict[str, Any]:
    """Read the challenge tool-call audit trail for the demo."""

    return _audited(
        "get_tool_audit_log",
        {},
        lambda: {"calls": store.list_tool_calls()},
    )


@mcp_server.resource(
    "anw-kalan-evidence://learners/{learner_id}/timeline",
    mime_type="application/json",
)
def learner_timeline_resource(learner_id: str) -> dict[str, Any]:
    items = store.list_evidence(learner_id)
    return {
        "learner_id": learner_id,
        "evidence": [item.to_dict() for item in items],
    }
