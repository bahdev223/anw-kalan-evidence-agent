from __future__ import annotations

import os
from typing import Any

import httpx

from .models import ActionProposal, EvidenceSummary


class OpenWeightsVerbalizer:
    """OpenAI-compatible adapter for an open-weights model endpoint.

    The model is intentionally downstream of the deterministic engines. It may
    explain a decision, but it cannot change the learning state, evidence IDs,
    approval requirement or proposed action.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = (
            base_url or os.getenv("OPEN_WEIGHTS_BASE_URL", "")
        ).rstrip("/")
        self.model = model or os.getenv("OPEN_WEIGHTS_MODEL", "")
        self.api_key = api_key or os.getenv("OPEN_WEIGHTS_API_KEY", "")
        self.timeout_seconds = timeout_seconds

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.model)

    def verbalize(
        self,
        summary: EvidenceSummary,
        proposal: ActionProposal,
    ) -> dict[str, Any]:
        if not self.configured:
            return {
                "used_model": False,
                "model": None,
                "text": self._fallback(summary, proposal),
            }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        system = (
            "You are N'kalan, a learning-evidence explainer. "
            "You do NOT decide mastery and you do NOT change the proposed action. "
            "Explain the deterministic result in concise teacher-facing language. "
            "State clearly that the recommendation requires human review. "
            "Cite only evidence IDs provided in the input."
        )
        user = {
            "learning_state": summary.state.value,
            "engine_rationale": summary.rationale,
            "evidence_ids": summary.evidence_ids,
            "proposal_action": proposal.action,
            "proposal_rationale": proposal.rationale,
            "requires_human_approval": proposal.requires_human_approval,
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "temperature": 0,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": str(user)},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()

        text = payload["choices"][0]["message"]["content"]
        return {
            "used_model": True,
            "model": self.model,
            "text": text,
        }

    @staticmethod
    def _fallback(
        summary: EvidenceSummary,
        proposal: ActionProposal,
    ) -> str:
        cited = ", ".join(summary.evidence_ids) or "none"
        return (
            f"Advisory state: {summary.state.value}. {summary.rationale} "
            f"Recommended next step: {proposal.action} "
            f"Evidence cited: {cited}. "
            "A teacher must accept, modify or reject this recommendation."
        )
