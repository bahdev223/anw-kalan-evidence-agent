from __future__ import annotations

import json
import os
from pathlib import Path


DEFAULT_PATH = Path("data/curriculum_demo.json")


def get_curriculum_context(
    learner_id: str,
    competency_id: str,
    path: str | None = None,
) -> dict:
    curriculum_path = Path(
        path or os.getenv("CURRICULUM_DEMO_PATH", str(DEFAULT_PATH))
    )
    if not curriculum_path.exists():
        return {
            "learner_id": learner_id,
            "competency_id": competency_id,
            "found": False,
            "detail": "Demo curriculum file is not available.",
        }

    payload = json.loads(curriculum_path.read_text(encoding="utf-8"))
    learners = payload.get("learners", {})
    learner = learners.get(learner_id)
    if not learner:
        return {
            "learner_id": learner_id,
            "competency_id": competency_id,
            "found": False,
            "detail": "Learner is not present in the synthetic curriculum fixture.",
        }

    competencies = learner.get("competencies", {})
    competency = competencies.get(competency_id)
    if not competency:
        return {
            "learner_id": learner_id,
            "competency_id": competency_id,
            "found": False,
            "detail": "Competency is outside the learner's demo curriculum context.",
        }

    return {
        "learner_id": learner_id,
        "competency_id": competency_id,
        "found": True,
        "level": learner.get("level"),
        "subject": learner.get("subject"),
        "language": learner.get("language"),
        "competency": competency,
    }
