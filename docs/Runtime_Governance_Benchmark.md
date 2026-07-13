# Runtime Governance Benchmark Suite

The Runtime Governance Benchmark Suite expands seed AI-agent and automation scenarios into deterministic variants, then compares SMERC posture decisions against a simple traditional allow/deny baseline.

The goal is not to fabricate proof. The goal is to make the product testable:

- Which actions does SMERC allow?
- Which actions does SMERC constrain, freeze, deny, or escalate?
- Where does SMERC differ from allow/deny?
- Which categories show the highest irreversible exposure?
- Which examples are useful for design-partner review?

## Example

```bash
python -m reference_engine.runtime_benchmark_suite examples/proxy_incident_replay_scenarios.json --pretty --json-output reports/runtime_governance_benchmark.json --markdown-output reports/Runtime_Governance_Benchmark.md
```

## Evidence Boundary

This benchmark is expanded proxy evidence. It is useful for:

- regression testing
- demo preparation
- design-partner scenario review
- threshold discussion
- product positioning against simple allow/deny policy

It does not prove:

- customer demand
- production incident reduction
- calibrated thresholds for a specific enterprise
- compliance readiness
- security certification

## How Scenarios Are Expanded

Each seed scenario is expanded into deterministic variants:

- baseline
- better evidence
- wider scope
- faster rollback
- weak evidence
- traditional deny

The variant model changes risk, recoverability, evidence validity, impact scope, and traditional policy outcome in a controlled way. The benchmark records the variant in each action context.

## Relationship To Existing Benchmark

`reference_engine.proxy_evidence_benchmark` remains the smaller hand-authored benchmark. `reference_engine.runtime_benchmark_suite` builds on it to create a broader repeatable suite for product review.
