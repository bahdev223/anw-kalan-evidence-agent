# Anw Kalan Evidence Agent

Challenge-specific open-source prototype for the African Agentic AI Design Challenge — Education track.

## Mission

Anw Kalan Evidence Agent helps a teacher understand what a learner can actually do over time. It separates assisted success from independent evidence, cites the evidence behind every recommendation, progressively reduces AI assistance, and keeps the human in control of the final decision.

The pedagogical loop is:

Understand → try with help → redo independently → explain → transfer to a new context → revisit later.

A learner is not considered strong merely because an AI helped them reach the answer.

## Core principles

- Evidence before claims.
- Assisted success is not mastery.
- The language model does not decide mastery.
- Recommendations are grounded in a deterministic evidence engine.
- Every recommendation cites the evidence that produced it.
- Teacher decisions are explicit: accept, modify, or reject.
- No recommendation silently changes an official learner record.
- Synthetic demo data only in this public repository.
- The full Anw Kalan product, private datasets, production backend, mobile application, and proprietary content are not part of this repository.

## Challenge scope

This repository is new work created during the 2026 challenge submission window. It is intentionally smaller than the production Anw Kalan platform.

Initial challenge scenario:

1. collect a learner's longitudinal evidence;
2. distinguish assisted and independent performance;
3. compute an advisory learning state using deterministic rules;
4. propose a next learning action;
5. show the exact evidence behind the proposal;
6. require a human decision before the proposal becomes an accepted plan;
7. audit tool calls and human decisions.

## MCP tools

The first-party MCP server exposes a narrow set of tools:

- get_learner_timeline
- analyze_learning_evidence
- get_curriculum_context
- propose_next_learning_action
- record_teacher_decision

The last tool performs a real write, but only records the teacher's explicit decision. The AI cannot approve its own recommendation.

## Repository layout

~~~text
src/anw_kalan_evidence_agent/
  models.py
  store.py
  evidence_engine.py
  recommendation_engine.py
  orchestration.py
  open_weights.py
  server.py
data/
  curriculum_demo.json
demo/
  seed_demo.py
  run_demo.py
evals/
  scenarios.json
tests/
  test_evidence_engine.py
ARCHITECTURE.md
EVALS.md
docs/CHALLENGE_COMPLIANCE.md
~~~

## Status

Foundation phase. The deterministic engines, MCP surface, human-approval model and evaluation fixtures are being built first. The final challenge submission will also include:

- a second MCP server not authored by this team;
- at least one end-to-end run using an open-weights model;
- visible tool-call logs;
- a minimal web demo;
- a public unedited demo video under the challenge time limit;
- completed evaluation results.

## License

GNU Affero General Public License v3.0 (AGPL-3.0). The license applies to this challenge repository only and does not relicense the separate Anw Kalan product or private repositories.
