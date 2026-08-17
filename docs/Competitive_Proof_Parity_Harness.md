# Competitive Proof Parity Harness

## Purpose

Adjacent MCP gateway, AI gateway, policy-as-code, runtime governance, and agent security products usually prove value through repeated evidence categories:

- catalog scans
- runtime decisions
- proxy or enforcement behavior
- audit and replay records
- benchmarks
- operational timing and reliability metrics

The SMERC Competitive Proof Parity Harness runs the reference project across those same categories and produces one report.

## Command

```bash
python -m reference_engine.competitive_proof_parity --pretty
```

Outputs:

```text
reports/competitive_proof_parity_report.json
reports/Competitive_Proof_Parity_Report.md
```

## Included Proof Categories

| Category | SMERC input |
|---|---|
| Catalog evidence | `examples/mcp/tool_definition_risk_examples.json` |
| Runtime decision evidence | `examples/mcp/tool_call_delete_customer_records.json`, `examples/mcp/tool_call_search_docs.json` |
| Proxy/enforcement evidence | MCP proxy runner and transport proxy examples |
| Benchmark evidence | `examples/proxy_incident_replay_scenarios.json` |
| Public incident replay evidence | `examples/real_public_incident_replay_scenarios.json` |
| Production-like simulation evidence | `examples/fake_customer_acme/production_like_scenarios.json` |
| Operational evidence | `examples/timing/github_actions_timing_evidence.json` |

## Evidence Boundary

This harness shows proof-category parity, not market superiority.

It does not use competitor private data, customer telemetry, production incident records, proprietary benchmarks, or live customer workflows. It does not prove incident reduction, production certification, buyer demand, or willingness to pay.

Its value is that it gives reviewers one concrete way to inspect whether SMERC can produce the same kinds of review artifacts adjacent products commonly use, while adding SMERC's recoverability-specific scores, controls, postures, and lifecycle evidence.
