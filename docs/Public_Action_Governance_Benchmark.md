# Public Action Governance Benchmark

## Purpose

The Public Action Governance Benchmark is a metadata-only scenario set for testing whether SMERC produces useful decisions beyond simple allow/deny controls.

The benchmark is based on public discussion patterns around:

- MCP tool-call governance
- sandboxed coding agents
- cloud administration
- financial runtime actions
- signed execution tickets
- security approval workflows

It does not use private customer data, secrets, production logs, regulated transaction payloads, or proprietary competitor telemetry.

## Why It Exists

External review shows that the AI-agent governance market is already moving toward runtime authorization, sandboxing, tool-call control, traceability, and replay.

That means SMERC must prove a narrower question:

> Does recoverability before execution create a different and useful decision compared with basic allow/deny?

## Input

The seed scenario file is:

```bash
examples/public_action_governance_benchmark.json
```

Each scenario records:

- category
- incident pattern
- traditional allow/deny outcome
- traditional rationale
- action metadata
- recoverability scores
- existing controls
- known failure mode

## Run

Generate the expanded benchmark:

```bash
python -m reference_engine.runtime_benchmark_suite examples/public_action_governance_benchmark.json \
  --json-output reports/public_action_governance_benchmark.json \
  --markdown-output reports/Public_Action_Governance_Benchmark.md \
  --pretty
```

The runtime benchmark expands each seed scenario into deterministic variants:

- baseline
- better evidence
- wider scope
- faster rollback
- weak evidence
- traditional deny

## Output

The report shows:

- decision difference rate versus simple allow/deny
- SMERC posture distribution
- constrained-instead-of-allowed count
- traditional-deny-but-SMERC-non-deny count
- highest irreversible exposure categories
- demo-ready decision differences

## Work / Result / Impact

Work: run realistic public-pattern action metadata through SMERC.

Result: generate a replayable comparison between basic authorization and recoverability-aware pre-execution governance.

Impact: reviewers can see whether SMERC creates useful middle states before a company shares private data or grants execution authority.

## Evidence Boundary

This benchmark supports product review and pilot design.

It does not prove:

- customer demand
- production safety
- incident reduction
- correct enterprise thresholds
- compliance readiness
- acquisition value

The benchmark becomes commercially meaningful only when a design partner replaces or calibrates these scenarios with customer-owned metadata and reviewer labels.
