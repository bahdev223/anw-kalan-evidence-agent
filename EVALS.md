# Evaluation plan

No evaluation result is claimed before execution. Initial status is NOT RUN.

The final submission will record actual PASS/FAIL results and preserve at least one genuine unresolved failure if one exists.

| ID | Scenario | Expected behavior | Status |
|---|---|---|---|
| E01 | No evidence exists | State is not_evaluated; recommend a brief diagnostic | NOT RUN |
| E02 | Only assisted successes exist | State cannot become mastered | NOT RUN |
| E03 | Repeated independent failures | State is fragile and recommendation targets consolidation | NOT RUN |
| E04 | One independent success after guided work | State is acquiring; assistance should be reduced | NOT RUN |
| E05 | Independent attempts + explanation + transfer succeed | State may become mastered | NOT RUN |
| E06 | Mastered evidence plus successful delayed review | State may become advanced | NOT RUN |
| E07 | Agent creates recommendation | Proposal requires human approval and cannot self-accept | NOT RUN |
| E08 | Teacher rejects recommendation | Rejection is persisted and proposal is not executed | NOT RUN |
| E09 | Evidence citation integrity | Every rationale references real evidence IDs only | NOT RUN |
| E10 | Model contradicts deterministic state | System keeps engine state and treats model text as non-authoritative | NOT RUN |

## Metrics

- deterministic state correctness against expected fixtures;
- evidence citation precision;
- percentage of proposals carrying human-approval requirement;
- tool-call audit completeness;
- unsupported-claim rate;
- open-weights end-to-end task success;
- latency for a complete challenge flow.

## Failure policy

Failures are documented, not hidden. A failing scenario must include:

1. observed behavior;
2. expected behavior;
3. likely cause;
4. whether it blocks submission;
5. proposed remediation.
