# SMERC Dynamic Schema Gate Report

Generated: `2026-09-13T01:07:22+00:00`
Version: `smerc.dynamic-schema-gate.v1`

## Work / Result / Impact

- Work: Evaluate MCP/JSON-RPC-style dynamic tool-call schemas before recoverability scoring or network execution.
- Result: Classified 7 metadata-only tool calls against 5 pinned schema entries using local structural checks, schema-text checks, and argument safety checks.
- Impact: SMERC can show that dynamic schema handling is a localized gateway problem: known-good calls can continue, while drifted, unknown, poisoned, under-specified, or unsafe calls are denied, frozen, throttled, or escalated before touching an external tool.

## Summary

- Registry entries: `5`
- Tool calls: `7`
- Classification counts: `{'DRIFTED': 1, 'STRUCTURAL_MISMATCH': 1, 'UNDER_SPECIFIED': 1, 'UNKNOWN_SCHEMA': 1, 'UNSAFE': 2, 'VALID': 1}`
- SMERC posture counts: `{'ALLOW': 1, 'DENY': 3, 'ESCALATE': 2, 'THROTTLE': 1}`
- Route hint counts: `{'BLOCK': 3, 'CONSTRAINED_EXECUTE': 1, 'EXECUTE': 1, 'REVIEW_REQUIRED': 2}`

## Evidence Boundary

This gate is deterministic and local. It is not a full JSON Schema implementation, not a replacement for MCP clients, not a live proxy trace, not production certification, and not proof that every prompt injection or schema attack is caught.

## Decisions

| Call | Tool | Schema | Classification | Posture | Route | Reasons |
| --- | --- | --- | --- | --- | --- | --- |
| `DSG-001` | `ticket.search` | `2026-09-01` | `VALID` | `ALLOW` | `EXECUTE` | `['SCHEMA_GATE_VALIDATED']` |
| `DSG-002` | `ticket.search` | `2026-10-01` | `UNKNOWN_SCHEMA` | `ESCALATE` | `REVIEW_REQUIRED` | `['SCHEMA_NOT_IN_GATE_INDEX']` |
| `DSG-003` | `cloud.instance.resize` | `2026-09-01` | `DRIFTED` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `['SCHEMA_DRIFT']` |
| `DSG-004` | `cloud.instance.resize` | `2026-09-01` | `STRUCTURAL_MISMATCH` | `DENY` | `BLOCK` | `['STRUCTURAL_MISSING_DESIRED_CAPACITY']` |
| `DSG-005` | `repo.write_file` | `2026-09-01` | `UNSAFE` | `DENY` | `BLOCK` | `['SCHEMA_GATE_FAIL_CLOSED', 'UNSAFE_ARGUMENT_VALUE']` |
| `DSG-006` | `ambiguous.admin` | `2026-09-01` | `UNDER_SPECIFIED` | `ESCALATE` | `REVIEW_REQUIRED` | `['UNDER_SPECIFIED_SCHEMA']` |
| `DSG-007` | `poisoned.schema` | `2026-09-01` | `UNSAFE` | `DENY` | `BLOCK` | `['SCHEMA_GATE_FAIL_CLOSED', 'UNSAFE_SCHEMA_TEXT']` |
