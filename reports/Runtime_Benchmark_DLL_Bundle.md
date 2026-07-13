# SMERC Benchmark Decision-Time Ledger Bundle

Generated: `2026-07-13T03:55:16+00:00`
Source benchmark: `smerc.runtime-benchmark-suite.v1`
Tenant: `benchmark-suite`

## Executive Summary

This bundle creates `84` hash-chained Decision Lifecycle Ledger records from the runtime governance benchmark suite.

The ledgers intentionally stop at request, evidence, and evaluation. They do not claim live execution, customer outcome, human review, or incident-reduction evidence.

## Metrics

- Valid ledgers: `84`
- Invalid ledgers: `0`
- Decision-time only ledgers: `84`
- Posture counts: `{'ALLOW': 18, 'DENY': 16, 'ESCALATE': 5, 'FREEZE': 14, 'THROTTLE': 31}`

## Evidence Boundary

Decision-time ledgers built from expanded proxy benchmark records; execution, outcome, human review, and customer incident evidence are intentionally absent until pilot collection.

## Example Ledger Heads

| Decision ID | Records | Head Hash | Posture |
| --- | ---: | --- | --- |
| `dll:proxy-deploy-001::baseline` | 3 | `670874934963e532cbdbb7e7a71e3ffc52194fd123919450f9ce607a8877afa2` | `THROTTLE` |
| `dll:proxy-deploy-001::better_evidence` | 3 | `9f5aee4e85dc09e470975a5328f67c1ed787033f6956b2d360ac533ce4abc52a` | `THROTTLE` |
| `dll:proxy-deploy-001::wider_scope` | 3 | `915d1f5f80dfdd9bbb16934d979d29836c1b6368f4d85714bc8bca67f2849905` | `THROTTLE` |
| `dll:proxy-deploy-001::faster_rollback` | 3 | `d1f1541a66e8742c0335858c442ca13d074260d33e190dbba97d7ae37e7019e2` | `THROTTLE` |
| `dll:proxy-deploy-001::weak_evidence` | 3 | `8d2cb24e66bdc0c6d8d4ef4fb75701b1780207006e6bc0241e94a3cb8c683f2c` | `THROTTLE` |
| `dll:proxy-deploy-001::traditional_deny` | 3 | `085859bb28c6baf49838fdcdd366e7180f613171fd03106f711aa9eae6298c35` | `THROTTLE` |
| `dll:proxy-deploy-002::baseline` | 3 | `f5978052128c6525b8dd21137fa192ed510a6a88e352c69989d6d06c50f1e397` | `ALLOW` |
| `dll:proxy-deploy-002::better_evidence` | 3 | `0d8842aa1f0160d92c0ff76c4285450d0492c4a3d6911819473673149017a794` | `ALLOW` |
| `dll:proxy-deploy-002::wider_scope` | 3 | `df33a666f8058e330f6db1a439b89654d281078115eaa49edf374b4b0821c2e0` | `ALLOW` |
| `dll:proxy-deploy-002::faster_rollback` | 3 | `d0882f402668f755ccec55dd28a6ae3e97bca3fb259a2b7cf597bd012527b8fa` | `ALLOW` |
| `dll:proxy-deploy-002::weak_evidence` | 3 | `018b76d45501ceb85e2d380f296c9e730c721fef9bd827c7da5f9cb4b247d269` | `ALLOW` |
| `dll:proxy-deploy-002::traditional_deny` | 3 | `6097882a664a5d8796911f7a856fed9f097b9a30bddbfe5a7d697165498e7fa0` | `ALLOW` |

## What This Adds

- Each benchmark decision becomes replayable evidence with a hash-chain integrity check.
- Missing outcome and execution evidence is explicit instead of hidden.
- The same ledger format can be reused when design partners provide real reviewer labels and execution outcomes.

## What This Does Not Prove

- It does not prove the benchmark reflects a customer's production environment.
- It does not prove SMERC reduced incidents.
- It does not replace customer security review, SIEM retention, GRC workflows, or legal recordkeeping.
