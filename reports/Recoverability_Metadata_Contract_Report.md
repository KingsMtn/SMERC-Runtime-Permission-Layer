# Recoverability Metadata Contract Report

Version: `smerc.recoverability-metadata-contract.v0`

## Work / Result / Impact

- Work: Define the smallest recoverability metadata shape for individual tool calls and automation actions.
- Result: MCP tools, GitHub Actions, AWS-style actions, and other runtimes can describe rollback, side effects, blast radius, evidence, and posture hints before execution.
- Impact: If this small contract becomes normal, larger SMERC scoring gets cleaner inputs instead of guessing recoverability from logs after the fact.

## Summary

- Records: `3`
- Valid records: `3`
- Invalid records: `0`
- Posture counts: `{'FREEZE': 1, 'THROTTLE': 2}`
- Risk hint counts: `{'bounded_side_effect': 1, 'recovery_unknown_or_hard': 1, 'side_effect_with_slow_rollback': 1}`

## Validation Results

| Action | Valid | Posture | Risk Hint | Errors |
| --- | --- | --- | --- | --- |
| `RMC-MCP-001` | `True` | `THROTTLE` | `bounded_side_effect` |  |
| `RMC-GHA-002` | `True` | `THROTTLE` | `side_effect_with_slow_rollback` |  |
| `RMC-AWS-003` | `True` | `FREEZE` | `recovery_unknown_or_hard` |  |

## Evidence Boundary

Recoverability metadata is a hint contract. It does not authorize execution, replace policy engines, prove safety, or certify production readiness. SMERC or another runtime still has to validate and decide.
