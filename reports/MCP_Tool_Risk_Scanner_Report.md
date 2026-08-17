# SMERC MCP Tool Risk Scanner Report

Generated: `2026-08-17T01:48:39+00:00`

## Summary

- Tool: `delete_customer_records`
- Operation class: `delete`
- Likely SMERC posture: `DENY`
- Irreversible exposure score: `0.844`
- Reversible capacity score: `0.388`
- Risk-adjusted authorization score: `0.455`

## Reason Codes

- `CANCEL_RELIABILITY_WEAK`
- `EXTERNAL_SIDE_EFFECT`
- `HIGH_IMPACT_TOOL_CLASS`
- `IMPACT_SCOPE_WIDE`
- `IRREVERSIBLE_EXPOSURE_HIGH`
- `LOW_INFERRED_REVERSIBILITY`
- `RECOVERY_CAPACITY_LOW`
- `SENSITIVE_DATA`
- `SENSITIVE_DOMAIN_TERMS`
- `TOOL_CAN_CREATE_SIDE_EFFECTS`

## Recommended Controls

- `block_execution`
- `explain_denial`
- `preserve_replay`
- `record_decision_lifecycle`
- `require_dry_run`
- `require_human_approval`
- `require_new_request`
- `require_rollback_plan`
- `require_scope_limit`

## Missing Metadata

- None

## Plain English

SMERC scanned MCP tool `delete_customer_records` as a likely `delete` operation and returned DENY. This should be treated as a triage result for reviewers before the tool is granted autonomous execution authority.

## Evidence Boundary

This scanner uses deterministic keyword, annotation, and schema heuristics to triage MCP tool definitions. It is a front-door risk scanner, not proof that a live tool call is safe or unsafe.
