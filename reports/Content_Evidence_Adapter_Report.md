# SMERC Content Evidence Adapter Report

- Generated: `2026-08-26T20:52:34+00:00`
- Scenarios evaluated: `5`
- Average content risk score: `0.616`
- Average evidence reliability score: `0.803`
- Max posture counts: `{'ALLOW': 1, 'DENY': 1, 'ESCALATE': 2, 'FREEZE': 1}`

| Action | Target | Risk | Reliability | Trust | Max Posture | Findings |
| --- | --- | ---: | ---: | --- | --- | --- |
| CONTENT_SQL_DROP_001 | sql_migration | 0.881 | 1.0 | HIGH | DENY | customer_data_deletion, destructive_database_operation |
| CONTENT_CUSTOMER_EMAIL_002 | customer_email | 0.711 | 1.0 | HIGH | ESCALATE | external_legal_commitment, regulated_data_exposure |
| CONTENT_CODE_DIFF_003 | code_diff | 0.108 | 1.0 | HIGH | ALLOW | None |
| CONTENT_SCANNER_DOWN_004 | mcp_tool_payload | 0.62 | 0.135 | MISSING_CONTENT | FREEZE | None |
| CONTENT_STALE_SCAN_005 | deployment_artifact | 0.76 | 0.88 | HIGH | ESCALATE | privilege_escalation |

## Evidence Boundary

Synthetic examples demonstrate content-evidence ingestion. Replace these with customer-approved scanner or reviewer signals during a pilot; do not send raw source code, customer data, secrets, or private prompts.

