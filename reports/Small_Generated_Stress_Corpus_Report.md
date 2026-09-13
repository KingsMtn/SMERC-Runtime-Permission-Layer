# Small Generated Stress Corpus Report

Version: `smerc.small-generated-stress-corpus.v1`

## Purpose

Exercise SMERC against a compact deterministic set of metadata-only stress patterns while preserving the boundary that generated data is fallback evidence, not customer validation.

## Corpus

- Actions: `12`
- Pattern families: `{'agent_egress_risk': 1, 'approved_execution_drift': 1, 'bounded_deployment': 1, 'cloud_identity_expansion': 1, 'dependency_unknown_change': 1, 'dynamic_schema_drift': 1, 'financial_retry_loop': 1, 'financial_velocity_bounds': 1, 'incident_pressure_control_change': 1, 'irreversible_data_mutation': 1, 'low_risk_validation': 1, 'network_boundary_change': 1}`
- Domain profiles: `{'cloud_admin': 3, 'finance_ops': 2, 'github_actions': 2, 'it_ops': 2, 'security_ops': 3}`

## SMERC Evaluation Summary

- Posture counts: `{'ALLOW': 1, 'DENY': 6, 'THROTTLE': 5}`
- Route state counts: `{'BLOCK': 6, 'CONSTRAINED_EXECUTE': 5, 'EXECUTE': 1}`
- Non-executable routes: `6`
- Valid DLL ledgers: `12`
- Pilot fit: `strong`

## Highest Exposure Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `STRESS-AWS-DATA-003` | `DENY` | `BLOCK` | 0.924 |
| `STRESS-MCP-EGRESS-005` | `DENY` | `BLOCK` | 0.881 |
| `STRESS-FINANCE-009` | `DENY` | `BLOCK` | 0.868 |
| `STRESS-INCIDENT-011` | `DENY` | `BLOCK` | 0.765 |
| `STRESS-AWS-IAM-001` | `DENY` | `BLOCK` | 0.751 |

## Replacement Metadata Ask

Replace this generated corpus with 5 to 25 metadata-only actions from one real workflow, then compare current controls against SMERC posture and route outputs.

## Evidence Boundary

This is a project-generated stress corpus for exercising SMERC behavior when no reviewer-owned metadata is available. It is not customer validation, production evidence, AWS endorsement, incident reduction proof, or an official benchmark score.
