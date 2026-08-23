# SMERC Autonomy Budget Report

Generated: `2026-08-23T01:06:57+00:00`

## Summary

- Initial state: `HEALTHY`
- Current autonomy state: `SUSPEND_AUTONOMY`
- Actions spent: `4` of `10`
- Scope units spent: `2544.0` of `1000`
- Risk spend: `2.833` of `3.0`
- Ref-gate failures: `1`
- Blocked or held attempts: `3`

## Review Triggers

- `ref_gate_failure`
- `scope_budget_exhausted`
- `repeated_blocked_or_held_attempts`
- `autonomy_removed_until_review`

## Budget Ledger

| # | Request | Tool | Posture | Ref Gate | Risk Spend | Remaining Actions | Remaining Scope | Remaining Risk | State After |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `MCP_SEARCH_DOCS_001` | `search_documents` | `ALLOW` | `pass` | 0.013 | 9 | 980.0 | 2.987 | `HEALTHY` |
| 2 | `MCP_DELETE_CUSTOMER_RECORDS_002` | `delete_customer_records` | `DENY` | `pass` | 0.7 | 8 | 0.0 | 2.287 | `SUSPEND_AUTONOMY` |
| 3 | `MCP_STABLECOIN_TRANSFER_003` | `stablecoin_treasury_transfer` | `DENY` | `pass` | 0.62 | 7 | 0.0 | 1.667 | `SUSPEND_AUTONOMY` |
| 4 | `MCP_STABLECOIN_TRANSFER_004` | `stablecoin_treasury_transfer` | `DENY` | `fail` | 1.5 | 6 | 0.0 | 0.167 | `SUSPEND_AUTONOMY` |

## Plain English Summary

Autonomy should be suspended for this session because the action stream exhausted or violated the current autonomy budget. Human review should requalify the agent or tool family before more autonomous execution is allowed.
