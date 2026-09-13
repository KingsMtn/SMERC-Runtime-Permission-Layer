# SMERC End-to-End Reviewer Flow

Generated: `2026-09-13T11:56:14+00:00`
Version: `smerc.end-to-end-reviewer-flow.v1`

## Flow

`metadata intake -> schema validation -> policy evaluation -> posture output -> evidence report`

## Work / Result / Impact

- Work: Run one reviewer-facing proof path from local metadata intake through schema validation, policy identity, posture output, and evidence reporting.
- Result: SMERC can show a coherent end-to-end flow without live AWS credentials, raw logs, customer data, or production execution authority.
- Impact: A contributor can map AWS-like or tool-call actions into SMERC safely enough for public review, while a company reviewer can see the exact handoff points needed for a private shadow-mode pilot.

## Stage Results

| Stage | Status | Summary |
| --- | --- | --- |
| `metadata_intake` | `PASS` | Accepted 5 of 7 metadata-only action summaries. |
| `schema_validation` | `PASS` | Evaluated 7 dynamic tool calls against 5 pinned schema entries. |
| `policy_evaluation` | `PASS` | Compiled SPL policy github-actions-shadow-mode@2026.07.07 in OBSERVE mode with evidence ceiling OBSERVE. |
| `posture_output` | `PASS` | Produced 5 posture rows and route hints from accepted metadata. |
| `evidence_report` | `PASS` | Generated a single evidence packet with boundaries, source artifacts, posture counts, and non-claims. |

## Policy Identity

- Policy: `github-actions-shadow-mode@2026.07.07`
- Mode: `OBSERVE`
- Evidence ceiling: `OBSERVE`
- Policy hash: `cc7b8bfd3d8f87eb10158bba6b203d5691de16529dc289a840fd7c2e0417f886`

## Summary

- Metadata actions accepted: `5`
- Intake classifications: `{'ACCEPTED_METADATA_ONLY': 5, 'REJECTED_RAW_LOG': 1, 'SKIPPED_PROHIBITED_FIELD': 1}`
- Schema classifications: `{'DRIFTED': 1, 'STRUCTURAL_MISMATCH': 1, 'UNDER_SPECIFIED': 1, 'UNKNOWN_SCHEMA': 1, 'UNSAFE': 2, 'VALID': 1}`
- Posture counts: `{'DENY': 1, 'FREEZE': 2, 'THROTTLE': 2}`
- Route counts: `{'BLOCK': 1, 'CONSTRAINED_EXECUTE': 2, 'PAUSE': 2}`

## Posture Rows

| Action | Type | Tool class | Current handling | SMERC posture | Route | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `ACT-001` | `Identity Modification` | `AWS IAM` | `allow` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `Deterministic policy diff summary` |
| `ACT-002` | `Credential Rotation` | `Secrets Manager` | `allow` | `FREEZE` | `PAUSE` | `Target secret class summary` |
| `ACT-003` | `Dynamic Tool Invocation` | `MCP Server` | `log only` | `DENY` | `BLOCK` | `Mismatched input schema summary` |
| `ACT-004` | `Database Drop` | `PostgreSQL` | `block` | `FREEZE` | `PAUSE` | `DDL command class summary` |
| `ACT-005` | `Compute Scaling` | `AWS ECS` | `allow` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `Desired count summary` |

## Evidence Boundary

This is a local proof wrapper. It does not call AWS, connect to MCP servers, execute tools, certify anonymization, prove incident reduction, or replace IAM, policy engines, scanners, approval workflows, SIEM, SOAR, or human accountability.
