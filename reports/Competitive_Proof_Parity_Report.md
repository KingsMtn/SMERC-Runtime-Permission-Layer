# SMERC Competitive Proof Parity Report

Generated: `2026-08-17T02:26:59+00:00`

## Executive Summary

This report runs SMERC across the same proof categories commonly used by adjacent MCP gateway, AI gateway, policy-as-code, runtime governance, and agent security products.

It shows proof-category parity and recoverability-specific decision evidence. It does not claim that SMERC is better than named competitors, production-certified, or customer-validated.

## Top Metrics

- Proof categories covered: `7`
- Total records evaluated across sections: `107`
- Aggregated posture counts: `{'ALLOW': 22, 'DENY': 20, 'ESCALATE': 7, 'FREEZE': 15, 'THROTTLE': 39, 'UNAVAILABLE': 0}`
- Average irreversible exposure across scored sections: `0.527`
- Average reversible capacity across scored sections: `0.57`
- Runtime benchmark decision difference rate: `0.786`
- Real public incident replay difference rate: `1.0`
- Fake-customer valid DLL chains: `5`
- Timing operational status: `ready`

## Proof Category Table

| Proof Category | Adjacent Products Usually Show | SMERC Evidence Produced | Source Boundary |
|---|---|---|---|
| Catalog evidence | Tool inventory, risk annotations, missing metadata, and dangerous-tool review. | Scanned 3 MCP-style tool definitions and identified 1 deny-class and 1 throttle-class tools. | Synthetic MCP-style tool definitions; no private MCP registry or customer tool catalog. |
| Runtime decision evidence | Pre-execution policy or governance decisions before a tool call runs. | Evaluated 2 MCP-style tool calls before execution with replayable posture and route evidence. | Metadata-only MCP tool-call examples; no live MCP server or production agent runtime. |
| Proxy/enforcement evidence | Gateway/proxy monitor mode, enforce mode, forwarding decisions, and audit trail. | Ran 4 proxy samples across shadow, enforce, and JSON-RPC-shaped transport behavior. | Local reference proxy samples; no network proxy, OAuth broker, sandbox, or native tool execution. |
| Benchmark evidence | Scenario benchmark showing decision distribution and comparison to baseline policy. | Evaluated 84 expanded proxy scenarios with a 0.786 difference rate from simple allow/deny. | Deterministic scenario expansion from seed proxy scenarios; not production validation or customer incident evidence. |
| Public incident replay evidence | Incident-pattern replay or narrative evidence showing governance behavior on known failure modes. | Replayed 6 public incident patterns from 4 sources with a 1.0 difference rate. | Public incident facts with analyst-assigned SMERC replay inputs; not customer telemetry, not reconstructed source-system state, and not proof of prevention. |
| Production-like simulation evidence | End-to-end demo path showing workflow decisions, routes, evidence records, and review artifacts. | Ran 5 fake-customer scenarios with 5 valid DLL chains. | Fake customer simulation; not customer proof or production certification. |
| Operational evidence | Latency, overhead, unavailable-evaluation, cancellation, and rollback metrics. | Summarized 3 timing records with operational status ready. | Synthetic timing evidence for local pilot review; not customer production latency or SLA evidence. |

## Section Summaries

### Catalog evidence

- Records: `3`
- Result: Scanned 3 MCP-style tool definitions and identified 1 deny-class and 1 throttle-class tools.
- Boundary: Synthetic MCP-style tool definitions; no private MCP registry or customer tool catalog.

- missing_metadata_items: `0`
- high_impact_tool_count: `2`
- average_irreversible_exposure_score: `0.484`
- average_reversible_capacity_score: `0.594`

### Runtime decision evidence

- Records: `2`
- Result: Evaluated 2 MCP-style tool calls before execution with replayable posture and route evidence.
- Boundary: Metadata-only MCP tool-call examples; no live MCP server or production agent runtime.

- allow_count: `1`
- deny_count: `1`
- average_irreversible_exposure_score: `0.496`
- average_reversible_capacity_score: `0.579`

### Proxy/enforcement evidence

- Records: `4`
- Result: Ran 4 proxy samples across shadow, enforce, and JSON-RPC-shaped transport behavior.
- Boundary: Local reference proxy samples; no network proxy, OAuth broker, sandbox, or native tool execution.

- forwarded_count: `2`
- blocked_or_held_count: `2`
- valid_ledger_count: `4`
- proxy_actions: `{'block_tool_call': 2, 'forward_tool_call': 1, 'observe_and_forward_tool_call': 1}`

### Benchmark evidence

- Records: `84`
- Result: Evaluated 84 expanded proxy scenarios with a 0.786 difference rate from simple allow/deny.
- Boundary: Deterministic scenario expansion from seed proxy scenarios; not production validation or customer incident evidence.

- decision_difference_rate: `0.786`
- constrained_instead_of_allowed_count: `42`
- traditional_denies_with_non_deny_smerc_count: `11`
- average_irreversible_exposure_score: `0.482`
- average_reversible_capacity_score: `0.61`

### Public incident replay evidence

- Records: `6`
- Result: Replayed 6 public incident patterns from 4 sources with a 1.0 difference rate.
- Boundary: Public incident facts with analyst-assigned SMERC replay inputs; not customer telemetry, not reconstructed source-system state, and not proof of prevention.

- source_count: `4`
- decision_difference_rate: `1.0`
- average_irreversible_exposure_score: `0.645`
- average_reversible_capacity_score: `0.497`

### Production-like simulation evidence

- Records: `5`
- Result: Ran 5 fake-customer scenarios with 5 valid DLL chains.
- Boundary: Fake customer simulation; not customer proof or production certification.

- decision_difference_rate: `0.8`
- valid_ledger_count: `5`
- rollback_scenarios: `1`
- route_state_counts: `{'BLOCK': 1, 'CONSTRAINED_EXECUTE': 2, 'EXECUTE': 1, 'REVIEW_REQUIRED': 1}`

### Operational evidence

- Records: `3`
- Result: Summarized 3 timing records with operational status ready.
- Boundary: Synthetic timing evidence for local pilot review; not customer production latency or SLA evidence.

- operational_status: `ready`
- decision_p95_ms: `60.6`
- workflow_overhead_p95_ms: `141.3`
- unavailable_evaluation_rate: `0.0`
- rollback_success_rate: `1.0`

## What This Supports

- SMERC can generate evidence in the same categories adjacent products commonly use for review.
- SMERC can add recoverability-specific scores and controls to catalog, runtime, proxy, benchmark, incident-replay, simulation, and timing evidence.
- SMERC can preserve middle-state posture evidence instead of collapsing every decision into allow or deny.

## What This Does Not Support

- customer-validated incident reduction
- production certification
- superiority over a named competitor in that competitor's own environment
- customer willingness to pay
- threshold calibration for a specific enterprise
- use of competitor private telemetry or proprietary benchmark data

## Recommended Next Step

Use this parity harness as the reusable evidence package for public review, then replace synthetic and analyst-assigned records with customer-approved metadata during a shadow-mode pilot.

