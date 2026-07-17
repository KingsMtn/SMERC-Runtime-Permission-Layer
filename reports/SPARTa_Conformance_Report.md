# SPARTa Adapter Conformance Report

This report checks whether declared SPARTa adapters route each SMERC posture into the expected execution state. It is not production certification or live vendor attestation.

## Summary

- Adapter count: `4`
- Posture probes: `20`
- Failed posture probes: `0`
- Example-only adapters: `2`
- Declared adapters: `2`
- Passed: `true`

## Adapter Results

| Adapter | Tool | Boundary | Gaps | Passed |
| --- | --- | --- | --- | --- |
| `github-actions-deployer` | `github_actions` | `declared_adapter` | none | `true` |
| `readonly-observer` | `audit_observer` | `declared_adapter` | scope_limit, checkpoint_or_rollback | `true` |
| `service-ticket-review` | `ticketing_review` | `example_adapter_only` | scope_limit, checkpoint_or_rollback | `true` |
| `chat-review-bridge` | `chat_review` | `example_adapter_only` | scope_limit, checkpoint_or_rollback | `true` |

## Posture Probes

| Adapter | Posture | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| `github-actions-deployer` | `ALLOW` | `EXECUTE` | `EXECUTE` | `pass` |
| `github-actions-deployer` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `CONSTRAINED_EXECUTE` | `pass` |
| `github-actions-deployer` | `FREEZE` | `PAUSE` | `PAUSE` | `pass` |
| `github-actions-deployer` | `DENY` | `BLOCK` | `BLOCK` | `pass` |
| `github-actions-deployer` | `ESCALATE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |
| `readonly-observer` | `ALLOW` | `EXECUTE` | `EXECUTE` | `pass` |
| `readonly-observer` | `THROTTLE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |
| `readonly-observer` | `FREEZE` | `PAUSE` | `PAUSE` | `pass` |
| `readonly-observer` | `DENY` | `BLOCK` | `BLOCK` | `pass` |
| `readonly-observer` | `ESCALATE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |
| `service-ticket-review` | `ALLOW` | `EXECUTE` | `EXECUTE` | `pass` |
| `service-ticket-review` | `THROTTLE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |
| `service-ticket-review` | `FREEZE` | `PAUSE` | `PAUSE` | `pass` |
| `service-ticket-review` | `DENY` | `BLOCK` | `BLOCK` | `pass` |
| `service-ticket-review` | `ESCALATE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |
| `chat-review-bridge` | `ALLOW` | `EXECUTE` | `EXECUTE` | `pass` |
| `chat-review-bridge` | `THROTTLE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |
| `chat-review-bridge` | `FREEZE` | `PAUSE` | `PAUSE` | `pass` |
| `chat-review-bridge` | `DENY` | `BLOCK` | `BLOCK` | `pass` |
| `chat-review-bridge` | `ESCALATE` | `REVIEW_REQUIRED` | `REVIEW_REQUIRED` | `pass` |

## Evidence Boundary

Static SPARTa adapter conformance report only. It verifies registry declarations against deterministic route behavior; it does not prove live vendor enforcement, production readiness, independent security review, or incident reduction.

## Recommended Next Action

Use this registry for pilot discussion and mock review flows. Before enforcement, replace example-only adapters with live integrations or keep them explicitly marked as production_boundary=example_adapter_only: service-ticket-review, chat-review-bridge
