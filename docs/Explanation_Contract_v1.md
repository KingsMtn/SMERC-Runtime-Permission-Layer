# SMERC Explanation Contract v1

`smerc.explanation-contract.v1` is the stable explanation boundary attached to
recoverability decisions. It lets adapters vary their transport representation
without changing the identity, evidence failures, reasons, or rule precedence
reported for the same governed action.

The contract contains:

- `canonical_action_identity`: caller-supplied or native action ID plus a stable SHA-256 digest.
- `required_evidence_failures`: unavailable recoverability signals and their canonical reason codes.
- `canonical_reason_codes`: a sorted, de-duplicated reason-code set.
- `precedence_trace`: the posture after policy thresholds and each safety floor or admission gate.
- `final_posture`: the strictest posture produced by the recorded stages.

MCP callers can supply `canonical_action_id` when their transport request ID is
not the governed action ID. Unknown fields still fail validation.

This is regression evidence, not proof of deployed enforcement. A caller must
still refuse malformed responses and must never map validation failure to
`ALLOW`. HTTP API validation failures are returned as typed API errors;
in-process adapters currently raise their documented validation exceptions.

See `examples/explanation_contract_mutation_matrix.json` and
`tests/test_cross_path_safety_invariants.py`.
