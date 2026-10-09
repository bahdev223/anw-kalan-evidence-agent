from __future__ import annotations

import json
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .evidence_engine import EvidenceEngine
from .open_weights import OpenWeightsVerbalizer
from .recommendation_engine import RecommendationEngine
from .store import ChallengeStore


class AgentState(TypedDict, total=False):
    learner_id: str
    competency_id: str
    summary: dict[str, Any]
    proposal: dict[str, Any]
    verbalization: dict[str, Any]


def build_graph(store: ChallengeStore):
    evidence_engine = EvidenceEngine()
    recommendation_engine = RecommendationEngine()
    verbalizer = OpenWeightsVerbalizer()

    def analyze(state: AgentState) -> AgentState:
        items = store.list_evidence(
            state["learner_id"], state["competency_id"]
        )
        summary = evidence_engine.analyze(
            state["learner_id"], state["competency_id"], items
        )
        return {"summary": summary.to_dict()}

    def propose(state: AgentState) -> AgentState:
        items = store.list_evidence(
            state["learner_id"], state["competency_id"]
        )
        summary = evidence_engine.analyze(
            state["learner_id"], state["competency_id"], items
        )
        proposal = recommendation_engine.propose(summary)
        store.save_proposal(proposal)
        return {"proposal": proposal.to_dict()}

    def verbalize(state: AgentState) -> AgentState:
        items = store.list_evidence(
            state["learner_id"], state["competency_id"]
        )
        summary = evidence_engine.analyze(
            state["learner_id"], state["competency_id"], items
        )
        proposal = store.get_proposal(state["proposal"]["id"])
        result = verbalizer.verbalize(summary, proposal)
        return {"verbalization": result}

    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyze)
    graph.add_node("propose", propose)
    graph.add_node("verbalize", verbalize)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "propose")
    graph.add_edge("propose", "verbalize")
    graph.add_edge("verbalize", END)
    return graph.compile()


def run_once(
    learner_id: str,
    competency_id: str,
    store: ChallengeStore | None = None,
) -> dict[str, Any]:
    store = store or ChallengeStore()
    graph = build_graph(store)
    return graph.invoke(
        {
            "learner_id": learner_id,
            "competency_id": competency_id,
        }
    )


def main() -> None:
    result = run_once(
        learner_id="learner-demo-001",
        competency_id="math.fractions.unlike-denominators",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
