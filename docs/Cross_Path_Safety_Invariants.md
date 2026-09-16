# Cross-Path Safety Invariants

SMERC treats external reviewer bypass probes as reusable system invariants. The purpose is to catch a class of defect across every entry point instead of patching one endpoint at a time.

## Current invariant matrix

| Invariant | Expected behavior |
| --- | --- |
| Missing admission | A request without admission evidence resolves to `REJECT` and cannot reach `ALLOW`. |
| Empty admission policy | `required_checks: []` cannot remove the default hard checks. |
| Strictest posture wins | Combining admission and recoverability decisions cannot reduce either posture. |
| Missing recoverability evidence | Omitted high-impact recovery signals do not produce `ALLOW`. |
| Cross-path consistency | Recoverability, Action Language, customer evaluation, and MCP paths all record missing evidence as unavailable. |
| Unknown contract shape | Unknown fields are rejected rather than ignored by structured entry points. |

Run the matrix with:

```bash
python -m unittest tests.test_cross_path_safety_invariants -v
```

## Adding an external probe

1. Reduce the report to the smallest input that reproduces the behavior.
2. Identify the safety invariant it violates, such as fail-closed defaults, monotonic strictness, or cross-path equivalence.
3. Add the same probe to every applicable entry point.
4. Confirm the test fails when the protection is removed and passes with the correction.
5. Preserve the external source and tested commit in `probes/` without copying sensitive data.

## Claim boundary

Passing this matrix demonstrates the declared behavior of the checked local paths. It does not prove deployed enforcement, complete attack coverage, production incident reduction, or customer-calibrated thresholds. Independent review remains useful for finding assumptions that the matrix itself does not yet encode.
