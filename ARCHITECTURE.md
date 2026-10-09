# Architecture

## Objective

The challenge prototype answers one narrow question:

**What can this learner demonstrably do independently over time, and what should a teacher consider next?**

It does not attempt to recreate the full Anw Kalan platform.

## System boundary

~~~text
Synthetic learning evidence
        |
        v
First-party MCP server
  | get_learner_timeline
  | analyze_learning_evidence
  | get_curriculum_context
  | propose_next_learning_action
  | apply_human_approved_decision
  | get_tool_audit_log
        |
        v
Deterministic Evidence Engine
        |
        v
Advisory Learning State
        |
        v
Recommendation Engine
        |
        +------> Open-weights model
        |        verbalizes only
        |        cannot change state
        v
Teacher review
 [Accept] [Modify] [Reject]
        |
        v
Decision + audit log

External MCP server
        |
        +------> challenge integration boundary
~~~

## Authority model

### 1. Evidence is the source of truth

Each evidence item has an identifier, type, timestamp, competency, score, assistance flag, source and notes.

### 2. Deterministic engine interprets the evidence

The language model does not compute mastery. A pure rules engine produces an advisory state:

- not_evaluated
- fragile
- acquiring
- mastered
- advanced

These are challenge-demo advisory states, not immutable labels attached to a child.

### 3. The model verbalizes; it does not govern

The open-weights model receives the computed summary and recommendation. Its role is to explain them clearly. It cannot change the evidence set, computed state, cited evidence IDs or approval requirement.

### 4. Human approval is explicit

Every proposed action has requires_human_approval=true.

A proposal remains proposed until a teacher explicitly chooses one of:

- accept;
- modify;
- reject.

The AI has no tool that can create a human approval grant. The human interface creates a one-time grant; the MCP action tool can only consume that already-authorized grant.

### 5. Auditability

Every MCP tool invocation is stored with:

- tool name;
- timestamp;
- input payload;
- output payload;
- success/failure.

Every teacher decision is stored separately.

## Pedagogical model

The prototype follows the learning loop:

Understand → guided attempt → independent attempt → explanation → transfer → delayed review.

Important invariants:

- assisted success alone never yields mastered;
- independent evidence is mandatory for mastered;
- explanation and transfer are required before mastered;
- delayed retention is required before advanced;
- recommendations must cite the evidence IDs used;
- lack of evidence must be reported as lack of evidence, not guessed around.

## Public/private boundary

This repository contains only the challenge implementation, synthetic fixtures and generic learning-evidence rules.

It does not contain:

- production learner data;
- private Anw Kalan repositories;
- the complete KLL runtime;
- proprietary course content;
- production credentials;
- production mobile code;
- private Bamanankan datasets.

## External MCP

The final submission will connect one independently authored MCP server through a clearly documented adapter. That integration is deliberately kept separate from the first-party MCP server so the judges can see which tools are ours and which are external.

## Open-weights requirement

The final demo must execute at least one complete task with an open-weights model. The architecture keeps this model behind a narrow verbalization interface so model substitution does not alter pedagogical authority.
