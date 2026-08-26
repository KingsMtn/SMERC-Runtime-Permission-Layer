# SMERC Company Evaluation Reviewer Scorecard

Use this scorecard after running a metadata-only customer evaluation.

## Fit Questions

| Question | Yes / No | Notes |
| --- | --- | --- |
| Did SMERC identify a recoverability issue our current process does not clearly show? |  |  |
| Did SMERC produce at least one useful constrained path between allow and block? |  |  |
| Did any hard admission gate correctly prevent scoring from supporting execution? |  |  |
| Did rollback latency, containment, cancellation, or impact scope change reviewer judgment? |  |  |
| Can this workflow be evaluated without secrets, source code, raw customer records, production logs, or regulated payloads? |  |  |
| Is there a workflow owner willing to run observe mode? |  |  |
| Is there a reviewer group willing to label sampled decisions weekly? |  |  |

## Reviewer Labels

For each evaluated action, assign one label:

- `agree`: SMERC posture matches reviewer judgment.
- `too_strict`: SMERC should have allowed or constrained more.
- `too_permissive`: SMERC should have constrained, frozen, denied, or escalated more.
- `useful_constraint`: SMERC found a middle path that existing controls would likely miss.
- `hard_gate_correct`: hard evidence failure should stop execution before scoring matters.
- `not_useful`: output does not add meaningful review value.

## Pilot Decision

Use this decision rule:

- `continue_to_observe_mode`: at least one workflow owner, reviewer availability, safe metadata boundary, and useful disagreement or useful constraints.
- `collect_more_metadata`: output is plausible but action examples are too generic.
- `stop`: reviewers see no value beyond existing controls or the workflow cannot be tested safely.

