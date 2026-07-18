# SMERC Fake Customer Production-Like Pilot Report

This report simulates AcmeCloud, a fake customer environment. It is useful for end-to-end program testing, not customer proof or production certification.

## Summary

- Scenario count: `5`
- Decision differences from traditional allow/deny: `4`
- Decision difference rate: `0.8`
- Valid DLL chains: `5`
- Rollback scenarios: `1`

## Scenario Results

| Scenario | Traditional | SMERC | SPARTa | Execution | Exposure | Capacity |
|---|---:|---:|---:|---:|---:|---:|
| `acme-safe-deployment` | `ALLOW` | `ALLOW` | `EXECUTE` | `succeeded` | `0.098` | `0.9` |
| `acme-risky-production-change` | `ALLOW` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `succeeded` | `0.5` | `0.613` |
| `acme-destructive-data-request` | `ALLOW` | `DENY` | `BLOCK` | `blocked` | `0.925` | `0.191` |
| `acme-escalated-security-request` | `ALLOW` | `ESCALATE` | `REVIEW_REQUIRED` | `not_executed` | `0.731` | `0.5` |
| `acme-failure-rollback` | `ALLOW` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `failed` | `0.442` | `0.671` |

## Boundary

- Does not prove: real customer demand
- Does not prove: live production safety
- Does not prove: native GitHub runner isolation
- Does not prove: truth of external platform controls
- Does not prove: incident reduction in customer environments
